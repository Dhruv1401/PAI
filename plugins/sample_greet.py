def run(user_input=None, **kwargs):
    if user_input and user_input.lower() in ["hello", "hi", "hey"]:
        return "Hello again, Dhruv! Ready when you are 😉"
    return None
