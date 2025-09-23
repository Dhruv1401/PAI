import cv2
import mediapipe as mp
from PySide6.QtCore import QThread, Signal
import os
import pickle

class FaceRecognition(QThread):
    frame_updated = Signal(object)
    recognized_face = Signal(str)

    def __init__(self):
        super().__init__()
        self.mp_face = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.6)
        self.known_faces_file = "data/memory/faces.pkl"
        self.load_known_faces()

    def load_known_faces(self):
        if os.path.exists(self.known_faces_file):
            with open(self.known_faces_file, "rb") as f:
                self.known_faces = pickle.load(f)
        else:
            self.known_faces = {}

    def save_known_faces(self):
        with open(self.known_faces_file, "wb") as f:
            pickle.dump(self.known_faces, f)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_face.process(rgb_frame)
            if results.detections:
                for det in results.detections:
                    bboxC = det.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x, y, bw, bh = int(bboxC.xmin*w), int(bboxC.ymin*h), int(bboxC.width*w), int(bboxC.height*h)
                    cv2.rectangle(frame, (x,y), (x+bw, y+bh), (0,255,0), 2)
                    # Recognition logic can be added here
            self.frame_updated.emit(frame)
