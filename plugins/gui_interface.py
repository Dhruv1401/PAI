from PyQt5 import QtWidgets, QtCore, QtGui
import sys

class ChatWindow(QtWidgets.QWidget):
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Jarvis Assistant")
        self.setGeometry(200, 200, 900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #333;
                border-radius: 5px;
                background-color: #1f1f1f;
                color: white;
            }
            QTextEdit {
                border: none;
                background-color: #181818;
                padding: 10px;
                border-radius: 8px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        # Title Bar
        title = QtWidgets.QLabel("🧠 Jarvis AI Assistant")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4FC3F7; margin: 10px;")
        layout.addWidget(title)

        # Horizontal Split
        main_split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Chat Panel
        chat_panel = QtWidgets.QWidget()
        chat_layout = QtWidgets.QVBoxLayout(chat_panel)

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("color: #BBDEFB;")
        chat_layout.addWidget(self.chat)

        self.input = QtWidgets.QLineEdit()
        self.input.returnPressed.connect(self.send_message)
        chat_layout.addWidget(self.input)

        main_split.addWidget(chat_panel)

        # Debug Panel
        debug_panel = QtWidgets.QWidget()
        debug_layout = QtWidgets.QVBoxLayout(debug_panel)

        debug_label = QtWidgets.QLabel("🔧 Debug Logs")
        debug_label.setStyleSheet("color: #81C784; font-weight: bold;")
        debug_layout.addWidget(debug_label)

        self.debug = QtWidgets.QTextEdit()
        self.debug.setReadOnly(True)
        self.debug.setStyleSheet("color: #A5D6A7;")
        debug_layout.addWidget(self.debug)

        main_split.addWidget(debug_panel)
        layout.addWidget(main_split)

    def send_message(self):
        text = self.input.text()
        self.input.clear()
        self.chat.append(f"<b style='color:white;'>You:</b> {text}")
        self.debug.append(f"[User Input] {text}")

        response = self.brain.process_input(text)

        self.chat.append(f"<b style='color:#4FC3F7;'>Jarvis:</b> {response}<br>")
        self.debug.append(f"[Jarvis Output] {response}")

class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        window = ChatWindow(self.brain)
        window.show()
        sys.exit(app.exec_())
