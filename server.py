import os
from flask import Flask, request, jsonify
from llama_cpp import Llama

app = Flask(__name__)

# Load model once at startup
MODEL_PATH = "mistral-7b-instruct-v0.2.Q3_K_L.gguf"
print(f"Loading model from {MODEL_PATH}...")
llm = Llama(model_path=MODEL_PATH, n_ctx=1024, n_threads=4)
print("Model loaded successfully.")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        user_input = data.get("input", "")
        history = data.get("history", [])

        # Build prompt from history
        prompt = ""
        for role, content in history:
            if role == "user":
                prompt += f"[INST] {content} [/INST]"
            elif role == "assistant":
                prompt += f"{content}</s>"

        # Add current input
        prompt += f"[INST] {user_input} [/INST]"

        output = llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
        response = output['choices'][0]['text'].strip()

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, threaded=True)

