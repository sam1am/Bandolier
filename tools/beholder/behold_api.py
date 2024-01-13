from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
import base64
import json
from langchain.llms import Ollama

# requires ollama server

app = FastAPI()

async def concatenate_results(response: requests.Response) -> (str, bool):
    """
    Concatenates line-by-line response content from the server.
    """
    full_response = ""
    done = False
    for line in response.iter_lines():
        if line:
            line_response = json.loads(line)
            full_response += line_response["response"]
            if 'done' in line_response and line_response["done"]:
                done = True
                break
    return full_response, done

def send_request_to_external_api(encoded_image: str, prompt: str) -> requests.Response:
    """
    Sends a POST request to the external API with the encoded image
    and a hardcoded prompt, and returns the response object.
    """
    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [encoded_image]
    }
    
    headers = {'Content-Type': 'application/json'}
    return requests.post("http://localhost:11434/api/generate", headers=headers, json=payload)

@app.post("/analyze_image/")
async def analyze_image(file: UploadFile = File(...), prompt: str = 'What is in this picture?'):
    """
    FastAPI endpoint to analyze an image by sending it to an external API.
    """
    image_content = await file.read()
    encoded_image = base64.b64encode(image_content).decode('utf-8')

    response = send_request_to_external_api(encoded_image, prompt)

    if response.status_code == 200:
        full_response, done = await concatenate_results(response)
        return {"response": full_response, "done": done}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
