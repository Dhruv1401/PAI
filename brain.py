from memory import Memory
from llama_cpp import Llama

class Brain:
    def __init__(self, config):
        self.memory = Memory()
        self.config = config
        model_path = "models/mistral-7b-instruct-v0.2.Q3_K_L.gguf"

        try:
            self.llm = Llama(model_path=model_path, n_ctx=1024, n_threads=4)
            print("[Brain] LLM loaded successfully.")
        except Exception as e:
            print("[Brain] Failed to load LLM:", e)
            self.llm = None

    def process_input(self, user_input):
        # 1. Recall
        if user_input.lower() in ["recall", "history"]:
            recalled = self.memory.recall_last(5)
            return "\n".join([f"{h['time']} You: {h['user']} | Jarvis: {h['assistant']}" for h in recalled]) or "No history yet."

        # 2. Scripted responses
        answer = self.memory.get_scripted_response(user_input)
        if answer:
            self.memory.save_chat(user_input, answer)
            return answer

        # 3. LLM Fallback
        response = self.local_llm_response(user_input)
        self.memory.save_chat(user_input, response)
        return response

    def local_llm_response(self, text):
        if not self.llm:
            return f"[LLM unavailable] You said: {text}"

        output = self.llm(
            f"You are Jarvis, a helpful AI assistant.\nUser: {text}\nJarvis:",
            max_tokens=128,
            stop=["User:"]
        )
        return output["choices"][0]["text"].strip()
