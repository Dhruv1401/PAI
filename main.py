import sys
import os
import threading
import json
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QTabWidget, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
import itertools
import pyttsx3
import pyaudio
import vosk
from llama_cpp import Llama

WAKE_WORD = "tara"
END_WORD = "over"

class WorkerSignals(QObject):
    log = Signal(str)
    response = Signal(str)
    partial_response = Signal(str)
    error = Signal(str)
    typing = Signal(bool)

class VoiceAssistantWorker(threading.Thread):
    def __init__(self, signals, model_path, vosk_model_path):
        super().__init__(daemon=True)
        self.signals = signals
        self.model_path = model_path
        self.vosk_model_path = vosk_model_path
        self.running = True
        self.conversation_history = []
        self.cache = {}  # Cache for input -> response
        self.engine = pyttsx3.init()
        self.load_model()
        self.load_vosk_model()
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.rec = None

    def load_model(self):
        self.signals.log.emit(f"Loading model from {self.model_path} ...")
        self.llm = Llama(model_path=self.model_path, n_ctx=1024, n_threads=2)  # Optimized for RPi4 2GB RAM
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
            self.signals.log.emit("Listening for wake word 'tara'...")
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
                            self.signals.typing.emit(True)
                            response = self.process_command(command)
                            self.signals.typing.emit(False)
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
            # Check cache first
            if command in self.cache:
                self.signals.log.emit(f"Cache hit for command: {command}")
                return self.cache[command]

            # Append user message as tuple
            self.conversation_history.append(("user", command))
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Build prompt with proper formatting
            prompt = ""
            for role, content in self.conversation_history:
                if role == "user":
                    prompt += f"[INST] {content} [/INST]"
                elif role == "assistant":
                    prompt += f"{content}</s>"

            output = self.llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
            response = output['choices'][0]['text'].strip()

            # Append assistant response as tuple
            self.conversation_history.append(("assistant", response))

            self.signals.log.emit(f"Response: {response}")
            self.cache[command] = response  # Cache the response
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

class CommandProcessorThread(threading.Thread):
    def __init__(self, worker, command, signals):
        super().__init__(daemon=True)
        self.worker = worker
        self.command = command
        self.signals = signals

    def run(self):
        import time
        import threading
        self.signals.typing.emit(True)
        full_response = self.worker.process_command(self.command)

        # Run speech synthesis in a separate thread to allow simultaneous speaking and streaming
        def speak_async(text):
            self.worker.speak(text)

        speak_thread = threading.Thread(target=speak_async, args=(full_response,), daemon=True)
        speak_thread.start()

        # Simulate streaming by emitting partial responses word by word
        words = full_response.split()
        partial = ""
        for word in words:
            if partial:
                partial += " "
            partial += word
            self.signals.partial_response.emit(partial)
            time.sleep(0.2)  # small delay to simulate streaming word by word
        self.signals.typing.emit(False)
        # Remove emitting full response again to avoid duplicate message
        # self.signals.response.emit(full_response)

