import argparse
from nyang.interpreter import Interpreter

def run_file(path: str) -> None:
    interp = Interpreter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            interp.exec_line(line)

def repl() -> None:
    interp = Interpreter()
    while True:
        try:
            line = input("nyang> ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if not line.strip():
            continue
        if line.strip() in {"exit", "quit"}:
            break
        interp.exec_line(line)

def main() -> None:
    parser = argparse.ArgumentParser(prog="nyang")
    parser.add_argument("file", nargs="?", help=".nyang 파일 경로(없으면 REPL)")
    args = parser.parse_args()

    if args.file:
        run_file(args.file)
    else:
        repl()

if __name__ == "__main__":
    main()