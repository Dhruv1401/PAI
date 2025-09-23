import sys, cv2, threading, os, pickle, time
import numpy as np
import face_recognition
import pyttsx3
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QColor, QFont

class ChatBubble(QLabel):
    def __init__(self, text, sender="user"):
        super().__init__()
        self.setWordWrap(True)
        self.setText(text)
        self.setFont(QFont("Arial", 12))
        self.sender = sender
        if sender == "user":
            self.setStyleSheet("background-color:#0078d7;color:white;padding:8px;border-radius:10px;")
            self.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet("background-color:#4fc3f7;color:black;padding:8px;border-radius:10px;")
            self.setAlignment(Qt.AlignLeft)

class ChatGUI(QWidget):
    def __init__(self, config, brain_callback):
        super().__init__()
        self.config = config
        self.brain_callback = brain_callback
        self.assistant_name = config.get("assistant_name","PAI")
        self.init_tts()
        self.init_ui()
        self.init_camera()
        self.load_known_faces()
        self.wake_animation_active = False

    def init_tts(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 170)

    def init_ui(self):
        self.setWindowTitle(f"{self.assistant_name} Assistant")
        self.resize(1200,800)
        self.setStyleSheet("background-color:#1e1e1e;color:white;")

        main_layout = QHBoxLayout(self)

        # --- Left panel: Chat ---
        chat_layout = QVBoxLayout()
        self.chat_area = QVBoxLayout()
        self.chat_widget = QFrame()
        self.chat_widget.setLayout(self.chat_area)
        self.chat_widget.setStyleSheet("background-color:#2e2e2e; border-radius:10px;")
        chat_layout.addWidget(self.chat_widget)

        # Input
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type here...")
        self.send_btn = QPushButton("Send")
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)
        self.send_btn.clicked.connect(self.send_message)
        self.input_line.returnPressed.connect(self.send_message)

        main_layout.addLayout(chat_layout, 3)

        # --- Right panel: Side panel ---
        side_layout = QVBoxLayout()
        self.face_feed = QLabel()
        self.face_feed.setFixedHeight(300)
        self.face_feed.setStyleSheet("background-color:black;")
        side_layout.addWidget(QLabel("Face Recognition Feed:"))
        side_layout.addWidget(self.face_feed)

        self.wake_label = QLabel("Waiting for wake word...")
        self.wake_label.setAlignment(Qt.AlignCenter)
        self.wake_label.setStyleSheet("color:#ffcc00;font-size:14pt;")
        side_layout.addWidget(self.wake_label)

        self.debug_box = QTextEdit()
        self.debug_box.setReadOnly(True)
        self.debug_box.setStyleSheet("background-color:#2d2d2d;color:#9cdcfe;")
        side_layout.addWidget(QLabel("Debug:"))
        side_layout.addWidget(self.debug_box)
        main_layout.addLayout(side_layout,1)

    # --- Camera + Face Recognition ---
    def init_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def load_known_faces(self):
        self.faces_path = "data/faces"
        os.makedirs(self.faces_path, exist_ok=True)
        self.known_faces = []
        self.known_names = []
        for f in os.listdir(self.faces_path):
            if f.endswith(".pkl"):
                with open(os.path.join(self.faces_path,f),"rb") as file:
                    data = pickle.load(file)
                    self.known_faces.append(data["encoding"])
                    self.known_names.append(data["name"])

    def register_face(self,name):
        ret, frame = self.cap.read()
        if not ret:
            return "Camera error"
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)
        if encodings:
            encoding = encodings[0]
            with open(os.path.join(self.faces_path,f"{name}.pkl"),"wb") as file:
                pickle.dump({"name":name,"encoding":encoding},file)
            self.known_faces.append(encoding)
            self.known_names.append(name)
            return f"Face registered: {name}"
        return "No face detected"

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb,face_locations)
        for (top,right,bottom,left),encoding in zip(face_locations,encodings):
            matches = face_recognition.compare_faces(self.known_faces,encoding)
            name="Unknown"
            if True in matches:
                idx = matches.index(True)
                name = self.known_names[idx]
            cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)
            cv2.putText(frame,name,(left,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        h,w,ch = rgb.shape
        qimg = QImage(rgb.data,w,h,ch*w,QImage.Format_RGB888)
        self.face_feed.setPixmap(QPixmap.fromImage(qimg).scaled(self.face_feed.width(),self.face_feed.height(),Qt.KeepAspectRatio))

    # --- Chat + message bubbles ---
    def send_message(self):
        text = self.input_line.text().strip()
        if not text:
            return
        bubble = ChatBubble(text,"user")
        self.chat_area.addWidget(bubble)
        self.input_line.clear()
        threading.Thread(target=self.process_response,args=(text,),daemon=True).start()

    def process_response(self,text):
        # send to brain
        response = self.brain_callback(text)
        self.debug_box.append(f"Processed: {text} -> {response}")
        self.tts.say(response)
        self.tts.runAndWait()
        bubble = ChatBubble(response,"assistant")
        self.chat_area.addWidget(bubble)
