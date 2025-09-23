from memory import Memory

class Brain:
    def __init__(self, config):
        self.memory = Memory()
        self.config = config

    def process_input(self, user_input):
        # 1. Recall if asked
        if user_input.lower() in ["recall", "history"]:
            recalled = self.memory.recall_last(5)
            return "\n".join([f"{h['time']} You: {h['user']} | Jarvis: {h['assistant']}" for h in recalled]) or "No history yet."

        # 2. Scripted responses
        answer = self.memory.get_scripted_response(user_input)
        if answer:
            self.memory.save_chat(user_input, answer)
            return answer

        # 3. Fallback to local LLM
        response = self.local_llm_response(user_input)
        self.memory.save_chat(user_input, response)
        return response

    def local_llm_response(self, text):
        # Placeholder for llama.cpp or tinyllm integration
        return f"[LLM simulated] You said: {text}"
