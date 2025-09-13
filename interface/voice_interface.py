# interface/voice_interface.py
import subprocess
import speech_recognition as sr

# Recognizer for voice input
recognizer = sr.Recognizer()

# Async wrapper for voice input
async def voice_input():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)  # offline alternative: pocketsphinx
        print(f"🗣️ You: {query}")
        return query
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError:
        print("⚠️ Speech recognition service unavailable.")
        return ""

# Voice output using offline espeak
def voice_output(text):
    # Use your default audio device (Bluetooth speaker if set)
    subprocess.run(["espeak", "-v", "en-us", text])
    print(f"🤖 PAI: {text}")

# Optional synchronous wrappers if needed
def voice_output_sync(text):
    voice_output(text)

def voice_input_sync():
    import asyncio
    return asyncio.run(voice_input())
