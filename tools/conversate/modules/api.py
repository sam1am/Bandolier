
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from .llm_api import process_query
from .database import log_interaction, get_last_messages
import os
import re
import json
import uuid
from datetime import datetime


app = Flask(__name__)
auth = HTTPBasicAuth()

API_PASSWORD = 'lookatmeimanapikey'

@auth.verify_password
def verify_password(username, password):
    return password == API_PASSWORD

@app.route('/api/query', methods=['POST'])
@auth.login_required
def query_api():
    data = request.get_json()
    query_text = data.get('query', '')

    if not query_text:
        return jsonify({'error': 'Query text is missing'}), 400

    # Retrieve the last X messages from the log
    num_messages = int(os.getenv("MESSAGE_HISTORY", 10))
    message_history = get_last_messages(num_messages)

    # Process the query using llm_api with message history
    response_text = process_query(query_text, message_history)

    # Extract the JSON object from the response using regular expressions
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    response_json = None
    if json_match:
        json_string = json_match.group()
        try:
            response_json = json.loads(json_string)
        except json.JSONDecodeError:
            pass

    short_answer = response_json.get("short_answer") if response_json else None

    # Log the interaction
    query_uuid = str(uuid.uuid4())
    log_interaction(query_uuid, "", query_text, response_text, "")

    return jsonify({'short_answer': short_answer})