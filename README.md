# NyangLang
> 고양이 울음소리로 작성하는 난해한 프로그래밍 언어 (Esolang)

**NyangLang**은 `냥`, `냐` 등 한국어 고양이 울음소리를 기반으로 설계된 난해한(Esolang) 프로그래밍 언어입니다.
인간이 보기엔 귀엽고 난해하지만, 컴파일러/파서 관점에서는 엄격한 규칙을 갖습니다.

이 프로젝트는 **언어 설계 → 파서 → 인터프리터 → LLVM 컴파일러 백엔드 → CLI → 웹 플레이그라운드**까지의 전체 툴체인을 직접 구현합니다.


## 특징
- 고양이 울음 기반 문법 (`냥`, `냐`, `.`, `~`, `!`, `?`)
- 번호 기반 변수 시스템 (변수1, 변수2, …)
- 스택 기반 연산 모델
- **인터프리터** + **LLVM 네이티브 컴파일러** 이중 백엔드
- CLI (`nyang run` / `nyang build`) 지원
- 웹 플레이그라운드 (FastAPI + Jinja2) 지원
- 인터프리터 대비 **약 1,267배 빠른** LLVM 컴파일 실행


## 프로젝트 구조
```
NyangLang/
├── src/nyang/
│   ├── _00_types.py          # Token, Command, CommandKind 타입 정의
│   ├── _01_lexer.py          # 렉서 (소스 → 토큰)
│   ├── _02_parser.py         # 파서 (토큰 → Command 리스트)
│   ├── _03_interpreter.py    # 인터프리터 (PC 기반 실행)
│   ├── _04_cli.py            # CLI 진입점 (nyang run / nyang build)
│   └── _05_llvm_codegen.py   # LLVM 컴파일러 백엔드 (llvmlite)
│
├── web/
│   ├── app.py                # FastAPI 웹 플레이그라운드
│   ├── templates/index.html  # 플레이그라운드 UI
│   └── static/               # CSS, 이미지
│
├── examples/
│   ├── 00_ex.nyang           # 두 수를 입력받아 합 출력
│   ├── 01_ex.nyang           # 'A' 문자 출력
│   ├── 02_ex.nyang           # 스택/변수 테이블 디버그 출력
│   ├── 03_ex.nyang           # Hello World!
│   ├── 04_ex.nyang           # 홀짝 판별
│   ├── 06_ex.nyang           # 구구단 출력
│   └── bench.nyang           # 100만 루프 벤치마크
│
├── docs/
│   ├── 00_변수 연산자 문법.md
│   ├── 01_사용자 입출력 문법.md
│   ├── 02_점프문.md
│   └── 03_배열.md
│
├── benchmark.py              # 인터프리터 vs LLVM 속도 비교
├── test_all.py               # 전체 자동 테스트 (인터프리터 vs LLVM 출력 비교)
└── pyproject.toml
```


## 실행 방법

### 1. 환경 설정
```bash
python -m venv .venv
source .venv/Scripts/activate   # bash
# 또는 .\.venv\Scripts\activate  # PowerShell

pip install -e .
```

### 2. 인터프리터로 실행
```bash
nyang run examples/00_ex.nyang
```

### 3. LLVM으로 컴파일 후 실행
```bash
nyang build examples/00_ex.nyang   # → 00_ex.exe 생성
./examples/00_ex.exe
```

### 4. 기타 빌드 옵션
```bash
nyang build examples/00_ex.nyang --ir    # LLVM IR 텍스트 출력
nyang build examples/00_ex.nyang --asm   # x86 어셈블리 텍스트 출력
```

### 5. 웹 플레이그라운드
```bash
uvicorn web.app:app --reload
# → http://localhost:8000 에서 실행
```

### 6. 전체 테스트
```bash
python test_all.py
```


## 문법 요약

| 구문 | 형태 | 설명 |
|------|------|------|
| 정수 리터럴 | `....` (점 N개) | 값 N을 스택에 push. `,`는 -1 |
| 변수 선언 | `냥N<값>야옹` | 변수N을 선언하고 초기화 |
| 변수 push | `냥N~야옹` | 변수N 값을 스택에 push |
| 변수 대입 | `냥N~~야옹` | 스택 top을 변수N에 저장 |
| 연산 | `냐냐~야옹` (냐 N개) | N=2:덧셈, 3:뺄셈, 4:곱셈, 5:나눗셈, 6:나머지 |
| 입력 | `냥N??야옹` | 정수를 입력받아 변수N에 저장 |
| 출력 (정수) | `냥N!?야옹` | 변수N을 10진 정수로 출력 |
| 출력 (ASCII) | `냥N!!??야옹` | 변수N을 ASCII 문자로 출력 |
| 점프 | `냥N?<라인>야옹` | 변수N이 0이 아니면 해당 라인으로 점프 |

> 자세한 문법은 `docs/` 폴더의 문서를 참고하세요.


## 예제: 두 수의 합

```
냥??야옹 냥냥??야옹 냥냥냥.,야옹    # 변수1, 2 입력, 변수3 = 0
냥~야옹 냥냥~야옹                   # 변수1, 2를 스택에 push
냐냐~야옹 냥냥냥~~야옹              # 덧셈 → 변수3에 저장
냥냥냥!?야옹                        # 변수3 출력
```

## 예제: Hello World!

```
..........~야옹 .......~야옹
냐냐냐냐~야옹 냥~~야옹 냥~야옹 ..~야옹 냐냐~야옹 냥~~야옹
냥!!??야옹
...
```


## 벤치마크 (100만 루프)

```
$ python benchmark.py

인터프리터:  26.3 초
LLVM exe:     0.021 초
──────────────────────
속도 향상:  1,267 배
```

LLVM 백엔드는 NyangLang 소스를 LLVM IR로 변환 후 네이티브 기계어 `.exe`로 컴파일합니다.
llvmlite를 사용하며, Windows x64 ABI를 준수합니다.


## 아키텍처

```
소스 (.nyang)
    │
    ▼
렉서 (_01_lexer.py)       → Token 리스트
    │
    ▼
파서 (_02_parser.py)      → Command 리스트 (한 라인에 여러 커맨드 가능)
    │
    ├──▶ 인터프리터 (_03_interpreter.py)  → 직접 실행
    │
    └──▶ LLVM 코드젠 (_05_llvm_codegen.py)
              │
              ├── LLVM IR  (--ir)
              ├── x86 ASM  (--asm)
              └── .obj → gcc 링킹 → .exe
```


## 문서

1. [변수·연산자 문법](./docs/00_변수%20연산자%20문법.md)
2. [사용자 입출력 문법](./docs/01_사용자%20입출력%20문법.md)
3. [점프문 문법](./docs/02_점프문.md)
4. [배열 문법](./docs/03_배열.md)
