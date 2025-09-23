from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from mc import ESP32SocketServer
from virtual_esp32 import VirtualESP32
import threading
import time
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot_dashboard_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Globální stav připojení
connected_esp32 = None
esp32_type = None  # 'real' nebo 'virtual'
sensor_data = {
    'temperature': 25.0,
    'humidity': 45.0,
    'light': 300,
    'pressure': 1013.25
}

# 📊 HLAVNÍ ROUTES
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/connect")
def connect_page():
    """Stránka pro připojení k ESP32"""
    return render_template("connect.html")

@app.route("/sensors")
def sensors_page():
    return render_template("sensors.html")

@app.route("/live-data")
def live_data():
    return render_template("live-data.html")

@app.route("/devices")
def devices_page():
    return render_template("devices.html")

# 📡 API ROUTES PRO ŘÍZENÍ
@app.route('/api/connect/real', methods=['POST'])
def connect_real_esp32():
    """Připojení k reálnému ESP32"""
    global connected_esp32, esp32_type
    
    data = request.get_json()
    ip = data.get('ip', '192.168.1.100')
    port = data.get('port', 5000)
    
    try:
        # Ukončení stávajícího připojení
        if connected_esp32:
            disconnect_esp32()
        
        # Vytvoření nového socket serveru
        esp32_type = 'real'
        connected_esp32 = ESP32SocketServer(host=ip, port=port)
        connected_esp32.set_callback(handle_esp32_data)
        connected_esp32.start()
        
        return jsonify({
            'status': 'success', 
            'message': f'Připojeno k ESP32 na {ip}:{port}',
            'type': 'real'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/connect/virtual', methods=['POST'])
def connect_virtual_esp32():
    """Připojení k virtuálnímu ESP32"""
    global connected_esp32, esp32_type
    
    try:
        # Ukončení stávajícího připojení
        if connected_esp32:
            disconnect_esp32()
        
        # Vytvoření virtuálního ESP32
        esp32_type = 'virtual'
        connected_esp32 = VirtualESP32()
        connected_esp32.set_callback(handle_esp32_data)
        connected_esp32.start()
        
        return jsonify({
            'status': 'success', 
            'message': 'Virtuální ESP32 spuštěno',
            'type': 'virtual'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Odpojení od ESP32"""
    disconnect_esp32()
    return jsonify({'status': 'success', 'message': 'Odpojeno od ESP32'})

@app.route('/api/status')
def get_status():
    """Stav připojení"""
    return jsonify({
        'connected': connected_esp32 is not None,
        'type': esp32_type,
        'sensor_data': sensor_data
    })

@app.route('/api/control/device', methods=['POST'])
def control_device():
    """Odeslání příkazu na ESP32"""
    data = request.get_json()
    device_id = data.get('device_id')
    action = data.get('action')
    value = data.get('value')
    
    # Příprava zprávy pro ESP32
    command = f"CONTROL:{device_id}:{action}:{value}"
    
    if connected_esp32 and hasattr(connected_esp32, 'send_command'):
        connected_esp32.send_command(command)
    
    # Broadcast přes WebSocket
    socketio.emit('device_controlled', {
        'device_id': device_id,
        'action': action,
        'value': value,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success', 'message': 'Příkaz odeslán'})

# 🔌 WEBSOCKET HANDLERS
@socketio.on('connect')
def handle_connect():
    print("Web klient připojen")
    # Odeslání aktuálního stavu
    socketio.emit('connection_status', {
        'connected': connected_esp32 is not None,
        'type': esp32_type,
        'sensor_data': sensor_data
    })

@socketio.on('request_sensor_data')
def handle_data_request():
    """Client žádá o aktuální data"""
    socketio.emit('sensor_data_update', sensor_data)

# 📡 CALLBACK PRO DATA Z ESP32
def handle_esp32_data(data):
    """Zpracování dat z ESP32 (reálného nebo virtuálního)"""
    print(f"[Flask] Data z ESP32: {data}")
    
    try:
        # Zpracování různých formátů dat
        if data == "device_connected":
            socketio.emit('esp32_status', {'status': 'connected'})
            return
        
        # Pokus o parsování JSON
        if data.strip().startswith('{'):
            json_data = json.loads(data)
            process_sensor_data(json_data)
        else:
            # Zpracování textového formátu
            process_text_data(data)
            
    except Exception as e:
        print(f"Chyba při zpracování dat: {e}")
        # Přeposlání surových dat
        socketio.emit('sensor_data', {'raw': data})

def process_sensor_data(data):
    """Zpracování JSON dat ze senzorů"""
    global sensor_data
    
    # Aktualizace senzorových dat
    if 'temperature' in data:
        sensor_data['temperature'] = float(data['temperature'])
    if 'humidity' in data:
        sensor_data['humidity'] = float(data['humidity'])
    if 'light' in data:
        sensor_data['light'] = int(data['light'])
    if 'pressure' in data:
        sensor_data['pressure'] = float(data['pressure'])
    
    # Přidání timestampu
    sensor_data['timestamp'] = datetime.now().isoformat()
    
    # Odeslání přes WebSocket
    socketio.emit('sensor_data_update', sensor_data)
    print(f"[Flask] Aktualizováno: {sensor_data}")

def process_text_data(data):
    """Zpracování textových dat (např.: TEMP:23.5,HUM:45)"""
    global sensor_data
    
    # Různé formáty textových dat
    if 'TEMP:' in data and 'HUM:' in data:
        try:
            parts = data.split(',')
            for part in parts:
                if 'TEMP:' in part:
                    sensor_data['temperature'] = float(part.split(':')[1])
                elif 'HUM:' in part:
                    sensor_data['humidity'] = float(part.split(':')[1])
                elif 'LIGHT:' in part:
                    sensor_data['light'] = int(part.split(':')[1])
        except ValueError as e:
            print(f"Chyba parsování: {e}")

def disconnect_esp32():
    """Odpojení od ESP32"""
    global connected_esp32, esp32_type
    
    if connected_esp32:
        if hasattr(connected_esp32, 'stop'):
            connected_esp32.stop()
        connected_esp32 = None
        esp32_type = None
    
    socketio.emit('esp32_status', {'status': 'disconnected'})

if __name__ == "__main__":
    print("🚀 Starting IoT Flask Dashboard...")
    print("📡 Access the dashboard at: http://localhost:8001")
    print("🔌 Connect to ESP32 at: http://localhost:8001/connect")
    
    socketio.run(app, host="0.0.0.0", port=8001, debug=True)