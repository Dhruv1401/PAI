import pyttsx3

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Set properties if needed
        self.engine.setProperty('rate', 180)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# Singleton instance
tts = TTS()
