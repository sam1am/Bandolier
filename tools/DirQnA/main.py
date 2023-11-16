from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os
import shutil
import secrets
from QnABot import QnABot

load_dotenv()

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

security = HTTPBasic()

app = FastAPI(docs_url=None, redoc_url=None)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != username or credentials.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/docs")
def docs(credentials: HTTPBasicCredentials = Depends(security)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/redoc")
def redoc(credentials: HTTPBasicCredentials = Depends(security)):
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")

@app.get("/openapi.json")
def get_open_api(credentials: HTTPBasicCredentials = Depends(security)):
    return get_openapi(title="API", version=1, routes=app.routes)

@app.post("/query", response_model=dict)
def answer_query(query: str, credentials: HTTPBasicCredentials = Depends(security), file: UploadFile = File(...)):
    working_dir = secrets.token_hex(nbytes=16)
    os.makedirs(working_dir, exist_ok=True)

    file_path = f"{working_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    bot = QnABot(directory=working_dir)
    result = bot.get_answer(query)

    shutil.rmtree(working_dir, ignore_errors=True)
    # bot.search_index.clear()

    return {"result": result}
