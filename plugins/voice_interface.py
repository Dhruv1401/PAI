import threading, time, speech_recognition as sr

class VoiceInterface:
    def __init__(self, gui):
        self.gui = gui
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        threading.Thread(target=self.listen_loop,daemon=True).start()

    def listen_loop(self):
        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio).lower()
                if "hey pai" in text:
                    self.gui.wake_label.setText("Listening...")
                    self.gui.wake_label.setStyleSheet("color:#00ff00;font-size:16pt;")
                    self.listen_command()
                    self.gui.wake_label.setText("Waiting for wake word...")
                    self.gui.wake_label.setStyleSheet("color:#ffcc00;font-size:14pt;")
            except: pass

    def listen_command(self):
        collected = []
        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio).lower()
                if "over" in text:
                    command = " ".join(collected)
                    self.gui.input_line.setText(command)
                    self.gui.send_message()
                    break
                else:
                    collected.append(text)
            except: pass
