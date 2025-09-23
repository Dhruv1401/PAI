from PyQt5 import QtWidgets, QtCore
from plugins.face_recognition import FaceRecognition

class Plugin(QtWidgets.QWidget):
    def __init__(self, config, brain, scripted, memory, debug_logger=None):
        super().__init__()
        self.config = config
        self.brain = brain
        self.scripted = scripted
        self.memory = memory
        self.debug_logger = debug_logger
        self.assistant_name = config.get("assistant_name", "Assistant")

        self.setWindowTitle(f"{self.assistant_name} - AI Assistant")
        self.resize(1000, 700)

        # --- Layout ---
        layout = QtWidgets.QVBoxLayout(self)

        # Chat Display
        self.chat_display = QtWidgets.QTextEdit(readOnly=True)
        self.chat_display.setStyleSheet("background-color:#1e1e1e;color:#dcdcdc;font:12pt Consolas;")
        layout.addWidget(self.chat_display)

        # Input Row
        input_layout = QtWidgets.QHBoxLayout()
        self.input_box = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton("Send")
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Face Recognition Feed
        self.face_widget = FaceRecognition(config)
        self.face_widget.setFixedHeight(250)
        layout.addWidget(QtWidgets.QLabel("Face Recognition Feed:"))
        layout.addWidget(self.face_widget)

        # Debug Output
        self.debug_display = QtWidgets.QTextEdit(readOnly=True)
        self.debug_display.setStyleSheet("background-color:#2d2d2d;color:#9cdcfe;font:10pt Consolas;")
        layout.addWidget(QtWidgets.QLabel("Debug Output:"))
        layout.addWidget(self.debug_display)

        self.send_button.clicked.connect(self.handle_send)

    def handle_send(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        self.chat_display.append(f"<b>You:</b> {user_text}")
        self.input_box.clear()
        self.memory.add("user", user_text)

        # Run async so GUI doesn’t freeze
        QtCore.QTimer.singleShot(50, lambda: self.get_reply(user_text))

    def get_reply(self, user_text):
        if self.scripted and self.scripted.can_handle(user_text):
            reply = self.scripted.handle(user_text)
        else:
            reply = self.brain.process(self.memory.chat_log, self.log_debug)

        self.chat_display.append(f"<b>{self.assistant_name}:</b> {reply}")
        self.memory.add("assistant", reply)

    def log_debug(self, text):
        self.debug_display.append(text)
