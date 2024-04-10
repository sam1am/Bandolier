import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter

def download_captions(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        captions = transcript.fetch()

        # Format the captions as SRT
        formatter = SRTFormatter()
        captions_srt = formatter.format_transcript(captions)

    except Exception as e:
        captions_srt = None

    return captions_srt

def main():
    # Load data from JSON file
    with open('output_scrubbed.json', 'r') as f:
        data = json.load(f)

    for video in data:
        print(f"Processing video: {video['url']}")
        video_id = video['url'].split('=')[-1]
        captions = download_captions(video_id)
        video['captions'] = captions

    # Write updated data back to JSON file
    with open('output_scrubbed.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
