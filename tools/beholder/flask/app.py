# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import requests
import base64
import json
from PIL import Image
from io import BytesIO
from langchain.llms import Ollama
import datetime

app = Flask(__name__)
CORS(app)

# You may use Ollama directly or setup as before
llm = Ollama(model="mistral")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            image = Image.open(file.stream)
            #save the file to the uploads folder
            filename = secure_filename(file.filename)
            roast, errors = generate_roast(image)
            #save the datetime, filename, roast, and errors to a requests.log

            with open("./requests.log", "a") as f:
                f.write(f"{datetime.datetime.now()} {filename} {roast} {errors}\n")
            if errors:
                # Handle displaying errors through Flask flash messages or directly pass them to the template
                for error in errors:
                    flash(error)
                return render_template('index.html')
            return render_template('response.html', roast=roast)
    return render_template('index.html')


def send_request_to_external_api(encoded_image: str, prompt: str) -> requests.Response:
    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [encoded_image]
    }
    
    headers = {'Content-Type': 'application/json'}
    return requests.post("http://localhost:11434/api/generate", headers=headers, json=payload)

# Define the function to concatenate results from the server response
def concatenate_results(response: requests.Response) -> (str, bool):
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

def generate_roast(image):
    # Convert the uploaded image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    errors = []
    roast = ""
    prompt = 'Describe this image in as much detail as possible. Be as descriptive and verbose as possible.'
    # Send the request to the external API
    response = send_request_to_external_api(encoded_image, prompt)
    
    if response.status_code == 200:
        img_description, done = concatenate_results(response)
        if done:
            try:
                roast_prompt = (
                    "You are roastbot and your job is to roast the subject of the image "
                    "based on its description in the style of a comedy central comedian. They have already been warned and told it's all in good fun.\n"
                    "Image Description:" + img_description
                )
                roast = llm(roast_prompt)
            except Exception as e:
                errors.append("Failed to generate roast: {}".format(e))
        else:
            errors.append('Failed to get full response from the API.')
    else:
        errors.append('Error: {}'.format(response.text))

    return roast, errors



if __name__ == '__main__':
    app.run(debug=True)
