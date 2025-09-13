from flask import Flask, render_template
from flask_socketio import SocketIO
from mc import ESP32SocketServer

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

# Callback pro příjem dat ze socket serveru
def handle_esp32_data(data):
    if data.strip():  # pouze pokud data nejsou prázdná
        print("[Flask] Přeposílám data na web:", data)
        socketio.emit("sensor_data", {"value": data})

@socketio.on('connect')
def test_connect():
    print("Web klient připojen")
    socketio.emit("sensor_data", {"value": "TEST"})

if __name__ == "__main__":
    # Spustíme socket server v pozadí
    socket_server = ESP32SocketServer(port=5000)
    socket_server.set_callback(handle_esp32_data)
    socket_server.start()

    # Spustíme Flask server
    socketio.run(app, host="0.0.0.0", port=8001)