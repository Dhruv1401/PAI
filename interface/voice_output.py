import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 160)

def output(text):
    print(f"TARS (voice): {text}")
    engine.say(text)
    engine.runAndWait()
