class Plugin:
    def __init__(self, config):
        self.config = config
        self.name = "scripted_responses"
        self.responses = {
            "hello": f"Hello! I am {config.get('assistant_name', 'Assistant')}.",
            "who are you": f"I am {config.get('assistant_name', 'Assistant')}, your personal AI.",
            "how are you": "I am functioning as expected. What about you?",
            "bye": "Goodbye! Talk to you later."
        }

    def can_handle(self, text):
        return text.lower() in self.responses

    def handle(self, text):
        return self.responses.get(text.lower(), None)
