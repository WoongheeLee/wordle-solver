# Wordle Solver

Wordle 게임 풀이를 위한 단어 추천 솔버 웹 애플리케이션입니다. 사용자가 입력한 Wordle 게임 결과(녹색, 노란색, 회색)를 바탕으로 다음 시도에 사용할 최적의 단어를 추천합니다.

## 주요 기능

- **실시간 단어 추천**: Wordle 게임 결과를 입력하면 조건에 맞는 후보 단어들을 실시간으로 추천
- **다중 전략 지원**: 랜덤 추천 또는 빈도 기반 추천 전략 선택 가능
- **동적 사전 관리**: 여러 사전 파일을 동적으로 로드하고 전환 가능
- **사용자 단어 추가**: 새로 발견한 단어를 사용자 사전에 추가하여 향후 추천에 포함
- **직관적인 UI**: Wordle 게임과 유사한 색상 피드백 시스템으로 쉬운 사용
- **시도 기록 관리**: 이전 시도로 되돌아가기 기능으로 실수 수정 가능

## 프로젝트 구조

```
wordle-solver/
├── app/
│   └── main.py              # FastAPI 웹 서버 메인 애플리케이션
├── py/
│   └── solver.py            # Wordle 솔버 로직 클래스
├── frontend/
│   └── index.html           # 웹 UI (HTML, CSS, JavaScript)
├── dictionary/              # 단어 사전 파일들
│   ├── full_vocabs.txt      # 전체 단어 사전
│   ├── unique.txt           # 고유 문자 기반 초기 추천 단어
│   ├── 5_letter_words.txt   # 5글자 단어 사전
│   ├── user_words.txt       # 사용자 추가 단어
│   └── wordle-La.txt        # 추가 단어 사전
├── requirements.txt         # Python 의존성 패키지 목록
└── README.md               # 프로젝트 설명서
```

## 설치 및 실행

### 필수 요구사항
- Python 3.7+
- pip (Python 패키지 관리자)

### 설치
1. 리포지토리를 클론하거나 다운로드합니다.
2. 가상환경을 생성하고 활성화합니다 (권장):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   venv\Scripts\activate     # Windows
   ```
3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

### 실행
1. app 디렉토리로 이동합니다:
   ```bash
   cd app
   ```
2. 서버를 시작합니다:
   ```bash
   python main.py
   ```
   
   추가 옵션:
   ```bash
   # 추천 전략 변경 (random 또는 freq)
   python main.py --strategy freq
   
   # 사전 파일 경로 지정
   python main.py --vocab ../dictionary/custom_vocab.txt --unique ../dictionary/custom_unique.txt
   ```

3. 웹 브라우저에서 `http://localhost:8000`에 접속합니다.

## 사용 방법

### 기본 사용법
1. 웹 인터페이스에서 5글자 영어 단어를 입력합니다.
2. 각 글자를 클릭하여 Wordle 게임 결과에 따라 색상을 설정합니다:
   - **회색**: 해당 글자가 정답에 없음
   - **노란색**: 해당 글자가 정답에 있지만 위치가 틀림
   - **녹색**: 해당 글자가 정답에 있고 위치도 맞음
3. Enter 키를 누르거나 제출하여 다음 추천 단어를 받습니다.
4. 추천된 단어 중 하나를 클릭하면 자동으로 입력됩니다.

### 고급 기능
- **이전 시도로 되돌아가기**: 실수했을 때 이전 단계로 돌아가 수정 가능
- **사용자 단어 추가**: 정답을 맞췄을 때 해당 단어를 사용자 사전에 추가 가능
- **페이지네이션**: 많은 추천 단어가 있을 때 페이지별로 탐색 가능

## API 엔드포인트

### 주요 엔드포인트
- `GET /`: 메인 웹 인터페이스
- `POST /submit`: 게임 결과 제출 및 추천 단어 요청
- `GET /config/dictionaries`: 사용 가능한 사전 파일 목록 조회
- `POST /config/dictionary`: 사전 설정 변경
- `POST /add_word`: 사용자 단어를 사전에 추가

### 요청/응답 예시
```python
# POST /submit
{
    "text": "AUDIO",
    "clicks": ["1", "2", "3", "1", "2"]  # 각 글자별 색상 상태
}

# 응답
{
    "suggestions": ["CREAM", "BREAD", "GREAT"],
    "word_nums": 127,
    "no_results": false
}
```

## 핵심 알고리즘

### WordleSolver 클래스
- **필터링 시스템**: 사용자 입력에 따라 단계별로 후보 단어를 필터링
- **빈도 기반 추천**: 문자별 빈도와 위치별 빈도를 고려한 스코어링 시스템
- **동적 사전 로딩**: 다양한 사전 파일을 자동으로 병합하여 포괄적인 단어 데이터베이스 구축

### 주요 필터링 단계
1. **제외 문자 필터**: 회색으로 표시된 문자가 포함된 단어 제거
2. **정확한 위치 매칭**: 녹색으로 표시된 문자가 해당 위치에 있는 단어만 선택
3. **잘못된 위치 필터**: 노란색으로 표시된 문자가 포함되되 해당 위치에는 없는 단어 선택

## 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 프레임워크
- **Python**: 핵심 로직 구현
- **Uvicorn**: ASGI 서버

### 프론트엔드
- **HTML5**: 구조
- **CSS3**: 스타일링 (Wordle 스타일의 색상 시스템)
- **JavaScript**: 동적 상호작용 및 AJAX 통신

### 데이터
- **텍스트 파일**: 단어 사전 저장
- **정규표현식**: 단어 패턴 매칭
- **집합 연산**: 효율적인 단어 필터링

## 설정 옵션

### 환경 변수
- `WS_STRATEGY`: 추천 전략 (`random` 또는 `freq`)
- `WS_VOCAB`: 전체 단어 사전 경로
- `WS_UNIQUE`: 초기 추천용 고유 문자 사전 경로

### 명령행 인수
- `--strategy`: 추천 전략 선택
- `--vocab`: 전체 후보 사전 경로
- `--unique`: 초기 추천용 사전 경로

## 참고 링크

### Wordle 게임 사이트
- [뉴욕 타임즈 Wordle](https://www.nytimes.com/games/wordle/index.html) - 공식 일일 Wordle
- [Wordly](https://wordly.org/) - 무제한 Wordle 게임

## 개발자 정보

이 프로젝트는 Wordle 게임의 전략적 접근을 위해 개발된 도구입니다. 단어 빈도 분석과 조건부 필터링을 통해 최적의 추천을 제공합니다.