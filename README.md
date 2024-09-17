# Wordle 풀이기

Wordle 게임을 위한 추천 단어 목록을 제공하는 어플리케이션입니다.

## 사용법
### 환경 설정
* 가상 환경 사용을 권장합니다. 아래 명령어를 실행하여 필요한 패키지를 설치하세요:
    ```
    pip install -r requirements.txt
    ```

### 어플리케이션 실행
1. 프로젝트 디렉토리로 이동한 후 `app` 폴더로 이동합니다:
    ```
    cd app
    ```
2. 다음 명령어를 실행하여 서버를 시작합니다:
    ```
    python main.py
    ```
3. 브라우저에서 `localhost:8000`에 접속하여 Wordle 풀이기를 사용하세요.

### 게임 방법
1. 5글자의 영어 단어를 입력하세요.
2. 각 글자를 마우스로 클릭하면 색상이 회색, 노란색, 녹색 순서로 변경됩니다.
3. 색상을 선택한 후 엔터를 누르면 추천 단어 목록이 갱신됩니다.

## 게임 해보기
* [뉴욕 타임즈 Wordle](https://www.nytimes.com/games/wordle/index.html) - 하루에 하나의 단어를 맞춰보세요.
* [Wordly](https://wordly.org/) - 무제한으로 게임을 즐길 수 있습니다.

## TODO
- [ ]: 웹 인터페이스 개선
- [ ]: 영어 단어 싸전 개선
