from PySide6.QtWidgets import QApplication
import sys
from core.brain import Brain
from core.memory import Memory
from plugins.gui_interface import ChatGUI
from plugins.voice_interface import VoiceInterface
from plugins.face_recognition import FaceRecognition

def main():
    app = QApplication(sys.argv)
    memory = Memory()
    brain = Brain(scripted_responses={"hello": "Hi there!"})
    face_plugin = FaceRecognition()
    voice_plugin = VoiceInterface(side_panel=None)  # we’ll link panel after GUI

    gui = ChatGUI(brain, memory, voice_plugin, face_plugin)
    voice_plugin.side_panel = gui.side_panel

    face_plugin.start()
    voice_plugin.start()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
