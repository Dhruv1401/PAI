def run(user_input=None, **kwargs):
    if user_input and user_input.lower().startswith("schedule "):
        task = user_input[9:]
        return f"Task scheduled: {task}"
    return None
