import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QTabWidget, QScrollArea, QFrame, QSplitter,
    QStyleFactory, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QClipboard, QPalette, QColor
import speech_recognition as sr
from datetime import datetime
from tts import tts
from client import SocketIOClient

class SpeechRecognitionThread(QThread):
    result_received = Signal(str)
    error_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False

    def run(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio)
                    self.result_received.emit(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.error_received.emit("Could not understand audio")
                except sr.RequestError as e:
                    self.error_received.emit(f"Could not request results; {e}")
                except Exception as e:
                    self.error_received.emit(str(e))

    def start_listening(self):
        self.listening = True
        self.start()

    def stop_listening(self):
        self.listening = False

class MessageWidget(QFrame):
    def __init__(self, text, msg_type, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.text_label)

        bottom_layout = QHBoxLayout()
        timestamp = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp.setStyleSheet("color: gray; font-size: 10px;")
        bottom_layout.addWidget(timestamp)
        bottom_layout.addStretch()

        if msg_type == 'bot':
            copy_btn = QPushButton("📋")
            copy_btn.setFixedSize(20, 20)
            copy_btn.clicked.connect(lambda: self.copy_text(text))
            bottom_layout.addWidget(copy_btn)

        layout.addLayout(bottom_layout)

        if msg_type == 'user':
            self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0b6ff7, stop:1 #1a9bff); color: white; border-radius: 10px;")
        elif msg_type == 'bot':
            self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0fffd0, stop:1 #70f2c3); color: #002419; border-radius: 10px;")
        else:
            self.setStyleSheet("background: rgba(255,255,255,0.03); color: gray; font-style: italic; border-radius: 10px;")

    def copy_text(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # Visual feedback
        self.sender().setText("✅")
        QTimer.singleShot(1000, lambda: self.sender().setText("📋"))

class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant")
        self.setGeometry(100, 100, 1100, 700)
        self.dark_theme = True
        self.apply_theme()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        brand_layout = QHBoxLayout()
        logo = QLabel("A")
        logo.setFixedSize(48, 48)
        logo.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #053241, stop:1 #02393a); color: white; font-size: 24px; font-weight: bold; border-radius: 10px;")
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
        self.theme_btn = QPushButton("Light")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
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
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.clicked.connect(self.toggle_mic)
        input_layout.addWidget(self.mic_btn)
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

        # SocketIO client
        self.client = SocketIOClient()
        self.client.log_received.connect(self.append_log)
        self.client.response_received.connect(self.append_response)
        self.client.connected.connect(lambda: self.append_log("Connected to server"))
        self.client.disconnected.connect(lambda: self.append_log("Disconnected from server"))
        self.client.start()

        # Speech recognition
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.result_received.connect(self.on_speech_result)
        self.speech_thread.error_received.connect(self.on_speech_error)
        self.mic_active = False

    def apply_theme(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QWidget { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #071019, stop:1 #08121a); color: #e6eef2; }
                QLineEdit, QTextEdit { background: rgba(255,255,255,0.03); border: none; border-radius: 10px; padding: 5px; }
                QPushButton { background: #00d1a1; color: #04201b; border: none; border-radius: 10px; padding: 10px; }
                QPushButton:hover { background: #00b388; }
                QTabWidget::pane { border: none; background: rgba(255,255,255,0.02); border-radius: 10px; }
                QTabBar::tab { background: rgba(255,255,255,0.03); border: none; padding: 8px; border-radius: 8px; margin-right: 5px; }
                QTabBar::tab:selected { background: rgba(0,209,161,0.15); color: #00d1a1; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background: #f7f9fb; color: #222; }
                QLineEdit, QTextEdit { background: rgba(0,0,0,0.03); border: none; border-radius: 10px; padding: 5px; }
                QPushButton { background: #00796b; color: white; border: none; border-radius: 10px; padding: 10px; }
                QPushButton:hover { background: #004d40; }
                QTabWidget::pane { border: none; background: white; border-radius: 10px; }
                QTabBar::tab { background: rgba(0,0,0,0.03); border: none; padding: 8px; border-radius: 8px; margin-right: 5px; }
                QTabBar::tab:selected { background: rgba(0,121,107,0.15); color: #00796b; }
            """)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.theme_btn.setText("Dark" if self.dark_theme else "Light")
        self.apply_theme()

    def append_message(self, text, msg_type):
        msg_widget = MessageWidget(text, msg_type)
        self.messages_layout.addWidget(msg_widget)
        # Scroll to bottom
        QTimer.singleShot(0, lambda: self.messages_scroll.verticalScrollBar().setValue(self.messages_scroll.verticalScrollBar().maximum()))

    def append_log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_tab.append(f"{timestamp} {text}")

    def append_response(self, response):
        text = response.get('text', '')
        self.append_message(text, 'bot')
        # Speak the response
        tts.speak(text)

    def send_message(self):
        text = self.message_input.text().strip()
        if text:
            self.append_message(text, 'user')
            self.client.send_message(text)
            self.message_input.clear()

    def toggle_mic(self):
        if not self.mic_active:
            self.mic_active = True
            self.mic_btn.setStyleSheet("background: #142026; box-shadow: 0 0 24px #00d1a1;")
            self.speech_thread.start_listening()
        else:
            self.mic_active = False
            self.mic_btn.setStyleSheet("")
            self.speech_thread.stop_listening()

    def on_speech_result(self, text):
        self.message_input.setText(text)
        self.send_message()

    def on_speech_error(self, error):
        self.append_log(f"Speech error: {error}")
        self.toggle_mic()  # Stop mic on error
