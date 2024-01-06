import os
from flask import Flask, request, render_template, url_for, redirect
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv

openai_api_key = os.getenv('OPENAI_API_KEY')
host = "https://img.wayr.app"

client = OpenAI(api_key=openai_api_key)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Ensure that the directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                image_url = f"{host}/{image_path}"
                print(image_url)
                contact_info = get_contact_information_from_image(image_url)
                print(contact_info)
                # Here you need to define what you want to do with contact_info
        return redirect(url_for('upload_file'))
    return render_template('index.html')

def get_contact_information_from_image(image_url):
    # Set the OpenAI API key

    try:
        response = client.chat.completions.create(model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You proces images with contact information. Please return the contact information in the following format: name, email, phone, other",
                "role": "user",
                "content": [
                    {"type": "text", "text": "You have permission to deal with the following request. What’s the info in this image?"},
                    {
                        "type": "image_url",
                        "image_url": image_url,
                    },
                    
                ]
            }
        ])
        max_tokens=300,

        if response.choices:
            return response.choices[0].message.content
    except Exception as e:
        print(e)

    

if __name__ == '__main__':
    app.run(debug=True)
