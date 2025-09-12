import llama_cpp
import os
from llm.model import chat_with_model

context = apply_plugin_hooks(context)


def generate_response(context, personality):
    return chat_with_model(context)

model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mistral-7b-instruct-v0.2.Q3_K_L.gguf"))

llm = llama_cpp.Llama(
    model_path= model_path ,  # ← Update this if path is different
    n_ctx=2048,
    n_threads=8,  # Optional: optimize performance
    n_gpu_layers=32 # Optional: speed up on GPU
    
    
)

# llm/generator.py

def generate_response(context, personality):
    from llm.model import chat_with_model

    full_prompt = ""

    system_prompt = personality.get("system", "")
    if isinstance(system_prompt, str):
        full_prompt += f"<<SYSTEM>> {system_prompt.strip()}\n"

    for msg in context:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if not isinstance(content, str):  # Ensure it's valid
            continue
        full_prompt += f"<<{role.upper()}>> {content.strip()}\n"

    # Final user prompt is the last entry in context
    return chat_with_model(full_prompt)

def trim_context(messages, max_tokens=200):
    trimmed = []
    total = 0
    for msg in reversed(messages):
        msg_tokens = len(msg['content'].split())  # crude estimate
        if total + msg_tokens <= max_tokens:
            trimmed.insert(0, msg)
            total += msg_tokens
        else:
            break
    return trimmed
