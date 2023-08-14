from fastapi import FastAPI, UploadFile, HTTPException
from PIL import Image
import base64
import requests
import openai
from typing import List
from io import BytesIO

app = FastAPI()

openai.api_key = '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'

@app.post("/upload/")
async def upload_image(file: UploadFile):
    try:
        # load image with PIL and convert to base64
        image = Image.open(file.file)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())

        # send image to external API for tagging
        payload = {
            'image': img_str.decode(),
            'model': 'mld-caformer.dec-5-97527',
            'threshold': 0.35
        }
        response = requests.post('http://127.0.0.1:7860/tagger/v1/interrogate', json=payload)
        response.raise_for_status()
        tags = response.json()['caption']

        # concatenate all tags into a single user message
        tag_message = ', '.join([f'{tag}: {value}' for tag, value in tags.items()])

        # send tags to GPT-4 API for caption generation
        chat_messages = [
            {'role': 'system', 'content': 'You generate a detailed natural language description of a photo based on a list of tags and weights received. Tags related to style should be ignored. Do not make up any details, only use the tags provided.'},
            {'role': 'user', 'content': tag_message}
        ]
        response = openai.ChatCompletion.create(model="gpt-4", messages=chat_messages)
        caption = response['choices'][0]['message']['content']

        return {'caption': caption}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
