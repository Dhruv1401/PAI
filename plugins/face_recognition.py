import cv2, os, pickle
import face_recognition
from PyQt5 import QtCore, QtGui, QtWidgets

class FaceRecognition(QtWidgets.QLabel):
    def __init__(self, config):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.data_path = "data/faces"
        os.makedirs(self.data_path, exist_ok=True)
        self.known_faces, self.known_names = self.load_known_faces()

    def load_known_faces(self):
        encodings, names = [], []
        for file in os.listdir(self.data_path):
            if file.endswith(".pkl"):
                with open(os.path.join(self.data_path, file), "rb") as f:
                    data = pickle.load(f)
                    encodings.append(data["encoding"])
                    names.append(data["name"])
        return encodings, names

    def register_face(self, name):
        ret, frame = self.cap.read()
        if not ret:
            return "Camera error"
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)
        if encodings:
            face_encoding = encodings[0]
            file_path = os.path.join(self.data_path, f"{name}.pkl")
            with open(file_path, "wb") as f:
                pickle.dump({"name": name, "encoding": face_encoding}, f)
            self.known_faces.append(face_encoding)
            self.known_names.append(name)
            return f"Face registered: {name}"
        return "No face detected"

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_faces, encoding)
            name = "Unknown"
            if True in matches:
                index = matches.index(True)
                name = self.known_names[index]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Show feed
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio))
