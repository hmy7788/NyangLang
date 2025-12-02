# NyangLang
> 고양이 울음소리로 작성하는 난해한 한국어 기반 프로그래밍 언어 (Esolang)

**NyangLang**은 `냥`, `냐`등을 기반으로 구성된 난해한(Esolang) 프로그래밍 언어입니다. 인간이 보기엔 귀엽고 난해하지만, 컴파일러/파서 관점에서는 엄격한 규칙을 갖도록 설계되었습니다. <br>
이 프로젝트는 프로그래밍 언어 설계, 파서 구현, 인터프리터 개발, CLI 및 웹 플레이그라운드 구축까지를 목표로 합니다.


# 특징
- 고양이 울음 기반 문법 (`냥`, `냐`)
- 번호 기반 변수/함수/배열 시스템
- 직접 구현한 인터프리터 구조
- CLI 실행 지원
- 웹 플레이그라운드 지원


# 목표
- NyangLang 문법 정립 및 문서화
- 인터프리터(또는 컴파일러) 코어 구현
- 터미널 명령어로 실행 가능한 CLI 제작
- 웹 브라우저 기반 실행 환경 구축
- 도전학기제 최종 보고서 및 데모 시연


# 프로젝트 구조
```
NyangLang/
    ┣ __pycache__/
    ┃
    ┣ .venv/
    ┃
    ┣ cli/
    ┃  ┣ nyanglang.egg-info/
    ┃  ┗ setup.py
    ┃
    ┣ docs/
    ┃  ┣ 00_변수 연산자 문법.md
    ┃  ┣ 01_사용자 입출력 문법.md
    ┃  ┗ 02_점프문.md
    ┃
    ┣ examples/
    ┃   ┣ 00_ex.nyang
    ┃   ┣ 01_ex.nyang
    ┃   ┣ 02_ex.nyang
    ┃   ┗ 03_ex.nyang
    ┃
    ┣ scripts/
    ┃
    ┣ src/
    ┃   ┣ __pycache__/
    ┃   ┣ nyang/
    ┃   ┃   ┣ __pycache__/
    ┃   ┃   ┣ __init__.py
    ┃   ┃   ┣ ast.py
    ┃   ┃   ┣ cli.py
    ┃   ┃   ┣ cmd.py
    ┃   ┃   ┣ interpreter.py
    ┃   ┃   ┣ lexer.py
    ┃   ┃   ┗ parser.py
    ┃   ┗ nyanglang.egg-info/
    ┃
    ┣ web/
    ┃  ┗ app.py
    ┃
    ┣ pyproject.toml
    ┣ README.md
    ┣ requirements.txt
    ┗ test.nyang
```


# 문법 보러가기
1. [정수,변수, 연산자 문법](./docs/00_변수%20연산자%20문법.md)
2. [사용자 입출력 문법](./docs/01_사용자%20입출력%20문법.md)
3. [점프문 문법](./docs/02_점프문.md)


# 실행방법
1. 가상환경 생성/활성화
```bash
python -m venv .venv
.\.venv\Scripts\activate    # PowerShell
```

2. 패키지 설치
```
pip install -e .
```

3. 예제 실행
```
nyang example/simple.nyang
```

- 설치 후 `nyang --help`로 옵션을 확인할 수 있습니다.