import sys
import os
import threading
import json
import queue
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QTabWidget, QScrollArea, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
import pyttsx3
import pyaudio
import vosk
from llama_cpp import Llama

WAKE_WORD = "hey computer"
END_WORD = "over"

class WorkerSignals(QObject):
    log = Signal(str)
    response = Signal(str)
    error = Signal(str)

class VoiceAssistantWorker(threading.Thread):
    def __init__(self, signals, model_path, vosk_model_path):
        super().__init__(daemon=True)
        self.signals = signals
        self.model_path = model_path
        self.vosk_model_path = vosk_model_path
        self.running = True
        self.conversation_history = []
        self.engine = pyttsx3.init()
        self.load_model()
        self.load_vosk_model()
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.rec = None

    def load_model(self):
        self.signals.log.emit(f"Loading model from {self.model_path} ...")
        self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=4)
        self.signals.log.emit("Model loaded.")

    def load_vosk_model(self):
        if not os.path.exists(self.vosk_model_path):
            self.signals.log.emit("Vosk model not found. Please download and place it in models/")
            raise FileNotFoundError("Vosk model not found")
        self.vosk_model = vosk.Model(self.vosk_model_path)
        self.signals.log.emit("Vosk model loaded.")

    def run(self):
        try:
            self.stream = self.pa.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=8000
            )
            self.rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            self.signals.log.emit("Listening for wake word 'hey computer'...")
            listening_for_command = False

            while self.running:
                try:
                    data = self.stream.read(4000, exception_on_overflow=False)
                except Exception as e:
                    self.signals.log.emit(f"Audio input error: {e}")
                    continue

                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get('text', '').strip().lower()
                    if WAKE_WORD in text:
                        self.signals.log.emit("Wake word detected!")
                        listening_for_command = True
                    elif listening_for_command:
                        command = text.replace(WAKE_WORD, "").strip()
                        if command:
                            self.signals.log.emit(f"Command: {command}")
                            if command == END_WORD:
                                self.signals.log.emit("Conversation ended by user.")
                                listening_for_command = False
                                self.conversation_history.clear()
                                continue
                            response = self.process_command(command)
                            self.signals.response.emit(response)
                            self.speak(response)
                            listening_for_command = False
                else:
                    partial = json.loads(self.rec.PartialResult())
                    partial_text = partial.get('partial', '').strip().lower()
                    if WAKE_WORD in partial_text and not listening_for_command:
                        self.signals.log.emit("Wake word detected in partial!")
                        listening_for_command = True
        except Exception as e:
            self.signals.error.emit(str(e))

    def process_command(self, command):
        try:
            self.conversation_history.append(f"[INST] {command} [/INST]")
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            prompt = "".join(self.conversation_history)
            output = self.llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
            response = output['choices'][0]['text'].strip()
            self.conversation_history.append(response + "</s>")
            self.signals.log.emit(f"Response: {response}")
            return response
        except Exception as e:
            self.signals.error.emit(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant")
        self.setGeometry(100, 100, 1100, 700)

        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.response.connect(self.append_response)
        self.signals.error.connect(self.append_log)

        self.init_ui()

        model_path = "models/mistral-7b-instruct-v0.2.Q3_K_L.gguf"
        vosk_model_path = "models/vosk-model-small-en-us-0.15"

        self.worker = VoiceAssistantWorker(self.signals, model_path, vosk_model_path)
        self.worker.start()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        brand_layout = QHBoxLayout()
        logo = QLabel("A")
        logo.setFixedSize(48, 48)
        logo.setStyleSheet("background: #053241; color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo)
        title_layout = QVBoxLayout()
        title = QLabel("Assistant")
        title.setStyleSheet("font-weight: bold;")
        subtitle = QLabel("Powered by Local LLM")
        subtitle.setStyleSheet("color: gray; font-size: 12px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        brand_layout.addLayout(title_layout)
        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main content
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Chat panel
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_scroll.setWidget(self.messages_container)
        chat_layout.addWidget(self.messages_scroll)

        # Input row
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)

        main_splitter.addWidget(chat_widget)
        main_splitter.setStretchFactor(0, 2)

        # Side panel
        side_widget = QWidget()
        side_layout = QVBoxLayout(side_widget)
        self.side_tabs = QTabWidget()
        self.log_tab = QTextEdit()
        self.log_tab.setReadOnly(True)
        self.settings_tab = QLabel("Settings panel - Coming soon")
        self.side_tabs.addTab(self.log_tab, "Log")
        self.side_tabs.addTab(self.settings_tab, "Settings")
        side_layout.addWidget(self.side_tabs)
        main_splitter.addWidget(side_widget)
        main_splitter.setStretchFactor(1, 1)

    def append_message(self, text, msg_type):
        msg = QLabel(text)
        msg.setWordWrap(True)
        if msg_type == 'user':
            msg.setStyleSheet("background: #0b6ff7; color: white; padding: 10px; border-radius: 10px;")
        else:
            msg.setStyleSheet("background: #0fffd0; color: #002419; padding: 10px; border-radius: 10px;")
        self.messages_layout.addWidget(msg)
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def append_log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_tab.append(f"{timestamp} {text}")

    def append_response(self, text):
        self.append_message(text, 'bot')
        # Speak response
        self.worker.speak(text)

    def send_message(self):
        text = self.message_input.text().strip()
        if text:
            self.append_message(text, 'user')
            response = self.worker.process_command(text)
            self.append_response(response)
            self.message_input.clear()

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec())
