import socket
import threading

class ESP32SocketServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.data_callback = None

    def set_callback(self, callback):
        self.data_callback = callback

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"[ESP32SocketServer] Listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                print(f"[ESP32SocketServer] Connected by {addr}")
                if self.data_callback:
                    self.data_callback("device_connected")
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        decoded = data.decode().strip()
                        print("[ESP32SocketServer] Received:", decoded)
                        if self.data_callback:
                            self.data_callback(decoded)