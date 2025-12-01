import argparse
from nyang.interpreter import Interpreter


def run_file(path: str) -> None:
    interp = Interpreter()
    pc = 0
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
        interp.run_program(lines)


def main() -> None:
    parser = argparse.ArgumentParser(prog="nyang")
    parser.add_argument("file", nargs="?", help=".nyang 파일 경로(없으면 REPL)")
    args = parser.parse_args()

    if args.file:
        run_file(args.file)


if __name__ == "__main__":
    main()