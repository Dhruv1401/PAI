# llm/generator.py
from llm.model import load_model, generate_from_model
from plugins.plugin_manager import apply_plugin_hooks

# Load the model once at startup
MODEL = load_model()

def generate_response(context, personality=""):
    """
    Generate a response using the model and context (list of dicts).
    Applies plugins first.
    """
    # Flatten context to prompt
    prompt = ""
    for msg in context:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            prompt += f"User: {content}\n"
        else:
            prompt += f"Assistant: {content}\n"

    # Apply plugins (for scripted responses)
    plugin_response = apply_plugin_hooks(context, prompt)
    if plugin_response is not None:
        return plugin_response

    # Add personality
    if personality:
        prompt = f"{personality}\n{prompt}"

    response = generate_from_model(MODEL, prompt)
    return response.strip()
