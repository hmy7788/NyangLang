"""
인터프리터 vs LLVM 전체 테스트
- 05_ex.nyang 제외
- 입력이 필요한 파일은 미리 정의된 stdin 사용
- 두 결과가 일치하면 PASS

비교 시 인터프리터의 입력 프롬프트("변수N 입력 > ")는 제거 후 비교
(LLVM은 scanf를 쓰므로 프롬프트를 출력하지 않음 — 정상 동작)
"""
import subprocess
import re
import os

VENV_NYANG = r".venv\Scripts\nyang.exe"
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"

# (파일, stdin, llvm_지원여부)
TEST_CASES = [
    ("examples/00_ex.nyang", "3\n7\n",  True),   # 두 수 입력 → 합 출력
    ("examples/01_ex.nyang", "",        True),    # 입력 없음 → 'A' 출력
    ("examples/02_ex.nyang", "",        False),   # DISPLAY_STACK 미구현 → SKIP
    ("examples/03_ex.nyang", "",        True),    # 입력 없음 → Hello World!
    ("examples/04_ex.nyang", "7\n",     True),    # 홀수 입력 → 홀짝 판별
    ("examples/06_ex.nyang", "3\n",     True),    # 단 입력 → 구구단
    ("examples/bench.nyang", "",        True),    # 입력 없음 → 순수 계산
]

_PROMPT_RE = re.compile(r"변수\d+ 입력 > ")


def run(cmd, stdin_data=""):
    r = subprocess.run(
        cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return r.stdout.strip()


def strip_prompts(text: str) -> str:
    """인터프리터의 입력 프롬프트 제거"""
    return _PROMPT_RE.sub("", text).strip()


def main():
    print("=" * 60)
    print("NyangLang 전체 테스트: 인터프리터 vs LLVM")
    print("=" * 60)

    passed = failed = skipped = 0

    for nyang_file, stdin, llvm_ok in TEST_CASES:
        name = os.path.basename(nyang_file)
        exe  = nyang_file.replace(".nyang", ".exe").replace("/", "\\")
        print(f"\n[{name}]  stdin={repr(stdin.strip()) if stdin else '(없음)'}")

        # 1. 인터프리터 실행
        out_interp_raw = run([VENV_NYANG, "run", nyang_file], stdin)
        out_interp = strip_prompts(out_interp_raw)
        print(f"  인터프리터: {repr(out_interp)}")

        # 2. LLVM 미지원 파일 → SKIP
        if not llvm_ok:
            print(f"  LLVM      : (DISPLAY_* 미구현으로 건너뜀)")
            print(f"  결과: {SKIP}")
            skipped += 1
            continue

        # 3. LLVM 빌드
        build = subprocess.run(
            [VENV_NYANG, "build", nyang_file],
            capture_output=True, text=True
        )
        if build.returncode != 0:
            print(f"  빌드 실패: {build.stderr.strip()}")
            print(f"  결과: {FAIL}")
            failed += 1
            continue

        # 4. LLVM exe 실행
        r = subprocess.run(
            [exe], input=stdin,
            capture_output=True, encoding="ascii", errors="replace",
        )
        out_llvm = r.stdout.strip()
        print(f"  LLVM      : {repr(out_llvm)}")

        # 5. 비교
        if out_interp == out_llvm:
            print(f"  결과: {PASS}")
            passed += 1
        else:
            print(f"  결과: {FAIL}  ← 출력 불일치")
            failed += 1

    print("\n" + "=" * 60)
    print(f"PASS {passed}  /  FAIL {failed}  /  SKIP {skipped}")
    if failed == 0:
        print(f"전체 결과: {PASS}")
    else:
        print(f"전체 결과: {FAIL}")
    print("=" * 60)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
