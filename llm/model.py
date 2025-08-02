import os
from llama_cpp import Llama

# ✅ Set absolute path to your model
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mistral-7b-instruct-v0.2.Q3_K_L.gguf"))

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at: {model_path}")

# ✅ Use Mistral's built-in chat template
llm = Llama(
    model_path=model_path,
    chat_format="mistral-instruct",   # or "mistral-instruct" if supported directly
    n_ctx=1024,             # Less than 4096 = faster
    n_threads=8,            # Use logical CPU cores
    n_gpu_layers=20,        # If using 4GB–6GB VRAM 
    verbose=False
)


# ✅ Expose this function so generator.py can import it
def chat_with_model(prompt_text):
    messages = [{"role": "user", "content": prompt_text}]
    output = llm.create_chat_completion(
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )
    return output["choices"][0]["message"]["content"]
