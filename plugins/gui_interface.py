from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class Plugin(QtWidgets.QWidget):
    def __init__(self, brain, config):
        super().__init__()
        self.brain = brain
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Jarvis Assistant")
        self.setGeometry(200, 200, 700, 500)
        self.setStyleSheet("background-color: #1e1e2f; color: white; font-family: 'Consolas';")

        layout = QtWidgets.QVBoxLayout()

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background-color: #252539; padding: 10px; border-radius: 10px; font-size: 14px;")
        layout.addWidget(self.chat)

        self.input = QtWidgets.QLineEdit()
        self.input.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #2e2e44; font-size: 14px;")
        self.input.returnPressed.connect(self.send_message)
        layout.addWidget(self.input)

        self.setLayout(layout)
        self.show()

    def send_message(self):
        text = self.input.text()
        self.input.clear()
        self.chat.append(f"<b>You:</b> {text}")
        response = self.brain.process_input(text)
        self.chat.append(f"<span style='color:#77dd77;'><b>Jarvis:</b> {response}</span><br>")

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        self.show()
        sys.exit(app.exec_())
