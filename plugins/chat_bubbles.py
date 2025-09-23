from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

class ChatBubble(QLabel):
    def __init__(self, text, sender="assistant"):
        super().__init__()
        self.setText(text)
        self.setWordWrap(True)
        self.setFont(QFont("Arial", 12))
        self.sender = sender

        if sender == "user":
            bg_color = "#4fc3f7"
            text_color = "#000000"
            alignment = Qt.AlignRight
        else:
            bg_color = "#323232"
            text_color = "#ffffff"
            alignment = Qt.AlignLeft

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 12px;
                padding: 8px;
                margin: 5px;
            }}
        """)
        self.setAlignment(alignment)


class ThinkingBubble(QLabel):
    def __init__(self):
        super().__init__("...")
        self.setStyleSheet("""
            QLabel {
                background-color: #444444;
                color: white;
                border-radius: 12px;
                padding: 8px;
                margin: 5px;
            }
        """)
        self.dots = 1
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)

    def animate(self):
        self.dots = (self.dots % 3) + 1
        self.setText("." * self.dots)
