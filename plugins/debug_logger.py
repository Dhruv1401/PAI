import os, datetime
class Transcript:
    def __init__(self):
        os.makedirs("data/logs",exist_ok=True)
        timestamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_path=f"data/logs/transcript_{timestamp}.txt"

    def save(self,role,text):
        with open(self.file_path,"a",encoding="utf-8") as f:
            f.write(f"{role}: {text}\n")
