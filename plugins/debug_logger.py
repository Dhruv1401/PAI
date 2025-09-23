import os
from datetime import datetime

class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config
        os.makedirs("data/logs", exist_ok=True)
        self.log_file = f"data/logs/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        print(f"[DebugLogger] Logging to {self.log_file}")

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

    def run(self):
        self.log("[DebugLogger] Started successfully.")
