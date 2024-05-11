import cv2
import base64
import requests
import time
import json
from threading import Thread
import os

observations = []

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

def behold(encoded_image: str, prompt: str) -> requests.Response:
    payload = {
        "model": "bakllava",
        "prompt": prompt,
        "images": [encoded_image]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post("http://localhost:11434/api/generate", headers=headers, json=payload)
    return response

def capture_and_send_frame(stream_url, base_prompt, interval):
    global observations  # Declare observations as global to ensure it's the same list being accessed in the thread
    
    cap = cv2.VideoCapture(stream_url)
    image_directory = './m5_imgs'
    log_file = './m5_beheld.log'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    if not os.path.exists(log_file):
        with open(log_file, 'w'):
            pass

    while True:
        for _ in range(30):
            cap.grab()

        ret, frame = cap.read()
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                encoded_image = base64.b64encode(buffer).decode('utf-8')
                
                # Generate the current prompt using the latest five observations
                recent_observations = '\n'.join(obs['response'] for obs in observations[-2:])
                current_prompt = base_prompt
                
                response = behold(encoded_image, current_prompt)
                
                if response.status_code == 200:
                    full_response, done = concatenate_results(response)
                    
                    if done:
                        filename = os.path.join(image_directory, time.strftime("%Y%m%d-%H%M%S") + '.jpg')
                        print("-----------\n" + filename)
                        print(full_response + "\n\n")
                        cv2.imwrite(filename, frame)
                        
                        with open(log_file, 'a') as f:
                            f.write(filename + ", " + full_response + "\n")
                        
                        # Add the observation to the list and ensure the list has no more than five entries
                        observations.append({
                            'response': full_response
                        })
                        observations = observations[-2:]

                else:
                    print("Failed to get a valid response from API")
            else:
                print("Failed to encode the frame")
        else:
            print("Failed to capture the frame")
        
        time.sleep(interval)

def main(stream_url, base_prompt, interval):
    thread = Thread(target=capture_and_send_frame, args=(stream_url, base_prompt, interval))
    thread.daemon = True
    thread.start()

    try:
        while True: time.sleep(100)
    except KeyboardInterrupt:
        print("Stopping video capture...")

if __name__ == "__main__":
    stream_url = 'rtsp://192.168.81.37:8554/mjpeg/1'
    base_prompt = "You are P, a visual observer. Give a detailed description of what you see starting with 'I see ...'."
    interval = 30  # seconds
    main(stream_url, base_prompt, interval)
