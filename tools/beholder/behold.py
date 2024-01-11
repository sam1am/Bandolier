import torch
from lavis.models import load_model_and_preprocess
from PIL import Image
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
raw_image = Image.open("./dragon.png").convert("RGB")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, vis_processors, _ = load_model_and_preprocess(
    name="blip_caption", model_type="large_coco", is_eval=True, device=device)
image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
captions = model.generate({"image": image}, use_nucleus_sampling=True)
for caption in captions:
    print(caption)

