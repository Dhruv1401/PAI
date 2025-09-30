import socketio
import time
from PySide6.QtCore import QThread, Signal

class SocketIOClient(QThread):
    log_received = Signal(str)
    response_received = Signal(dict)
    connected = Signal()
    disconnected = Signal()

    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.connected_flag = False

        @self.sio.event
        def connect():
            print("Connected to server")
            self.connected_flag = True
            self.connected.emit()

        @self.sio.event
        def disconnect():
            print("Disconnected from server")
            self.connected_flag = False
            self.disconnected.emit()

        @self.sio.on('log')
        def on_log(data):
            self.log_received.emit(data)

        @self.sio.on('response')
        def on_response(data):
            self.response_received.emit(data)

    def run(self):
        while True:
            try:
                self.sio.connect('http://localhost:5001')
                self.sio.wait()
            except Exception as e:
                print(f"Connection error: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def send_message(self, text):
        if self.connected_flag:
            self.sio.emit('message', {'text': text})
        else:
            print("Not connected to server, cannot send message")

    def is_connected(self):
        return self.connected_flag
