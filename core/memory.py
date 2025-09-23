import json, os, datetime

class Memory:
    def __init__(self, base_path="data/memory"):
        os.makedirs(base_path, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_path = os.path.join(base_path, f"session_{timestamp}.json")
        self.chat_log = []

    def add(self, role, content):
        self.chat_log.append({"role": role, "content": content})
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.chat_log, f, indent=2)

    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            self.chat_log = json.load(f)
        return self.chat_log
