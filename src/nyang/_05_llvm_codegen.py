from __future__ import annotations

from llvmlite import ir, binding

from nyang._00_types import Command, CommandKind
from nyang._01_lexer import lex_line
from nyang._02_parser import parse_line


binding.initialize_native_target()
binding.initialize_native_asmprinter()

i32 = ir.IntType(32)
i64 = ir.IntType(64)
i8  = ir.IntType(8)
i1  = ir.IntType(1)


class LLVMCodeGen:
    def __init__(self):
        self.module = ir.Module(name="nyang_program")
        self.module.triple = binding.get_default_triple()

        self.builder: ir.IRBuilder | None = None
        self.main_fn: ir.Function | None = None

        self.variables: dict[int, ir.AllocaInstr] = {}  # nyang_id → alloca
        self.stack_arr: ir.AllocaInstr | None = None     # int stack[256]
        self.stack_sp: ir.AllocaInstr | None = None      # 스택 포인터

        self.printf_fn: ir.Function | None = None
        self.scanf_fn: ir.Function | None = None
        self._fmt_cache: dict[str, ir.GlobalVariable] = {}

        self._declare_printf()
        self._declare_scanf()
        self._setup_main()

    # ── 외부 함수 선언 ────────────────────────────────────────────────────

    def _declare_printf(self) -> None:
        ty = ir.FunctionType(i32, [i8.as_pointer()], var_arg=True)
        self.printf_fn = ir.Function(self.module, ty, name="printf")

    def _declare_scanf(self) -> None:
        ty = ir.FunctionType(i32, [i8.as_pointer()], var_arg=True)
        self.scanf_fn = ir.Function(self.module, ty, name="scanf")

    # ── main 함수 + entry 블록 ────────────────────────────────────────────

    def _setup_main(self) -> None:
        fn_ty = ir.FunctionType(i32, [])
        self.main_fn = ir.Function(self.module, fn_ty, name="main")
        entry = self.main_fn.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)

        self.stack_arr = self.builder.alloca(ir.ArrayType(i32, 256), name="stack")
        self.stack_sp  = self.builder.alloca(i32, name="sp")
        self.builder.store(ir.Constant(i32, 0), self.stack_sp)

    # ── 포맷 문자열 헬퍼 ─────────────────────────────────────────────────

    def _fmt_ptr(self, text: str) -> ir.Value:
        if text not in self._fmt_cache:
            encoded = bytearray((text + "\0").encode("utf-8"))
            arr_ty  = ir.ArrayType(i8, len(encoded))
            gv = ir.GlobalVariable(self.module, arr_ty, name=f"fmt_{len(self._fmt_cache)}")
            gv.global_constant = True
            gv.initializer = ir.Constant(arr_ty, list(encoded))
            self._fmt_cache[text] = gv
        zero = ir.Constant(i64, 0)
        return self.builder.gep(self._fmt_cache[text], [zero, zero], name="fmtptr")

    # ── 스택 헬퍼 ────────────────────────────────────────────────────────

    def _stack_push(self, val: ir.Value) -> None:
        sp   = self.builder.load(self.stack_sp, name="sp")
        sp64 = self.builder.sext(sp, i64, name="sp64")
        ptr  = self.builder.gep(self.stack_arr, [ir.Constant(i64, 0), sp64], name="slot")
        self.builder.store(val, ptr)
        new_sp = self.builder.add(sp, ir.Constant(i32, 1), name="sp_inc")
        self.builder.store(new_sp, self.stack_sp)

    def _stack_pop(self, name: str = "pop") -> ir.Value:
        sp     = self.builder.load(self.stack_sp, name="sp")
        new_sp = self.builder.sub(sp, ir.Constant(i32, 1), name="sp_dec")
        self.builder.store(new_sp, self.stack_sp)
        sp64 = self.builder.sext(new_sp, i64, name="sp64")
        ptr  = self.builder.gep(self.stack_arr, [ir.Constant(i64, 0), sp64], name="slot")
        return self.builder.load(ptr, name=name)

    # ── 변수 헬퍼 ────────────────────────────────────────────────────────

    def _get_var(self, nyang_id: int) -> ir.AllocaInstr:
        return self.variables[nyang_id]

    def _pre_alloc_vars(self, all_commands: list[list[Command]]) -> None:
        """모든 커맨드를 미리 스캔해서 사용되는 변수를 entry 블록에 alloca"""
        used_ids: set[int] = set()
        for cmds in all_commands:
            for cmd in cmds:
                if cmd.nyang_id is not None:
                    used_ids.add(cmd.nyang_id)
                if cmd.jump_kind in ("int?nyang", "nyang?nyang") and cmd.jump_line is not None:
                    used_ids.add(cmd.jump_line)
                if cmd.jump_kind in ("nyang?int", "nyang?nyang") and cmd.condition is not None:
                    used_ids.add(cmd.condition)
        for nyang_id in sorted(used_ids):
            self.variables[nyang_id] = self.builder.alloca(i32, name=f"var{nyang_id}")

    # ── 개별 명령 IR 생성 ─────────────────────────────────────────────────

    def _emit_var_decl(self, cmd: Command) -> None:
        self.builder.store(ir.Constant(i32, cmd.int_value), self._get_var(cmd.nyang_id))

    def _emit_value_push(self, cmd: Command) -> None:
        self._stack_push(ir.Constant(i32, cmd.int_value))

    def _emit_var_push(self, cmd: Command) -> None:
        val = self.builder.load(self._get_var(cmd.nyang_id), name=f"var{cmd.nyang_id}_val")
        self._stack_push(val)

    def _emit_var_assign(self, cmd: Command) -> None:
        val = self._stack_pop(name="assign_val")
        self.builder.store(val, self._get_var(cmd.nyang_id))

    def _emit_operation(self, cmd: Command) -> None:
        b = self._stack_pop("b")
        a = self._stack_pop("a")
        op = cmd.op_arity
        if   op == 2: result = self.builder.add(a, b, name="add")
        elif op == 3: result = self.builder.sub(a, b, name="sub")
        elif op == 4: result = self.builder.mul(a, b, name="mul")
        elif op == 5: result = self.builder.sdiv(a, b, name="div")
        elif op == 6: result = self.builder.srem(a, b, name="mod")
        else: return
        self._stack_push(result)

    def _emit_input(self, cmd: Command) -> None:
        fmt = self._fmt_ptr("%d")
        self.builder.call(self.scanf_fn, [fmt, self._get_var(cmd.nyang_id)])

    def _emit_output(self, cmd: Command) -> None:
        if cmd.output_kind == "int":
            val = ir.Constant(i32, cmd.int_value)
        else:
            val = self.builder.load(self._get_var(cmd.nyang_id), name="out_val")

        spec   = "%c" if cmd.output_form == "ascii" else "%d"
        suffix = {"newline": "\n", "inline": "", "space": " "}.get(cmd.output_mode, "\n")
        self.builder.call(self.printf_fn, [self._fmt_ptr(spec + suffix), val])

    def _emit_jump(
        self,
        cmd: Command,
        line_idx: int,
        line_blocks: list[ir.Block],
        exit_block: ir.Block,
    ) -> None:
        n = len(line_blocks)

        # ── 조건값 ──────────────────────────────────────────────────────
        if cmd.jump_kind in ("int?int", "int?nyang"):
            cond_val: ir.Value = ir.Constant(i32, cmd.condition)
        else:  # nyang?int, nyang?nyang
            cond_val = self.builder.load(self._get_var(cmd.condition), name="cond")

        # ── 목적지 블록 ──────────────────────────────────────────────────
        if cmd.jump_kind in ("int?int", "nyang?int"):
            # 정적 목적지
            tgt_idx = cmd.jump_line - 1  # 1-indexed → 0-indexed
            target_block = line_blocks[tgt_idx] if 0 <= tgt_idx < n else exit_block
            next_block   = line_blocks[line_idx + 1] if line_idx + 1 < n else exit_block

            if isinstance(cond_val, ir.Constant):
                # 조건도 상수 → 컴파일 타임 분기
                self.builder.branch(target_block if cond_val.constant != 0 else next_block)
            else:
                cond_bool = self.builder.icmp_signed("!=", cond_val, ir.Constant(i32, 0), name="cond_bool")
                self.builder.cbranch(cond_bool, target_block, next_block)

        else:
            # 동적 목적지 (변수에 저장된 라인 번호)
            tgt_line_val = self.builder.load(self._get_var(cmd.jump_line), name="jump_line")
            next_block   = line_blocks[line_idx + 1] if line_idx + 1 < n else exit_block

            # condition 체크: 0이면 무조건 fall-through
            cond_bool = self.builder.icmp_signed("!=", cond_val, ir.Constant(i32, 0), name="cond_bool")
            jump_block = self.main_fn.append_basic_block(f"dyn_jump_{line_idx}")
            self.builder.cbranch(cond_bool, jump_block, next_block)

            # 동적 목적지: switch로 1..n → 각 블록
            self.builder.position_at_end(jump_block)
            sw = self.builder.switch(tgt_line_val, exit_block)
            for idx, blk in enumerate(line_blocks):
                sw.add_case(ir.Constant(i32, idx + 1), blk)  # 라인 번호는 1-indexed

    def _emit(self, cmd: Command) -> None:
        dispatch = {
            CommandKind.VAR_DECL:   self._emit_var_decl,
            CommandKind.VALUE_PUSH: self._emit_value_push,
            CommandKind.VAR_PUSH:   self._emit_var_push,
            CommandKind.VAR_ASSIGN: self._emit_var_assign,
            CommandKind.OPERATION:  self._emit_operation,
            CommandKind.INPUT:      self._emit_input,
            CommandKind.OUTPUT:     self._emit_output,
        }
        handler = dispatch.get(cmd.kind)
        if handler:
            handler(cmd)

    # ── 컴파일 진입점 ────────────────────────────────────────────────────

    def compile_lines(self, lines: list[str]) -> None:
        # Pass 1: 전체 파싱
        all_commands: list[list[Command]] = []
        for line in lines:
            tokens = lex_line(line)
            all_commands.append(parse_line(tokens))

        n = len(all_commands)

        # entry 블록: 변수 pre-alloc
        self._pre_alloc_vars(all_commands)

        # 라인별 basic block + exit block 생성
        line_blocks = [self.main_fn.append_basic_block(f"line_{i}") for i in range(n)]
        exit_block  = self.main_fn.append_basic_block("exit")

        # entry → line_0 (또는 exit)
        self.builder.branch(line_blocks[0] if n > 0 else exit_block)

        # Pass 2: 각 라인 블록 채우기
        for i, cmds in enumerate(all_commands):
            self.builder.position_at_end(line_blocks[i])

            jumped = False
            for cmd in cmds:
                if cmd.kind == CommandKind.JUMP:
                    self._emit_jump(cmd, i, line_blocks, exit_block)
                    jumped = True
                    break
                self._emit(cmd)

            if not jumped:
                next_block = line_blocks[i + 1] if i + 1 < n else exit_block
                self.builder.branch(next_block)

        # exit 블록: return 0
        self.builder.position_at_end(exit_block)
        self.builder.ret(ir.Constant(i32, 0))

    # ── 결과 출력 ────────────────────────────────────────────────────────

    def emit_ir(self) -> str:
        return str(self.module)

    def _get_machine(self):
        target  = binding.Target.from_default_triple()
        machine = target.create_target_machine()
        self.module.data_layout = machine.target_data
        return machine, binding.parse_assembly(str(self.module))

    def emit_asm(self) -> str:
        machine, mod = self._get_machine()
        mod.verify()
        return machine.emit_assembly(mod)

    def emit_object(self) -> bytes:
        machine, mod = self._get_machine()
        mod.verify()
        return machine.emit_object(mod)
