#check for a conda environment named beholder and create it if it doesn't exist
if conda env list | grep -q "beholder"; then
    echo "beholder environment already exists"
else
    echo "beholder environment does not exist, creating it now"
    conda create -n beholder python=3.8
fi
conda activate lavis
conda install pytorch torchvision cudatoolkit=11.0
pip install salesforce-lavis

curl -sfL https://raw.githubusercontent.com/janhq/nitro/main/install.sh | sudo /bin/bash -

mkdir model && cd model
wget -O llama-2-7b-model.gguf https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q5_K_M.gguf?download=true

nohup nitro & 

curl http://localhost:3928/inferences/llamacpp/loadmodel \
  -H 'Content-Type: application/json' \
  -d '{
    "llama_model_path": "/model/llama-2-7b-model.gguf",
    "ctx_len": 512,
    "ngl": 100,
  }'

curl http://localhost:3928/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Who won the world series in 2020?"
      },
    ]
  }'