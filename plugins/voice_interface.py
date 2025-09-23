import speech_recognition as sr
import pyttsx3
import threading

class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config
        self.running = True
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("[Voice] Listening...")
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio)
        except:
            return ""

    def run(self):
        def loop():
            while self.running:
                text = self.listen().lower()
                if self.config["wake_word"] in text:
                    self.speak("Yes?")
                    command = self.listen().lower()
                    if self.config["end_word"] in command:
                        command = command.replace(self.config["end_word"], "").strip()
                        response = self.brain.process_input(command)
                        print(f"[Voice] {response}")
                        self.speak(response)

        threading.Thread(target=loop, daemon=True).start()
