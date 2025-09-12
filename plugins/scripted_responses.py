import json
import os

RESPONSES_FILE = os.path.join("plugins", "scripted_responses", "responses.json")

def load_responses():
    try:
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("[ScriptedResponses] ERROR: Invalid JSON format in responses file.")
        return {}

def apply(context):
    """Intercepts user input and returns predefined reply if exists."""
    user_input = context.get("user_input", "").strip().lower()
    responses = load_responses()

    if user_input in responses:
        context["response"] = responses[user_input]
        context["skip_llm"] = True  # Signal main.py to not call the model
    return context
