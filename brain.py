from memory import Memory

class Brain:
    def __init__(self, config):
        self.memory = Memory()
        self.config = config

    def process_input(self, user_input):
        # 1. Check scripted Q&A
        answer = self.memory.get_scripted_response(user_input)
        if answer:
            return answer

        # 2. Fallback to local LLM
        return self.local_llm_response(user_input)

    def local_llm_response(self, text):
        # Placeholder — integrate llama.cpp or tinyllm
        return f"[LLM response simulated] You said: {text}"
