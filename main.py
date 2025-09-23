import sys
import json
from PyQt5.QtWidgets import QApplication
from gui_interface import ChatGUI

# Fake brain function for now
def brain(user_input):
    return f"[LLM simulated] You said: {user_input}"

def main():
    app = QApplication(sys.argv)
    gui = ChatGUI(brain)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    