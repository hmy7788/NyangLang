import subprocess
import time
import sys
import os

NYANG_FILE = "examples/bench.nyang"
EXE_FILE   = r"examples\bench.exe"
PYTHON     = sys.executable
VENV_NYANG = r".venv\Scripts\nyang.exe"

def measure(label, cmd, runs=3):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        subprocess.run(cmd, capture_output=True)
        times.append(time.perf_counter() - t0)
    avg = sum(times) / len(times)
    print(f"  {label:20s}: {avg:.3f}초  (평균 {runs}회)")
    return avg

def main():
    print("=" * 50)
    print("NyangLang 벤치마크: 인터프리터 vs LLVM 컴파일")
    print("=" * 50)
    print(f"파일: {NYANG_FILE}")
    print()

    # 1. 빌드
    print("[빌드 중...]")
    r = subprocess.run([VENV_NYANG, "build", NYANG_FILE], capture_output=True, text=True)
    if r.returncode != 0:
        print("빌드 실패:", r.stderr)
        return
    print(f"  빌드 완료: {EXE_FILE}")
    print()

    # 2. 측정
    print("[실행 시간 측정]")
    t_interp  = measure("인터프리터 (Python)", [VENV_NYANG, "run", NYANG_FILE])
    t_compile = measure("LLVM 컴파일 exe",    [EXE_FILE])

    # 3. 결과
    print()
    print("=" * 50)
    print("결과")
    print("=" * 50)
    print(f"  인터프리터:    {t_interp:.3f}초")
    print(f"  LLVM 컴파일:   {t_compile:.3f}초")
    speedup = t_interp / t_compile if t_compile > 0 else float("inf")
    print(f"  속도 향상:     {speedup:.1f}배 빠름")
    print()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
