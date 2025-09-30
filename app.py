import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import pyaudio
import vosk
import pyttsx3
from llama_cpp import Llama
import struct
import os
import json
import requests
import zipfile

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Conversation history for memory
conversation_history = []

# Load LLM
model_path = "models/mistral-7b-instruct-v0.2.Q3_K_L.gguf"
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)  # Adjust threads for Pi4

# TTS
engine = pyttsx3.init()

# Load Vosk model (download vosk-model-small-en-us-0.15 and place in models/)
vosk_model_path = "models/vosk-model-small-en-us-0.15"
if not os.path.exists(vosk_model_path):
    print("Vosk model not found. Downloading...")
    url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = "models/vosk-model-small-en-us-0.15.zip"
    os.makedirs("models", exist_ok=True)
    response = requests.get(url, stream=True)
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("models")
    os.remove(zip_path)
    print("Vosk model downloaded.")
vosk_model = vosk.Model(vosk_model_path)

# Voice handling
def voice_loop():
    if not vosk_model:
        print("Vosk model not loaded, voice disabled")
        return

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=16000,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=8000
    )

    rec = vosk.KaldiRecognizer(vosk_model, 16000)
    print("Listening for wake word 'hey computer'...")

    listening_for_command = False
    command_audio = b""

    while True:
        try:
            data = stream.read(4000)
        except OSError as e:
            print(f"Audio input overflow: {e}")
            continue
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get('text', '').strip().lower()
            if 'hey computer' in text:
                print("Wake word detected!")
                socketio.emit('log', "Wake word detected!")
                listening_for_command = True
                command_audio = b""
            elif listening_for_command:
                command = text.replace("hey computer", "").strip()
                if command:
                    print(f"Command: {command}")
                    socketio.emit('log', f"Command: {command}")
                    if command == "over":
                        print("Conversation ended by user.")
                        socketio.emit('log', "Conversation ended by user.")
                        listening_for_command = False
                        conversation_history.clear()
                        continue
                    # Send to LLM
                    try:
                        conversation_history.append(f"[INST] {command} [/INST]")
                        if len(conversation_history) > 20:
                            conversation_history[:] = conversation_history[-20:]
                        prompt = "".join(conversation_history)
                        output = llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
                        response = output['choices'][0]['text'].strip()
                        conversation_history.append(response + "</s>")
                        print(f"Response: {response}")
                        # TTS
                        engine.say(response)
                        engine.runAndWait()
                        # Send to GUI
                        socketio.emit('response', {'text': response, 'type': 'voice'})
                    except Exception as e:
                        print(f"Error: {str(e)}")
                listening_for_command = False
        else:
            partial = json.loads(rec.PartialResult())
            partial_text = partial.get('partial', '').strip().lower()
            if 'hey computer' in partial_text and not listening_for_command:
                print("Wake word detected in partial!")
                listening_for_command = True
                command_audio = b""

# Start voice thread
threading.Thread(target=voice_loop, daemon=True).start()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@socketio.on('message')
def handle_message(data):
    text = data['text']
    print(f"Text input: {text}")
    socketio.emit('log', f"Text input: {text}")
    try:
        conversation_history.append(f"[INST] {text} [/INST]")
        if len(conversation_history) > 20:
            conversation_history[:] = conversation_history[-20:]
        prompt = "".join(conversation_history)
        output = llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
        response = output['choices'][0]['text'].strip()
        conversation_history.append(response + "</s>")
        print(f"Response: {response}")
    except Exception as e:
        response = f"Error generating response: {str(e)}"
        print(response)
    emit('response', {'text': response, 'type': 'text'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
