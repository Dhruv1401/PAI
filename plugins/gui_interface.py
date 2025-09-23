from PyQt5 import QtWidgets, QtGui, QtCore

class Plugin(QtWidgets.QWidget):
    def __init__(self, config, brain, scripted, debug_logger=None):
        super().__init__()
        self.config = config
        self.brain = brain
        self.scripted = scripted
        self.debug_logger = debug_logger
        self.assistant_name = config.get("assistant_name", "Assistant")

        self.setWindowTitle(f"{self.assistant_name} - AI Assistant")
        self.setGeometry(200, 200, 800, 600)

        # --- Layout ---
        layout = QtWidgets.QVBoxLayout()

        # Chat display
        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font: 12pt Consolas;")
        layout.addWidget(self.chat_display)

        # Input + Send
        input_layout = QtWidgets.QHBoxLayout()
        self.input_box = QtWidgets.QLineEdit()
        self.input_box.setStyleSheet("padding: 8px; font: 11pt Arial;")
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 6px;")
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Debug panel
        self.debug_display = QtWidgets.QTextEdit()
        self.debug_display.setReadOnly(True)
        self.debug_display.setStyleSheet("background-color: #2d2d2d; color: #9cdcfe; font: 10pt Consolas;")
        layout.addWidget(QtWidgets.QLabel("Debug Output:"))
        layout.addWidget(self.debug_display)

        # Face recognition status
        self.face_status = QtWidgets.QLabel("Face Recognition: Not Running")
        self.face_status.setStyleSheet("color: #ffcc00; font: 10pt Arial;")
        layout.addWidget(self.face_status)

        self.setLayout(layout)
        self.send_button.clicked.connect(self.handle_send)

    def handle_send(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        self.chat_display.append(f"<b>You:</b> {user_text}")
        self.input_box.clear()

        # Check scripted responses
        if self.scripted and self.scripted.can_handle(user_text):
            reply = self.scripted.handle(user_text)
        else:
            reply = self.brain.process([{"role": "user", "content": user_text}], self.log_debug)

        self.chat_display.append(f"<b>{self.assistant_name}:</b> {reply}")

    def log_debug(self, text):
        self.debug_display.append(text)

    def update_face_status(self, status):
        self.face_status.setText(f"Face Recognition: {status}")
