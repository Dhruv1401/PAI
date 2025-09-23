import json
import os

class Memory:
    def __init__(self):
        self.qa_file = "data/qa.json"
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
