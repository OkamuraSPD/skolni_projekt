from flask import Flask, render_template, request, jsonify
import random
from esp32_simulator import ESP32Simulator
import threading
from json_manager import JsonManager

x = 0
y = 0

app = Flask(__name__)
data = {
        "message": "Ahoj z Flasku!",
        "status": "OK",
        "value": 42
    }
# 1️⃣ Hlavní stránka
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sensors_settings')
def sensors_settings():
    return render_template('sensors_settings.html')

# 2️⃣ Route pro odesílání dat z Flasku do JavaScriptu
@app.route('/get_data')
def get_data():
    data['value'] = data['value'] + 1  # Aktualizace hodnoty pro demonstraci
    return jsonify(data)

# 3️⃣ Route pro přijímání dat z formuláře (metoda POST)
@app.route('/submit_sensor', methods=['POST'])
def submit():
    global x
    sensor_type = request.form.get('sensor_type')
    ad = request.form.get('A/D')
    slot = request.form.get('slot')
    pin = request.form.get('pin')


    print(f"Přijatá data: {sensor_type}, {ad}, {slot}")
    JsonManager('static/data.json').write_json({
        "id": JsonManager('static/data.json').read_json().__len__() + 1+x,
        "sensor_type": sensor_type,
        "A/D": ad,
        "slot": slot,
        "pin": pin,
        "value":0
    })
    return jsonify({
        "status": "success",
        "message": "Data byla úspěšně přijata a uložena."

    
    })
# 4️⃣ Route pro mazání dat podle ID (metoda POST)
@app.route('/delete_sensor', methods=['POST'])
def delete():
    delete_id = request.form.get('delete_id')
    global x


    print(f"Přijatá data: {delete_id}")
    JsonManager('static/data.json').delete_by_id(int(delete_id))
    x = x+1
    return jsonify({
        "status": "success",
        "message": "Data byla úspěšně smazana a uložena."
})

# monitoring page
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')
    
#odesílání hodnot senzorů do monitoru
@app.route('/get_sensors')
def get_sensors():
    
    value = {}
    for i in JsonManager('static/data.json').read_json():
        
        value[i["pin"]] = i["value"]
        
    return jsonify(value)
@app.route('/outputs_settings')
def outputs_settings():
    return render_template('outputs_settings.html')

@app.route('/submit_output', methods=['POST'])
def submit2():
    global x
    output_type = request.form.get('output_type')
    ad = request.form.get('A/D')
    slot = request.form.get('slot')
    pin = request.form.get('pin')
    value = request.form.get('value')


    print(f"Přijatá data: {output_type}, {ad}, {slot}")
    JsonManager('static/outputs.json').write_json({
        "id": JsonManager('static/outputs.json').read_json().__len__() + 1+x,
        "output_type": output_type,
        "A/D": ad,
        "slot": slot,
        "pin": pin,
        "value":value
    })
    return jsonify({
        "status": "success",
        "message": "Data byla úspěšně přijata a uložena."

    
    })
# 4️⃣ Route pro mazání dat podle ID (metoda POST)
@app.route('/delete_output', methods=['POST'])
def delete_ouptut():
    delete_id = request.form.get('delete_id')
    global y


    print(f"Přijatá data: {delete_id}")
    JsonManager('static/outputs.json').delete_by_id(int(delete_id))
    y = y+1
    return jsonify({
        "status": "success",
        "message": "Data byla úspěšně smazana a uložena."
})



@app.route('/outputs')
def monitor_outputs():
    return render_template('outputs.html')
    
#odesílání hodnot senzorů do monitoru
@app.route('/get_outputs')
def get_outputs():
    
    value = {}
    for i in JsonManager('static/outputs.json').read_json():
        
        value[i["id"]] = [i[j] for j in i]
        
    print(value)    
       



    return jsonify(value)



if __name__ == "__main__":
    # spustíme background thread
    esp = ESP32Simulator()
    t = threading.Thread(target=esp.loop, daemon=True)
    t.start()

    app.run(debug=True, host="0.0.0.0")