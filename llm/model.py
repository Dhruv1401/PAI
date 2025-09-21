# llm/model.py
from pathlib import Path
from llama_cpp import Llama

MODEL_PATH = Path(__file__).parent / "mistral-7b-instruct-v0.2.Q3_K_L.gguf"

def load_model():
    """
    Load the Mistral GGUF model and return the model object.
    """
    return Llama(model_path=str(MODEL_PATH), n_ctx=2048)

def generate_from_model(model, prompt, max_tokens=128):
    """
    Generate text from the model given a prompt string.
    """
    output = model(prompt, max_tokens=max_tokens)
    return output["choices"][0]["text"]
# Initialize the model once