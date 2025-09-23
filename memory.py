import json
import os
from datetime import datetime

class Memory:
    def __init__(self):
        self.qa_file = "data/qa.json"
        self.chat_dir = "data/chats"
        os.makedirs(self.chat_dir, exist_ok=True)

        if not os.path.exists(self.qa_file):
            with open(self.qa_file, "w") as f:
                json.dump({}, f)

    def get_scripted_response(self, query):
        with open(self.qa_file, "r") as f:
            qa = json.load(f)
        return qa.get(query.lower(), None)

    def add_scripted_response(self, query, answer):
        with open(self.qa_file, "r") as f:
            qa = json.load(f)
        qa[query.lower()] = answer
        with open(self.qa_file, "w") as f:
            json.dump(qa, f, indent=2)

    def save_chat(self, user_input, response):
        """Save conversations with timestamp."""
        date = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.chat_dir, f"{date}.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "user": user_input,
            "assistant": response
        })

        with open(file_path, "w") as f:
            json.dump(history, f, indent=2)

    def recall_last(self, n=5):
        """Recall last n exchanges from today."""
        date = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.chat_dir, f"{date}.json")

        if not os.path.exists(file_path):
            return []

        with open(file_path, "r") as f:
            history = json.load(f)
        return history[-n:]
