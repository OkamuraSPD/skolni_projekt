from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
from esp32_simulator import esp32_simulator, start_esp32_simulator, stop_esp32_simulator

app = Flask(__name__)
DATA_FILE = 'data.json'

# Načtení dat ze souboru
def load_data():
    if not os.path.exists(DATA_FILE):
        base_data = {"sensors": []}
        save_data(base_data)
        return base_data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "sensors" not in data:
                data = {"sensors": []}
            return data
    except (json.JSONDecodeError, Exception) as e:
        print(f"Chyba při načítání souboru: {e}")
        return {"sensors": []}

# Uložení dat do souboru
def save_data(data):
    if "sensors" not in data:
        data = {"sensors": data} if isinstance(data, list) else {"sensors": []}
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Hlavní stránka - rozcestník
@app.route('/')
def index():
    return render_template('index.html')

# Konfigurace senzorů
@app.route('/config')
def config():
    data = load_data()
    return render_template('config.html', sensors=data['sensors'])

# Monitorování senzorů
@app.route('/monitor')
def monitor():
    data = load_data()
    sensor_data = esp32_simulator.get_all_sensor_data()
    return render_template('monitor.html', 
                         sensors=data['sensors'], 
                         sensor_data=sensor_data,
                         now=datetime.now(),
                         simulator_running=esp32_simulator.is_running)

# ESP32 Simulátor ovládání
@app.route('/start_simulator', methods=['POST'])
def start_simulator():
    if start_esp32_simulator():
        return jsonify({"status": "success", "message": "Simulátor spuštěn"})
    else:
        return jsonify({"status": "error", "message": "Simulátor již běží"}), 400

@app.route('/stop_simulator', methods=['POST'])
def stop_simulator():
    if stop_esp32_simulator():
        return jsonify({"status": "success", "message": "Simulátor zastaven"})
    else:
        return jsonify({"status": "error", "message": "Simulátor není spuštěn"}), 400

@app.route('/simulator_status')
def simulator_status():
    return jsonify({
        "running": esp32_simulator.is_running,
        "sensors_data": esp32_simulator.get_all_sensor_data()
    })

@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = load_data()
    
    new_sensor = {
        "id": len(data['sensors']) + 1,
        "pin": request.form['pin'],
        "type": request.form['type'],
        "name": request.form['name'],
        "sensor_type": request.form['sensor_type'],
        "location": request.form['location'],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data['sensors'].append(new_sensor)
    save_data(data)
    
    return redirect(url_for('config'))

@app.route('/delete_sensor/<int:sensor_id>', methods=['POST'])
def delete_sensor(sensor_id):
    data = load_data()
    
    data['sensors'] = [sensor for sensor in data['sensors'] if sensor['id'] != sensor_id]
    
    for index, sensor in enumerate(data['sensors'], 1):
        sensor['id'] = index
    
    save_data(data)
    
    return redirect(url_for('config'))

# API endpoints
@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    data = load_data()
    return jsonify(data)

@app.route('/api/sensors', methods=['POST'])
def add_sensor_api():
    data = load_data()
    
    new_sensor = {
        "id": len(data['sensors']) + 1,
        "pin": request.json['pin'],
        "type": request.json['type'],
        "name": request.json['name'],
        "sensor_type": request.json['sensor_type'],
        "location": request.json['location'],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data['sensors'].append(new_sensor)
    save_data(data)
    
    return jsonify(new_sensor), 201

@app.route('/api/sensors/<int:sensor_id>', methods=['DELETE'])
def delete_sensor_api(sensor_id):
    data = load_data()
    
    original_count = len(data['sensors'])
    data['sensors'] = [sensor for sensor in data['sensors'] if sensor['id'] != sensor_id]
    
    if len(data['sensors']) == original_count:
        return jsonify({"error": "Sensor not found"}), 404
    
    for index, sensor in enumerate(data['sensors'], 1):
        sensor['id'] = index
    
    save_data(data)
    
    return jsonify({"message": "Sensor deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)