import face_recognition
import cv2
import os
import numpy as np

class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config
        self.known_faces = []
        self.known_names = []
        self.data_dir = "data/faces"
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_faces()

    def load_faces(self):
        for file in os.listdir(self.data_dir):
            if file.endswith(".jpg") or file.endswith(".png"):
                image = face_recognition.load_image_file(os.path.join(self.data_dir, file))
                encoding = face_recognition.face_encodings(image)[0]
                self.known_faces.append(encoding)
                self.known_names.append(file.split(".")[0])

    def run(self):
        video = cv2.VideoCapture(0)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb_frame)
            encodings = face_recognition.face_encodings(rgb_frame, locations)

            for encoding, loc in zip(encodings, locations):
                matches = face_recognition.compare_faces(self.known_faces, encoding)
                name = "Unknown"

                if True in matches:
                    index = np.argmin(face_recognition.face_distance(self.known_faces, encoding))
                    name = self.known_names[index]

                top, right, bottom, left = loc
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.imshow("Jarvis Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        video.release()
        cv2.destroyAllWindows()
