import json
import os

RESPONSES_FILE = os.path.join(os.path.dirname(__file__), "scripted_responses", "responses.json")

with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
    RESPONSES = json.load(f)

def hook(user_input):
    key = user_input.lower().strip()
    if key in RESPONSES:
        return RESPONSES[key]
    return None
