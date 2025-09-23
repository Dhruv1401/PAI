from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from plugins.chat_bubbles import ChatBubble, ThinkingBubble
from plugins.animated_panel import AnimatedPanel
import numpy as np
import pyqtgraph as pg

class ChatGUI(QWidget):
    def __init__(self, brain, memory, voice_plugin, face_plugin):
        super().__init__()
        self.brain = brain
        self.memory = memory
        self.voice_plugin = voice_plugin
        self.face_plugin = face_plugin

        self.setWindowTitle("PAI Chat")
        self.resize(1000, 600)

        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        self.side_panel = AnimatedPanel()
        main_layout.addWidget(self.side_panel)

        # Chat + waveform
        right_layout = QVBoxLayout()
        self.chat_area_layout = QVBoxLayout()
        chat_widget = QWidget()
        chat_widget.setLayout(self.chat_area_layout)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(chat_widget)
        right_layout.addWidget(self.scroll, 3)

        # Waveform
        self.waveform = pg.PlotWidget()
        self.waveform.setYRange(-1,1)
        self.waveform.hideAxis('bottom')
        self.waveform.hideAxis('left')
        right_layout.addWidget(self.waveform, 1)

        # Input
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        right_layout.addLayout(input_layout)

        main_layout.addLayout(right_layout, 3)

        self.send_button.clicked.connect(self.handle_input)
        self.input_line.returnPressed.connect(self.handle_input)

        # Connect plugins
        self.voice_plugin.speech_received.connect(self.handle_voice)
        self.face_plugin.frame_updated.connect(self.update_frame)

        self.face_label = QLabel()
        right_layout.addWidget(self.face_label)

    def handle_input(self):
        text = self.input_line.text().strip()
        if not text:
            return
        self.add_chat(text, sender="user")
        self.input_line.clear()

        thinking = ThinkingBubble()
        self.chat_area_layout.addWidget(thinking)

        self.brain.generate_response(text, callback=lambda response: self.show_response(response, thinking))

    def handle_voice(self, text):
        self.add_chat(text, sender="user")
        thinking = ThinkingBubble()
        self.chat_area_layout.addWidget(thinking)
        self.brain.generate_response(text, callback=lambda r: self.show_response(r, thinking))

    def show_response(self, response, thinking):
        self.chat_area_layout.removeWidget(thinking)
        thinking.deleteLater()
        self.add_chat(response, sender="assistant")
        self.memory.save_message("assistant", response)
        self.voice_plugin.speak(response)

    def add_chat(self, text, sender):
        bubble = ChatBubble(text, sender)
        self.chat_area_layout.addWidget(bubble)

    def update_frame(self, frame):
        # Convert OpenCV frame to QImage
        import cv2
        from PySide6.QtGui import QImage, QPixmap
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qimg = QImage(rgb_image.data, w, h, ch*w, QImage.Format_RGB888)
        self.face_label.setPixmap(QPixmap.fromImage(qimg))
