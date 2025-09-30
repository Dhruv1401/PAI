# TODO for Alexa-like Assistant GUI Refactor

- [x] Update requirements.txt to add PySide6 and python-socketio
- [x] Refactor code into multiple files for modularity
  - [x] Create main.py to start the app
  - [x] Create client.py for socketio client thread with retry logic
  - [x] Create gui_components.py for GUI widgets and layout matching static/index.html
  - [x] Create tts.py for text-to-speech
- [x] Improve GUI to match static/index.html design
  - [x] Chat panel with messages, input, mic button
  - [x] Side panel with tabs for log and settings
  - [x] Theme toggle
  - [x] Timestamps and copy buttons for messages
- [x] Add voice output for assistant responses
- [x] Add speech recognition for mic button
- [x] Test by running app.py and main.py
