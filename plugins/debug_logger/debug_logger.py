import os
import datetime

LOG_FILE = "logs/debug.log"

def init():
    os.makedirs("logs", exist_ok=True)
    log("🔍 Debug Logger initialized.")

def log(message: str):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def wrap_function(name, func):
    def wrapper(*args, **kwargs):
        log(f"▶️ Function `{name}` called with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            log(f"✅ `{name}` completed successfully.")
            return result
        except Exception as e:
            log(f"❌ Error in `{name}`: {e}")
            raise
    return wrapper
