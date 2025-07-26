import psutil

def run(user_input=None, **kwargs):
    if user_input and "diagnose" in user_input.lower():
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        return f"[Diagnostics] CPU: {cpu}% | RAM: {ram}%"
    return None
