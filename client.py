import sys
import os
import threading
import json
import requests
from datetime import datetime

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget, QScrollArea, QSplitter
from PySide6.QtCore import Qt, Signal, QObject, QTimer
import itertools
import pyttsx3
import pyaudio
import vosk

WAKE_WORD = "hey"
END_WORD = "over"
HOST_URL = "http://192.168.1.15:5005/generate"  # Change to your server IP

# ---------------- SIGNALS ----------------
class WorkerSignals(QObject):
    log = Signal(str)
    response = Signal(str)
    partial_response = Signal(str)
    error = Signal(str)
    typing = Signal(bool)
    connection = Signal(str)  # Signal for connection logs

# ---------------- VOICE ASSISTANT WORKER ----------------
class VoiceAssistantWorker(threading.Thread):
    def __init__(self, signals, vosk_model_path):
        super().__init__(daemon=True)
        self.signals = signals
        self.vosk_model_path = vosk_model_path
        self.running = True
        self.conversation_history = []
        self.cache = {}  
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        self.tts_lock = threading.Lock()
        self.load_vosk_model()
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.rec = None

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
            self.signals.log.emit(f"Listening for wake word '{WAKE_WORD}'...")
            listening_for_command = False

            while self.running:
                data = self.stream.read(4000, exception_on_overflow=False)
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
            if command in self.cache:
                return self.cache[command]

            try:
                self.signals.connection.emit(f"Sending command to host: {command}")
                response = requests.post(HOST_URL, json={
                    "input": command,
                    "history": self.conversation_history
                }, timeout=30)
                self.signals.connection.emit("Host responded successfully. Connection OK")
            except Exception as e:
                self.signals.connection.emit(f"Connection failed: {str(e)}")
                return f"Connection failed: {str(e)}"

            data = response.json()
            if "response" in data:
                reply = data["response"]
                self.conversation_history.append(("user", command))
                self.conversation_history.append(("assistant", reply))
                self.cache[command] = reply
                return reply
            else:
                return f"Error: {data.get('error','Unknown error')}"
        except Exception as e:
            return f"Host request failed: {str(e)}"

    def speak(self, text):
        with self.tts_lock:
            self.engine.say(text)
            self.engine.runAndWait()

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

# ---------------- COMMAND PROCESSOR THREAD ----------------
class CommandProcessorThread(threading.Thread):
    def __init__(self, worker, command, signals):
        super().__init__(daemon=True)
        self.worker = worker
        self.command = command
        self.signals = signals

    def run(self):
        import time
        self.signals.typing.emit(True)
        full_response = None

        def request_server():
            nonlocal full_response
            full_response = self.worker.process_command(self.command)

        request_thread = threading.Thread(target=request_server, daemon=True)
        request_thread.start()

        while request_thread.is_alive():
            self.signals.partial_response.emit("Waiting for server response...")
            time.sleep(0.5)

        self.signals.typing.emit(False)

        if full_response:
            self.signals.partial_response.emit("")
            self.signals.response.emit(full_response)
            threading.Thread(target=self.worker.speak, args=(full_response,), daemon=True).start()

# ---------------- GUI ----------------
class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TARA")
        self.setGeometry(100, 100, 1100, 700)
        self.setMinimumSize(600, 400)

        self.typing_label = QLabel("")
        self.dark_theme = True
        self.apply_theme()

        self.typing_animation_timer = QTimer()
        self.typing_animation_timer.setInterval(500)
        self.typing_animation_timer.timeout.connect(self.update_typing_animation)
        self.typing_animation_iterator = itertools.cycle([
            "TARA is typing",
            "TARA is typing.",
            "TARA is typing..",
            "TARA is typing..."
        ])
        self.typing_label.setStyleSheet("font-style: italic; color: #00ffff; font-size: 16pt; padding: 5px;")

        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.response.connect(self.append_response)
        self.signals.partial_response.connect(self.append_partial_response)
        self.signals.error.connect(self.append_log)
        self.signals.typing.connect(self.show_typing)
        self.signals.connection.connect(self.append_connection_log)

        self.init_ui()
        vosk_model_path = "vosk-model-small-en-us-0.15"
        self.worker = VoiceAssistantWorker(self.signals, vosk_model_path)
        self.worker.start()
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

        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_scroll.setWidget(self.messages_container)
        chat_layout.addWidget(self.messages_scroll)

        self.typing_label = QLabel("")
        self.typing_label.setStyleSheet("font-style: italic; color: #9aa3ad; padding: 5px;")
        chat_layout.addWidget(self.typing_label)

        self.bot_loading_label = QLabel("")
        self.bot_loading_label.setStyleSheet("font-style: italic; color: #00ffff; font-size: 14pt; padding: 5px;")
        chat_layout.addWidget(self.bot_loading_label)

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

        side_widget = QWidget()
        side_layout = QVBoxLayout(side_widget)
        self.side_tabs = QTabWidget()

        self.log_tab = QTextEdit()
        self.log_tab.setReadOnly(True)
        self.connection_tab = QTextEdit()
        self.connection_tab.setReadOnly(True)
        self.connection_tab.append("Connection logs will appear here...")

        self.side_tabs.addTab(self.log_tab, "Log")
        self.side_tabs.addTab(self.connection_tab, "Connection")

        side_layout.addWidget(self.side_tabs)
        main_splitter.addWidget(side_widget)
        main_splitter.setStretchFactor(1, 1)

    def append_message(self, text, msg_type):
        msg = QLabel(text)
        msg.setWordWrap(True)
        font = msg.font()
        font.setPointSize(14)
        msg.setFont(font)
        if msg_type == 'user':
            msg.setStyleSheet("background: linear-gradient(90deg,#0b6ff7,#1a9bff); color: white; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
        else:
            if self.dark_theme:
                msg.setStyleSheet("background: linear-gradient(90deg,#ff9f43,#ff6f00); color: white; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
            else:
                msg.setStyleSheet("background: linear-gradient(90deg,#0fffd0,#70f2c3); color: black; padding: 10px; border-radius: 10px; margin: 5px; font-size: 14pt;")
        self.messages_layout.addWidget(msg)
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def append_log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_tab.append(f"{timestamp} {text}")

    def append_connection_log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.connection_tab.append(f"{timestamp} {text}")

    def append_response(self, text):
        self.append_message(text, 'bot')

    def append_partial_response(self, text):
        if self.messages_layout.count() == 0:
            self.append_message(text + " |", 'bot')
        else:
            last_msg = self.messages_layout.itemAt(self.messages_layout.count() - 1).widget()
            if last_msg:
                last_msg.setText(text + " |")
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def load_conversation_history(self):
        for msg in self.worker.conversation_history:
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
            thread = CommandProcessorThread(self.worker, text, self.signals)
            thread.start()

    def update_typing_animation(self):
        next_text = next(self.typing_animation_iterator)
        self.typing_label.setText(next_text)

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec())
