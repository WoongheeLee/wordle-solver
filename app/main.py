import sys
sys.path.append("../py")

from solver import WordleSolver

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()

solver = WordleSolver()

templates = Jinja2Templates(directory='../frontend')


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):

    global solver
    solver = WordleSolver() # 솔버 클래스 다시 생성
    solutions = solver.sample_word()
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
    solutions = solver.sample_word(yes=yes, wrong=wrong, no=no)


    return solutions


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", reload=True)