Output of tree command:
```
|-- app.py
|-- templates
    |-- index.html
    |-- response.html

```

---

./app.py
```
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

app = Flask(__name__)
CORS(app)

# You may use Ollama directly or setup as before
llm = Ollama(model="mistral")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                image = Image.open(file)
                prompt = 'Describe this image in as much detail as possible. Be as verbose as you possibly can be.'
                roast = generate_roast(prompt, image)
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

def generate_roast(prompt, image):
    # Convert the uploaded image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
  
    with st.spinner('Checking out the image...'):
        response = send_request_to_external_api(encoded_image, prompt)

        if response.status_code == 200:
            full_response, done = concatenate_results(response)
            st.success('Done!')
            # st.write(full_response)
        else:
            st.error('Error: {}'.format(response.text))

    with st.spinner('Roasting...'):
        roast = llm("You are roastbot and your job is to roast the subject of the image based on its description in the style of a comedy central comedian.\nImage Description:" + full_response)

    st.write("Roast:" + roast)


if __name__ == '__main__':
    app.run(debug=True)
```
---

./templates/response.html
```
<!-- response.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roast Result</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .response-container {
            background: #fff;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            width: 80%;
            max-width: 600px;
        }
        .response-container p {
            font-size: 1.2rem;
        }
        .back-link {
            color: #888;
            text-decoration: none;
            margin-top: 2rem;
        }
        .back-link:hover {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="response-container">
        <h1>Your Roast:</h1>
        <p>{{ roast }}</p>
        <a href="/" class="back-link">Go back</a>
    </div>

    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```
---

./templates/index.html
```
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get Roasted</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }

        .upload-container {
            background: #fff;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .form-control {
            border-radius: 0.7rem;
        }

        .btn-primary {
            background-color: #4CAF50;
            border: none;
            border-radius: 0.7rem;
        }

        .btn-primary:hover {
            background-color: #45a049;
        }

        h1 {
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
</head>

<body>
    <div class="upload-container">
        <h1>Upload your image to get roasted</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <input type="file" name="file" class="form-control" required><br>
            <button type="submit" class="btn btn-primary btn-block">Upload</button>
        </form>
    </div>

    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>```
---
