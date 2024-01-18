import streamlit as st
import torch
from lavis.models import load_model_and_preprocess
from PIL import Image
import time
from langchain.llms import Ollama
import os

PROMPTS_FILE = 'prompts.txt'

def load_prompts():
    try:
        with open(PROMPTS_FILE, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

def save_prompt(new_prompt):
    with open(PROMPTS_FILE, 'a') as file:
        file.write(f"{new_prompt}\n")

def generate_captions(image_path, selected_prompt, caption_count, llms_selected):
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # model, vis_processors, _ = load_model_and_preprocess(name="blip_caption", model_type="base_coco", is_eval=True, device=device)

    start_time = time.time()
    # raw_image = Image.open(image_path).convert("RGB")
    # image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
    # captions = model.generate({"image": image}, use_nucleus_sampling=True, num_captions=caption_count)

    # all_captions = ""
    # for i, caption in enumerate(captions):
    #     all_captions += f"Caption {i}: {caption}\n"

    for llm_name in llms_selected:
        # run the command in terminal `ollama run llava {selected prompt} absolute file path}` and return the result
        os.system(f"ollama run {llm_name} {selected_prompt} {image_path} > output.txt")
        #wait for output.txt to exist...
        time.sleep(5)
        with open("output.txt", "r") as f:
            result = f.read()

        print(result)
            
    return result, time.time() - start_time

# Load existing prompts from file
prompts = load_prompts()

st.title('Beholder')

# Display existing prompts
if prompts:
    selected_prompt = st.selectbox("Select a prompt", prompts)
else:
    selected_prompt = st.empty()

# Input for new prompt
# new_prompt = st.text_input("Create a new prompt")
# if st.button("Save new prompt"):
#     if new_prompt and new_prompt not in prompts:
#         save_prompt(new_prompt)
#         prompts.append(new_prompt)
#         st.success(f"Prompt '{new_prompt}' added successfully!")
#         selected_prompt = st.selectbox("Select a prompt", prompts, index=len(prompts) - 1)  # Update the select box with the new prompt
#     else:
#         st.error("Prompt is empty or already exists.")

# Slider for detail level
# caption_detail = st.slider("Detail (Number of captions to generate)", 1, 3, value=1)
caption_detail = 1

# Checkboxes for LLM selection
# llms_available = {'mistral': "Beholderv1", 'llama2-uncensored': "Beholderv2", 'llava': "Beholderv3"}
llms_available = {'llava': "Beholderv3"}
llms_selected = []
for llm_key in llms_available:
    if st.checkbox(f"{llms_available[llm_key]}", value=True):  # Default all checked
        llms_selected.append(llm_key)

# Uploading the image
uploaded_file = st.file_uploader("Choose an image...", type="jpg")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    st.write("Generating captions...")
    model_comments, elapsed = generate_captions(uploaded_file, selected_prompt, caption_detail, llms_selected)
    for llm_name, comment in model_comments:
        st.write(f"Model {llms_available[llm_name]}: {comment}")
    st.write(f"Time taken for generation: {elapsed}s")