class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TARA")
        self.setGeometry(100, 100, 1100, 700)
        self.setMinimumSize(600, 400)

        self.typing_label = QLabel("")  # Initialize early to avoid NoneType errors

        self.dark_theme = True
        self.apply_theme()

        # Typing animation setup
        self.typing_animation_timer = QTimer()
        self.typing_animation_timer.setInterval(500)  # 500 ms interval
        self.typing_animation_timer.timeout.connect(self.update_typing_animation)
        self.typing_animation_iterator = itertools.cycle([
            "TARA is typing",
            "TARA is typing.",
            "TARA is typing..",
            "TARA is typing..."
        ])

        # Improve typing label style for readability
        self.typing_label.setStyleSheet("font-style: italic; color: #00ffff; font-size: 16pt; padding: 5px;")

        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.response.connect(self.append_response)
        self.signals.partial_response.connect(self.append_partial_response)
        self.signals.error.connect(self.append_log)
        self.signals.typing.connect(self.show_typing)

        self.init_ui()

        model_path = "mistral-7b-instruct-v0.2.Q3_K_L.gguf"  # Lightweight model for RPi4 2GB RAM
        vosk_model_path = "vosk-model-small-en-us-0.15"

        self.worker = VoiceAssistantWorker(self.signals, model_path, vosk_model_path)
        self.worker.start()

        # Display previous conversation history in the chat GUI
        self.load_conversation_history()

    def apply_theme(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QWidget { background: #0f1115; color: #e6eef2; }
                QLineEdit, QTextEdit { background: #121419; border-radius: 10px; padding: 8px; color: #e6eef2; }
                QPushButton { background: #00d1a1; color: #04201b; border-radius: 10px; padding: 10px; }
                QPushButton:hover { background: #00b388; }
                QTabWidget::pane { background: #121419; border-radius: 12px; }
                QTabBar::tab { background: transparent; color: #9aa3ad; padding: 8px; border-radius: 8px; }
                QTabBar::tab:selected { background: #1a9b8f; color: #00d1a1; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background: #f7f9fb; color: #222; }
                QLineEdit, QTextEdit { background: #fff; border-radius: 10px; padding: 8px; color: #222; }
                QPushButton { background: #00796b; color: white; border-radius: 10px; padding: 10px; }
                QPushButton:hover { background: #004d40; }
                QTabWidget::pane { background: #fff; border-radius: 12px; }
                QTabBar::tab { background: transparent; color: #607d8b; padding: 8px; border-radius: 8px; }
                QTabBar::tab:selected { background: #00796b; color: #fff; }
            """)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        brand_layout = QHBoxLayout()
        logo = QLabel("T")
        logo.setFixedSize(48, 48)
        logo.setStyleSheet("background: linear-gradient(135deg,#053241,#02393a); color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo)
        title_layout = QVBoxLayout()
        title = QLabel("TARA")
        title.setStyleSheet("font-weight: 700;")
        subtitle = QLabel("Powered by Local LLM")
        subtitle.setStyleSheet("color: #9aa3ad; font-size: 12px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        brand_layout.addLayout(title_layout)
        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        self.theme_toggle_btn = QPushButton("Light")
        self.theme_toggle_btn.setFixedWidth(60)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle_btn)
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

        # Typing animation label
        self.typing_label = QLabel("")
        self.typing_label.setStyleSheet("font-style: italic; color: #9aa3ad; padding: 5px;")
        chat_layout.addWidget(self.typing_label)

        # Bot loading animation label
        self.bot_loading_label = QLabel("")
        self.bot_loading_label.setStyleSheet("font-style: italic; color: #00ffff; font-size: 14pt; padding: 5px;")
        chat_layout.addWidget(self.bot_loading_label)

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
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        self.theme_label = QLabel("Theme:")
        settings_layout.addWidget(self.theme_label)
        self.theme_light_btn = QPushButton("Light")
        self.theme_dark_btn = QPushButton("Dark")
        self.theme_light_btn.clicked.connect(self.set_light_theme)
        self.theme_dark_btn.clicked.connect(self.set_dark_theme)
        settings_layout.addWidget(self.theme_light_btn)
        settings_layout.addWidget(self.theme_dark_btn)
        self.side_tabs.addTab(self.log_tab, "Log")
        self.side_tabs.addTab(self.settings_tab, "Settings")
        side_layout.addWidget(self.side_tabs)
        main_splitter.addWidget(side_widget)
        main_splitter.setStretchFactor(1, 1)

    def set_light_theme(self):
        self.dark_theme = False
        self.apply_theme()

    def set_dark_theme(self):
        self.dark_theme = True
        self.apply_theme()

    def append_message(self, text, msg_type):
        msg = QLabel(text)
        msg.setWordWrap(True)
        font = msg.font()
        font.setPointSize(14)  # Increase font size
        msg.setFont(font)
        if msg_type == 'user':
            msg.setStyleSheet("background: linear-gradient(90deg,#0b6ff7,#1a9bff); color: white; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
        else:
            if self.dark_theme:
                # Different color for dark mode bot messages, text color white
                msg.setStyleSheet("background: linear-gradient(90deg,#ff9f43,#ff6f00); color: white; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
            else:
                # Light mode bot messages, text color black
                msg.setStyleSheet("background: linear-gradient(90deg,#0fffd0,#70f2c3); color: black; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
        self.messages_layout.addWidget(msg)
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def append_log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_tab.append(f"{timestamp} {text}")

    def append_response(self, text):
        self.append_message(text, 'bot')

    def append_partial_response(self, text):
        # Append or update the last bot message with partial text and blinking cursor
        if self.messages_layout.count() == 0:
            self.append_message(text + " |", 'bot')
        else:
            last_msg = self.messages_layout.itemAt(self.messages_layout.count() - 1).widget()
            if last_msg:
                last_msg.setText(text + " |")
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def load_conversation_history(self):
        # Display previous conversation history in the chat GUI
        for msg in self.worker.conversation_history:
            # Filter out empty or control tokens
            if msg.strip() and not msg.startswith("[INST]") and not msg.endswith("[/INST]"):
                self.append_message(msg, 'bot')

    def show_typing(self, is_typing):
        try:
            if self.typing_label is not None:
                if is_typing:
                    self.typing_animation_timer.start()
                    self.bot_loading_label.setText("Loading...")
                else:
                    self.typing_animation_timer.stop()
                    self.typing_label.setText("")
                    self.bot_loading_label.setText("")
                    # Remove blinking cursor from last bot message
                    if self.messages_layout.count() > 0:
                        last_msg = self.messages_layout.itemAt(self.messages_layout.count() - 1).widget()
                        if last_msg:
                            text = last_msg.text()
                            if text.endswith(" |"):
                                last_msg.setText(text[:-2])
        except Exception as e:
            self.append_log(f"Error in show_typing: {str(e)}")

    def send_message(self):
        text = self.message_input.text().strip()
        if text:
            self.append_message(text, 'user')
            self.message_input.clear()
            # Run command processing in a separate thread
            thread = CommandProcessorThread(self.worker, text, self.signals)
            thread.start()

    def update_typing_animation(self):
        next_text = next(self.typing_animation_iterator)
        self.typing_label.setText(next_text)

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec())
