import sys
import os
import argparse
sys.path.append("../py")

from solver import WordleSolver

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()

# 전략 선택: 환경변수 기본값, __main__에서 CLI로 재정의 가능
STRATEGY = os.environ.get('WS_STRATEGY', 'random')
VOCAB_PATH = os.environ.get('WS_VOCAB', '../dictionary/full_vocabs.txt')
UNIQUE_PATH = os.environ.get('WS_UNIQUE', '../dictionary/unique.txt')

solver = WordleSolver(path_vocab=VOCAB_PATH, path_unique=UNIQUE_PATH)

templates = Jinja2Templates(directory='../frontend')


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):

    global solver
    solver = WordleSolver(path_vocab=VOCAB_PATH, path_unique=UNIQUE_PATH) # 선택된 사전으로 재생성
    solutions = solver.sample_word(strategy=STRATEGY, itr=50)  # 더 많은 추천 단어 제공
    suggestions = solutions['suggestions']
    word_nums = solutions['word_nums']
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "suggestions": suggestions, 
            "word_nums": word_nums})


@app.post("/submit")
async def submit(request: Request):
    global solver 

    data = await request.json()
    text = data['text']
    clicks = data['clicks']


    yes = [None] * 5
    wrong = [None] * 5
    no = None

    # clicks: 1 -> no, 2 -> wrong, 3 -> yes
    for i in range(5):
        c = int(clicks[i])
        if c==1:
            if not no:
                no = set()
            no.add(text[i])
        elif c==2:
            wrong[i] = text[i]
        elif c==3:
            yes[i] = text[i]

    wrong = tuple(wrong)
    solutions = solver.sample_word(yes=yes, wrong=wrong, no=no, strategy=STRATEGY, itr=50)  # 더 많은 추천 단어 제공


    return solutions


@app.get('/config/dictionaries')
async def list_dictionaries():
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dictionary'))
    files = []
    try:
        for name in os.listdir(base):
            if name.lower().endswith('.txt'):
                files.append(name)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return {"directory": base, "files": sorted(files)}


@app.post('/config/dictionary')
async def set_dictionary(request: Request):
    global solver, VOCAB_PATH, UNIQUE_PATH
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "invalid JSON"})

    base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dictionary'))

    vocab_path = data.get('vocab_path')
    unique_path = data.get('unique_path')
    preset_vocab = data.get('preset_vocab')
    preset_unique = data.get('preset_unique')

    if preset_vocab:
        vocab_path = os.path.join(base, preset_vocab)
    if preset_unique:
        unique_path = os.path.join(base, preset_unique)

    # 기본값 유지 옵션
    if not vocab_path:
        vocab_path = VOCAB_PATH
    if not unique_path:
        unique_path = UNIQUE_PATH

    # 경로 정규화 및 존재 확인
    vocab_path = os.path.normpath(vocab_path)
    unique_path = os.path.normpath(unique_path)
    if not os.path.exists(vocab_path):
        return JSONResponse(status_code=400, content={"error": f"vocab file not found: {vocab_path}"})
    if not os.path.exists(unique_path):
        return JSONResponse(status_code=400, content={"error": f"unique file not found: {unique_path}"})

    # 반영 및 솔버 재생성
    VOCAB_PATH, UNIQUE_PATH = vocab_path, unique_path
    solver = WordleSolver(path_vocab=VOCAB_PATH, path_unique=UNIQUE_PATH)
    solutions = solver.sample_word(strategy=STRATEGY)
    return {"message": "dictionary set", "vocab_path": VOCAB_PATH, "unique_path": UNIQUE_PATH, "initial": solutions}


@app.post('/add_word')
async def add_user_word(request: Request):
    """
    사용자가 발견한 새로운 단어를 user_words.txt에 추가
    """
    global solver
    try:
        data = await request.json()
        word = data.get('word', '').strip().lower()
        
        if not word:
            return JSONResponse(status_code=400, content={"error": "단어가 제공되지 않았습니다"})
        
        if len(word) != 5 or not word.isalpha():
            return JSONResponse(status_code=400, content={"error": "5글자 영문 단어만 추가 가능합니다"})
        
        # user_words.txt 파일 경로
        base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dictionary'))
        user_words_path = os.path.join(base_dir, 'user_words.txt')
        
        # 기존 단어들 읽기 (중복 방지)
        existing_words = set()
        if os.path.exists(user_words_path):
            with open(user_words_path, 'r', encoding='utf-8') as f:
                existing_words = {line.strip().lower() for line in f if line.strip()}
        
        # 이미 존재하는 단어인지 확인
        if word in existing_words:
            return JSONResponse(status_code=200, content={"message": f"'{word.upper()}'는 이미 사용자 사전에 있습니다", "added": False})
        
        # 새 단어 추가
        with open(user_words_path, 'a', encoding='utf-8') as f:
            f.write(f"{word}\n")
        
        # 솔버 재생성 (새 단어가 포함된 사전으로)
        solver = WordleSolver(path_vocab=VOCAB_PATH, path_unique=UNIQUE_PATH)
        
        return JSONResponse(status_code=200, content={"message": f"'{word.upper()}'를 사용자 사전에 추가했습니다", "added": True})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"단어 추가 중 오류가 발생했습니다: {str(e)}"})}


if __name__ == '__main__':
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', choices=['random','freq'], default=STRATEGY, help='추천 전략 선택')
    parser.add_argument('--vocab', default=VOCAB_PATH, help='전체 후보(허용 추측) 사전 경로')
    parser.add_argument('--unique', default=UNIQUE_PATH, help='초기 추천용(유니크 문자) 사전 경로')
    args = parser.parse_args()
    # 환경변수로도 전달하여 reload 시에도 유지
    os.environ['WS_STRATEGY'] = args.strategy
    STRATEGY = args.strategy
    os.environ['WS_VOCAB'] = args.vocab
    os.environ['WS_UNIQUE'] = args.unique
    VOCAB_PATH = args.vocab
    UNIQUE_PATH = args.unique

    uvicorn.run("main:app", reload=True)
