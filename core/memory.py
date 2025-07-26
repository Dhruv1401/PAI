# core/memory.py
import json
from datetime import datetime

class ShortTermMemory:
    def __init__(self):
        self.memory = []
        self.file_path = "memory/startup_memory.json"
        self.load()

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                self.memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory = []

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def add(self, role, content):
        self.memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def get_recent(self, n=5):
        return self.memory[-n:] if len(self.memory) >= n else self.memory
