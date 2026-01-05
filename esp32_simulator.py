import random
import time
from json_manager import JsonManager

class ESP32Simulator:
    def __init__(self):
        pass


   #odeslání náhodných hodnot digitálních senzorů
    def send_digital_sensors_value(self):
        return random.randint(0, 1)
    
    def send_analog_sensors_value(self):
        return random.randint(0, 1023)
    
    def loop(self):
        while True:
            sensors = JsonManager('static/data.json').read_json()
            for sensor in sensors:
                if sensor["A/D"] == "D":
                    new_value = self.send_digital_sensors_value()
                    JsonManager('static/data.json').update_by_pin(sensor["pin"], new_value)
                    print(f"Sensor Pin: {sensor['pin']}, New Value: {new_value}")
                if sensor["A/D"] == "A":
                    new_value = self.send_analog_sensors_value()
                    JsonManager('static/data.json').update_by_pin(sensor["pin"], new_value)
                    print(f"Sensor Pin: {sensor['pin']}, New Value: {new_value}")
                else:
                    print(f"Unknown sensor type for Pin: {sensor['sensor_type']}")
                
            time.sleep(2)  # čekej 5 sekund před dalším cyklem

   

if __name__ == "__main__":
    esp = ESP32Simulator()
    esp.loop()    
    