from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

class AnimatedPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Plugins")
        self.label.setFont(QFont("Arial", 14, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.colors = ["#4fc3f7", "#81c784", "#fbc02d", "#e57373"]
        self.idx = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)

    def animate(self):
        self.status_label.setStyleSheet(f"background-color: {self.colors[self.idx]}; color: white; padding: 5px;")
        self.idx = (self.idx + 1) % len(self.colors)

    def set_status(self, text):
        self.status_label.setText(text)
