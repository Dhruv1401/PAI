import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
