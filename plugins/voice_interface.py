import speech_recognition as sr
import threading

class VoiceInterface:
    def __init__(self, config, gui_plugin):
        self.gui = gui_plugin
        self.assistant_name = config.get("assistant_name", "Assistant")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = True
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def listen_loop(self):
        while self.running:
            with self.microphone as source:
                print("[Voice] Listening for wake word...")
                audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio).lower()
                if f"hey {self.assistant_name.lower()}" in text:
                    self.gui.chat_display.append("<i>[Voice activated]</i>")
                    self.listen_command()
            except Exception:
                continue

    def listen_command(self):
        collected = []
        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio).lower()
                if "over" in text:
                    command = " ".join(collected)
                    self.gui.input_box.setText(command)
                    self.gui.handle_send()
                    break
                else:
                    collected.append(text)
            except:
                continue
