
from __future__ import annotations
from typing import TYPE_CHECKING
from .parser import Command

if TYPE_CHECKING:
    from .interpreter import Interpreter

class CommandExecMixin:
    """
    Interpreter에서 사용하는 개별 명령 실행 로직을 모은 믹스인 클래스
    Interpreter가 이 클래스를 상속받아 self._exec_*를 그대로 사용
    """

    # 변수 선언 & 초기화: <냥 N개><. , M개>
    def _exec_var_decl(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        value = cmd.int_value
        self.variables_table[var_id] = value


    # 정수형 push: <. , M개>~
    def _exec_value_push(self: "Interpreter", cmd: Command) -> None:
        value = cmd.int_value
        self.stack.append(value)
        self.last_result = value


    # 변수형 push / 대입: <냥 N개>~
    def _exec_var_push_or_access(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id

        # 변수에 last_result 값 대입
        if self.last_was_operation:
            if not self.stack:
                raise RuntimeError("스택이 비어있는데 대입을 시도했습니다.")
            self.variables_table[var_id] = self.stack.pop()

            if len(self.stack) == 0:
                self.last_result = None
            else:
                self.last_result = self.stack[-1]
                
            self.last_was_operation = False

        # 변수값 push
        else:
            int_value = self.variables_table[var_id]
            self.stack.append(int_value)
            self.last_result = int_value


    # 연산: <냐 N개>~
    def _exec_operation(self: "Interpreter", cmd: Command) -> None:
        if len(self.stack) < 2:
            raise RuntimeError("연산을 수행하기 위한 스택 값이 부족합니다.")
        b = self.stack.pop()
        a = self.stack.pop()
        op = cmd.op_arity

        if op == 2:
            result = a + b
        elif op == 3:
            result = a - b
        elif op == 4:
            result = a * b
        elif op == 5:
            if b == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다.")
            result = a // b
        else:
            raise RuntimeError("지원하지 않는 연산입니다.")
        
        self.stack.append(result)
        self.last_result = result
        self.last_was_operation = True


    # 입력: <냥 N개>?
    def _exec_input(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            raw = input(f"변수{var_id} 입력 > ")
            value = int(raw.rstrip())
        except ValueError:
            raise ValueError("정수만 입력할 수 있습니다.")
        self.variables_table[var_id] = value

    
    # 출력: <숫자형/변수형?<!/!!><?/??/???>
    def _exec_output(self: "Interpreter", cmd: Command) -> None:
        # 출력 종류
        if cmd.output_kind == "int":
            value = cmd.int_value
        elif cmd.output_kind == "nyang":
            try:
                var_id = cmd.nyang_id
                value = self.variables_table[var_id]
            except KeyError:
                raise KeyError(f"변수{var_id}가 정의되지 않았습니다.")
        else:
            raise RuntimeError("알 수 없는 output_kind")
        
        # 출력 형식
        if cmd.output_form == "decimal":
            out = value
        elif cmd.output_form == "ascii":
            try:
                out = chr(value)
            except ValueError:
                raise ValueError("ASCII 범위를 벗어난 값입니다.")
        else:
            raise RuntimeError("알 수 없는 output_form")
        
        # 출력 모드
        if cmd.output_mode == "newline":
            end = "\n"
        elif cmd.output_mode == "inline":
            end = ""
        elif cmd.output_mode == "space":
            end = " "
        else:
            raise RuntimeError("알 수 없는 output_mode")
        
        # 
        self.write(out, end=end)



    # 출력: 냐! -> 현재 스택 출력
    def _exec_display_stack(self: "Interpreter") -> None:
        self.write()
        if self.stack:
            self.write("===============")
            for i in range(len(self.stack)-1, -1, -1):
                if i == len(self.stack)-1:
                    self.write(f'=      {self.stack[i]}      = <- Top')
                else:
                    self.write(f'=      {self.stack[i]}      =')
            self.write("==[현재 스택]==")
        else:
            self.write("====================")
            self.write("스택이 비어있습니다.")
            self.write("====================")



    # 출력: 냐!! -> 현재 변수 테이블 출력
    def _exec_display_variable_table(self: "Interpreter") -> None:
        vt = self.variables_table
        self.write()
        if vt:
            self.write("--[변수 테이블]--")
            for k, v in vt.items():
                self.write(f'- 변수{k} = {v}    -')
            self.write("-----------------")
        else:
            self.write("===========================")
            self.write("변수 테이블이 비어있습니다.")
            self.write("===========================")


    # 점프문: <숫자형/변수형>?<숫자형/변수형>
    def _exec_jump(self: "Interpreter", cmd: Command, pc: int):
        jump_kind = cmd.jump_kind

        # 점프문1: <숫자형>?<숫자형>
        if jump_kind == 'int?int':
            condition = cmd.condition
            line = cmd.jump_line

        # 점프문2: <숫자형>?<변수형>
        elif jump_kind == 'int?nyang':
            condition = cmd.condition
            try:
                line = self.variables_table[cmd.jump_line]
            except KeyError:
                raise KeyError(f"변수{cmd.jump_line}은 정의되지 않았습니다.")

        # 점프문3: <변수형>?<숫자형>
        elif jump_kind == 'nyang?int':
            try:
                condition = self.variables_table[cmd.condition]
            except KeyError:
                raise KeyError(f"변수{cmd.condition}은 정의되지 않았습니다.")
            line = cmd.jump_line
        
        # 점프문4: <변수형>?<변수형>
        elif jump_kind == 'nyang?nyang':
            try:
                condition = self.variables_table[cmd.condition]
                line = self.variables_table[cmd.jump_line]
            except KeyError:
                raise KeyError(f"변수{cmd.condition} 또는 변수{cmd.jump_line}은 정의되지 않았습니다.")
        
        if condition != 0:
            if line <= 0:
                raise RuntimeError(f"잘못된 점프 라인 {line}")
            return line-1
        else:
            return pc+1
        

    def _exec_array_decl(self: "Interpreter", cmd: Command):
        array_id = cmd.array_id

        if cmd.array_decl_mode == 0:
            array_length = cmd.array_length

        elif cmd.array_decl_mode == 1:
            try:
                array_length = self.variables_table[cmd.array_length]
            except KeyError:
                KeyError(f"변수{cmd.array_length}가 정의되지 않았습니다.")
        else:
            raise 

        array = [0 for _ in range(array_length)]
        self.array_table[array_id] = array

    def _exec_array_write(self: "Interpreter", cmd: Command):
        array_id = cmd.array_id

        try:
            array = self.array_table[array_id]
        except KeyError:
            raise KeyError(f"배열{array_id}가 정의되지 않았습니다.")

        if cmd.array_write_mode == 0:
            array_idx = cmd.array_idx
            value = cmd.int_value

        elif cmd.array_write_mode == 1:
            array_idx = cmd.array_idx
            try:
                value = self.variables_table[cmd.int_value]
            except KeyError:
                raise KeyError(f"변수{cmd.int_value}")
            
            try:
                pass
            except:
                pass
                



        elif cmd.array_write_mode == 2:
            pass

        elif cmd.array_write_mode == 3:
            pass

        else:
            raise

    def _exec_array_read(self: "Interpreter", cmd: Command):
        pass