import speech_recognition as sr

async def get_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        txt = recognizer.recognize_google(audio)
        print(f"You: {txt}")
        return txt
    except:
        return ""
