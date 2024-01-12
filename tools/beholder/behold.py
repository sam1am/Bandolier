import torch
from lavis.models import load_model_and_preprocess
from PIL import Image
import time
import os

# from langchain.callbacks.manager import CallbackManager
# from langchain.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama

# llm_llama2 = Ollama(model="llama2")
# llm_mistral = Ollama(model="mistral")
# llm_dolphin_phi = Ollama(model="dolphin-phi")
# llm_llama2_uncensored = Ollama(model="llama2-uncensored")
# llm_orca_mini = Ollama(model="orca-mini")
# llm_llava = Ollama(model="llava")

# llms = ['llama2', 'mistral', 'dolphin-phi', 'llama2-uncensored', 'orca-mini', 'llava']
llms = ['mistral', 'llama2-uncensored', 'llava']

caption_count = 10


# from lavis.models import model_zoo
# print(model_zoo)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, vis_processors, _ = load_model_and_preprocess(
    name="blip_caption", model_type="base_coco", is_eval=True, device=device)


#get a list of images with jpg or png extension in the ./testimgs folder
images = [f for f in os.listdir("./testimgs") if f.endswith(('.jpg', '.png'))]
for image in images:
    print("\n\nImage: ", image)
    
    start_time = time.time()
    raw_image = Image.open("./testimgs/" + image).convert("RGB")
    image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
    captions = model.generate({"image": image}, use_nucleus_sampling=True, num_captions=caption_count)
    all_captions = ""
    i = 0
    for caption in captions:
        all_captions += "Caption " + str(i) + ": " + caption + " \n"
        i += 1
        # print(caption)
    print("\n\nAll captions: ", all_captions)
    
    for llm in llms:
        print("\n\n\n--------------------------\n\n\nProcessing for llm: ", llm)
        model = Ollama(model=llm)
        result = model("Several versions of a caption based on the same single image are provided below. Write a comedy central style roast of the subjects in the photo:\n" + all_captions)
        print("\n\nLLM: ", llm)
        print("Result: ", result)
    end_time = time.time()
    # poem = llm("Write a poem based off of the following image description: " + all_captions)
    # image_abs_path = os.path.abspath("./testimgs/" + image)
    # caption = llm_llava("Write a detailed caption for the following image: " + image_abs_path)
    # print("llava caption: ", caption)
    print("Time taken: ", end_time - start_time)

# model, vis_processors, txt_processors = load_model_and_preprocess(name="blip_vqa", model_type="vqav2", is_eval=True, device=device)
# question = "Describe this photo in exhaustive detail."
# image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
# question = txt_processors["eval"](question)
# answer = model.predict_answers(samples={"image": image, "text_input": question}, inference_method="generate")
# print(answer)

# def get