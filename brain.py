import json
import os
from llama_cpp import Llama

class Brain:
    def __init__(self, config):
        self.config = config
        self.assistant_name = config.get("assistant_name", "Assistant")

        # Load LLM (replace with your llama.cpp params)
        model_path = os.path.join("models", "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)
        print(f"[Brain] LLM loaded successfully as {self.assistant_name}")

    def process(self, messages, debug_callback=None):
        try:
            output = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=200,
                stop=["</s>"]
            )
            reply = output["choices"][0]["message"]["content"]

            # Show debug template
            if debug_callback:
                formatted_debug = ""
                for m in messages:
                    if m["role"] == "user":
                        formatted_debug += m["content"] + " [/INST]\n"
                    elif m["role"] == "assistant":
                        formatted_debug += m["content"] + "</s>\n"
                debug_callback(formatted_debug)

            return reply
        except Exception as e:
            return f"[{self.assistant_name}] Error: {e}"
