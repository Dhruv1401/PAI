import pyttsx3
import speech_recognition as sr
from PySide6.QtCore import QThread, Signal

class VoiceInterface(QThread):
    speech_received = Signal(str)
    wake_word = "pai"

    def __init__(self, side_panel):
        super().__init__()
        self.side_panel = side_panel
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def run(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio).lower()
                    if self.wake_word in text:
                        self.side_panel.set_status("Listening...")
                        if "over" in text:
                            text = text.replace(self.wake_word, "").replace("over", "").strip()
                            self.speech_received.emit(text)
                            self.side_panel.set_status("Idle")
                except Exception:
                    continue

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
