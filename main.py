import sys
from PySide6.QtWidgets import QApplication
from gui_components import AssistantGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec())
