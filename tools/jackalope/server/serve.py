from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
import os
from datetime import datetime
import json
#language model related imports
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain
#image processing
import base64
from io import BytesIO
# from IPython.display import HTML, display
from PIL import Image




llm = Ollama(model="mistral")
vision_llm = Ollama(model="bakllava")


# Load environment variables
load_dotenv()

# Basic Auth setup
security = HTTPBasic()

# Create and configure FastAPI app instance
app = FastAPI()

# Path to the uploads folder
UPLOAD_DIR = "./uploads"

# Database file path
DB_FILE = "./db/requests_log.json"

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("API_USER")
    correct_password = os.getenv("API_PASS")
    if credentials.username == correct_username and credentials.password == correct_password:
        return credentials.username
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

def log_request(req_type, details, response):
    """Log request details to a simple JSON database."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as db:
            json.dump([], db)
    
    with open(DB_FILE, "r+") as db:
        data = json.load(db)
        data.append({
            "timestamp": datetime.now().isoformat(),
            "type": req_type,
            "details": details,
            "response": response,
        })
        db.seek(0)
        json.dump(data, db, indent=4)

@app.post("/text")
def handle_text(request_data: str = Body(), username: str = Depends(get_current_username)):
    # response = f"Howdy Doo! You said: {request_data}"
    response = ask_llm(request_data)
    log_request("text", {"user": username, "request_data": request_data}, response)
    return {"response": response}

@app.post("/audio")
async def handle_audio(file: UploadFile = File(...), username: str = Depends(get_current_username)):
    file_location = os.path.join(UPLOAD_DIR, "audio", file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    response = "Oh boy!"
    log_request("audio", {"user": username, "file": file_location}, response)
    return {"response": response}

@app.post("/file")
async def handle_file(text: str, file: UploadFile = File(...), username: str = Depends(get_current_username)):
    file_location = os.path.join(UPLOAD_DIR, "file", file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    response = "File received!"
    log_request("file", {"user": username, "file": file_location, "text": text}, response)
    return {"response": response}

@app.post("/image")
async def handle_image(text: str, file: UploadFile = File(...), username: str = Depends(get_current_username)):
    file_location = os.path.join(UPLOAD_DIR, "image", file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    response = "bingo!"
    log_request("image", {"user": username, "file": file_location, "text": text}, response)
    return {"response": response}

def ask_llm(text):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an intelligent AI assistant named Jackalope."),
        ("user", f"{text}"),
    ])
    # chain = prompt | llm
    # chain.invoke({"input": text})
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({"input": text})

    return response

# Image Processing

def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized Base64 string
    """

    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def plt_img_base64(img_base64):
    """
    Display base64 encoded string as image

    :param img_base64:  Base64 string
    """
    # Create an HTML img tag with the base64 string as the source
    image_html = f'<img src="data:image/jpeg;base64,{img_base64}" />'
    # Display the image by rendering the HTML
    display(HTML(image_html))

#example
# file_path = "../../../static/img/ollama_example_img.jpg"
# pil_image = Image.open(file_path)
# image_b64 = convert_to_base64(pil_image)
# plt_img_base64(image_b64)
#     llm_with_image_context = bakllava.bind(images=[image_b64])
# llm_with_image_context.invoke("What is the dollar based gross retention rate:")