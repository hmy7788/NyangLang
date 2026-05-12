# import ========================================
import argparse
import subprocess
import sys
from pathlib import Path

from nyang._03_interpreter import Interpreter
from nyang._05_llvm_codegen import LLVMCodeGen
# import ========================================


def run_file(path: str) -> None:
    interp = Interpreter()
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    interp.run_program(lines)


def build_file(path: str, emit_ir: bool = False, emit_asm: bool = False) -> None:
    src = Path(path)
    with open(src, encoding="utf-8") as f:
        lines = f.readlines()

    codegen = LLVMCodeGen()
    codegen.compile_lines(lines)

    if emit_ir:
        print(codegen.emit_ir())
        return

    if emit_asm:
        print(codegen.emit_asm())
        return

    obj_path = src.with_suffix(".o")
    obj_path.write_bytes(codegen.emit_object())

    out_path = src.with_suffix(".exe" if sys.platform == "win32" else "")
    result = subprocess.run(
        ["gcc", str(obj_path), "-o", str(out_path)],
        capture_output=True, text=True
    )

    obj_path.unlink(missing_ok=True)

    if result.returncode != 0:
        print("링킹 실패:", result.stderr, file=sys.stderr)
        sys.exit(1)

    print(f"빌드 완료: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="nyang")
    subparsers = parser.add_subparsers(dest="command")

    # nyang run <file>
    run_p = subparsers.add_parser("run", help=".nyang 파일 인터프리터 실행")
    run_p.add_argument("file", help=".nyang 파일 경로")

    # nyang build <file>
    build_p = subparsers.add_parser("build", help=".nyang 파일 컴파일 (LLVM)")
    build_p.add_argument("file", help=".nyang 파일 경로")
    build_p.add_argument("--ir",  action="store_true", help="LLVM IR 텍스트 출력")
    build_p.add_argument("--asm", action="store_true", help="x86 어셈블리 텍스트 출력")

    args, remaining = parser.parse_known_args()

    if args.command == "run":
        run_file(args.file)
    elif args.command == "build":
        build_file(args.file, emit_ir=args.ir, emit_asm=args.asm)
    elif remaining:
        # 하위 호환: nyang <file> → run으로 동작
        run_file(remaining[0])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
