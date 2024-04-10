from pytube import Search, YouTube
import json
from dotenv import load_dotenv
import openai
import os
from json import loads

import requests

def get_description(video: YouTube) -> str:
    i: int = video.watch_html.find('"shortDescription":"')
    desc: str = '"'
    i += 20  # excluding the `"shortDescription":"`
    while True:
        letter = video.watch_html[i]
        desc += letter  # letter can be added in any case
        i += 1
        if letter == '\\':
            desc += video.watch_html[i]
            i += 1
        elif letter == '"':
            break
    return loads(desc)


def main():
    # Read queries from file
    with open('queries.txt') as f:
        queries = [line.strip() for line in f]

    processed_urls = set()

    output = []

    for query in queries:
        s = Search(query)
        # Fetch first set of results
        for video in s.results:
            if video.watch_url in processed_urls:
                
                continue

            yt = YouTube(video.watch_url)

            duration = yt.length / 60
            # stream = yt.streams.first()
            description = get_description(yt)
            # captions_text = yt.captions.get_by_language_code('en').generate_srt_captions() if 'en' in yt.captions else Nonetion: {description}")
            # if result == 'TRUE':
            if duration > 35:
                print(f"Title: {video.title}")
                output.append({'url': video.watch_url, 'title': video.title, 'description': description, 'captions': ''})
                processed_urls.add(video.watch_url)

    # Write output to JSON file
    with open('output.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
