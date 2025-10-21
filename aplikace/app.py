from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import tempfile
from datetime import datetime
from esp32_simulator import esp32_simulator, start_esp32_simulator, stop_esp32_simulator

app = Flask(__name__)
# Použijeme absolutní cestu uvnitř adresáře aplikace, aby data.json bylo vždy v tomtéž adresáři
DATA_FILE = os.path.join(app.root_path, 'data.json')

# Načtení dat ze souboru
def load_data():
    if not os.path.exists(DATA_FILE):
        base_data = {"sensors": []}
        try:
            save_data(base_data)
        except Exception as e:
            print(f"Chyba při vytváření {DATA_FILE}: {e}")
        return base_data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "sensors" not in data:
                data = {"sensors": []}
            return data
    except json.JSONDecodeError as e:
        # Poškozený soubor — logneme a přepíšeme základní strukturou
        print(f"Chyba při načítání souboru (JSONDecodeError): {e}. Soubor bude obnoven.")
        base_data = {"sensors": []}
        try:
            save_data(base_data)
        except Exception as ex:
            print(f"Chyba při přepisování poškozeného {DATA_FILE}: {ex}")
        return base_data
    except Exception as e:
        print(f"Chyba při načítání souboru: {e}")
        return {"sensors": []}

# Uložení dat do souboru (atomicky)
def save_data(data):
    if "sensors" not in data:
        data = {"sensors": data} if isinstance(data, list) else {"sensors": []}
    
    dirpath = os.path.dirname(DATA_FILE)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    # Atomický zápis: zapíšeme do temp souboru a pak nahradíme
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=dirpath) as tmpf:
            json.dump(data, tmpf, ensure_ascii=False, indent=4)
            tmpname = tmpf.name
        os.replace(tmpname, DATA_FILE)
    except Exception as e:
        # Pokud dojde k chybě, snažíme se odstranit temp soubor pokud existuje
        try:
            if 'tmpname' in locals() and os.path.exists(tmpname):
                os.remove(tmpname)
        except Exception:
            pass
        print(f"Chyba při ukládání dat do {DATA_FILE}: {e}")
        raise

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
        "pin": request.form.get('pin', ''),
        "type": request.form.get('type', ''),
        "name": request.form.get('name', ''),
        "sensor_type": request.form.get('sensor_type', ''),
        "location": request.form.get('location', ''),
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

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Základní validace - upravte podle potřeby
    pin = payload.get('pin')
    s_type = payload.get('type')
    name = payload.get('name')
    sensor_type = payload.get('sensor_type')
    location = payload.get('location')

    if pin is None or s_type is None or name is None:
        return jsonify({"error": "Missing required fields: pin, type, name"}), 400

    new_sensor = {
        "id": len(data['sensors']) + 1,
        "pin": pin,
        "type": s_type,
        "name": name,
        "sensor_type": sensor_type or '',
        "location": location or '',
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