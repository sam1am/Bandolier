# app.py
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import openai

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        query = request.form.get('query')
        # Run your faiss search here and get the results...
        faiss_results = 'FAISS search results go here...'
        # Pass the faiss results and the user's query to the OpenAI API
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an AI expert in carbon nanotubes. Using the following context, answer the user\'s question with references: ' + faiss_results
                },
                {
                    'role': 'user',
                    'content': query
                }
            ]
        )
        result = completion.choices[0].message['content']

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
