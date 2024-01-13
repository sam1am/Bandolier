import streamlit as st
import requests
import base64
import json
from PIL import Image
from io import BytesIO
from langchain.llms import Ollama

llm=Ollama(model="mistral")

# Define the function to send requests to the external API
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

# Streamlit app starts here
st.title('Get Roasted')

# Prompt is hardcoded
prompt = 'Describe this image in as much detail as possible. Be as verbose as you possibly can be.'

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])


if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    generate_roast(prompt, image)
    # Convert the uploaded image to base64
    if st.button("Regenerate"):
        generate_roast(prompt, image)

