# core/memory.py
import json, os
from datetime import datetime

class Memory:
    def __init__(self):
        os.makedirs("data/memory", exist_ok=True)
        self.file = f"data/memory/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.messages = []

    def save_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        with open(self.file, "w") as f:
            json.dump(self.messages, f, indent=4)
