from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def process_query(query):
    completion = client.chat.completions.create(
        model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=0.7,
    )
    response_text = completion.choices[0].message
    return response_text
