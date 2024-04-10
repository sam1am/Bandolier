import json
import os
from dotenv import load_dotenv
import openai
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_text(title, description, transcript):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"We are looking for videos that primarily contain real, staged, or demonstrated mental health counseling sessions between a professional and a patient. Analyze the video based on the provided information and return TRUE if the video is likely to contain a real, demonstrated, staged, or role-played mental health therapy, counseling, or coaching session between a professionl and a client or clients. Otherwise, return FALSE.\nVideo Title: '{title}'\nVideo Description: '{description}'\nVideo Transcript Excerpt: '{transcript}'."}
        ]
    )

    response = completion.choices[0].message['content']
    return 'TRUE' if 'TRUE' in response else 'FALSE'

def main():
    # Load data from JSON file
    with open('output_scrubbed.json', 'r') as f:
        data = json.load(f)

    for video in data:
        # print(f"Processing video: {video['url']}")
        title = video['title']
        description = video['description'][:500] if video['description'] else ''  # First 500 characters of the description

        # Get rid of SRT timestamps and extra newlines
        if video['captions']:
            scrubbed_transcript = re.sub(r'\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+', '', video['captions']) 
            scrubbed_transcript = re.sub(r'\n+', '\n', scrubbed_transcript)
        else:
            scrubbed_transcript = ''
        transcript = scrubbed_transcript[:1000]  # First 1000 characters of the scrubbed SRT

        is_dialogue = analyze_text(title, description, transcript)
        print(title, is_dialogue)
        video['is_dialogue'] = is_dialogue

    # Write updated data back to JSON file
    with open('output_scrubbed.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()