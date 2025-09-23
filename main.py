import json, os
from core.brain import Brain
from core.memory import Memory
from plugins.gui_interface import Plugin as GUI
from plugins.scripted_responses import Plugin as Scripted
from plugins.debug_logger import Plugin as DebugLogger
from plugins.voice_interface import VoiceInterface
from PyQt5.QtWidgets import QApplication
import sys

def load_config():
    config_path = os.path.join("config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    config = load_config()
    memory = Memory()
    brain = Brain(config)
    scripted = Scripted(config)
    debug_logger = DebugLogger(config)
    
    app = QApplication(sys.argv)
    gui = GUI(config, brain, scripted, memory, debug_logger)
    gui.show()

    # Voice interface runs in background
    VoiceInterface(config, gui, memory)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
