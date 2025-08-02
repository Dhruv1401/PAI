import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # adjust speech rate

def voice_input():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"🗣️ You: {query}")
        return query
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError:
        print("⚠️ Speech recognition service unavailable.")
        return ""

def voice_output(response):
    print(f"🤖 PAI: {response}")
    engine.say(response)
    engine.runAndWait()
