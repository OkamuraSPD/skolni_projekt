import requests
import random
import time
import threading
import json
from datetime import datetime

class ESP32Simulator:
    def __init__(self, flask_url="http://localhost:5000"):
        self.flask_url = flask_url
        self.is_running = False
        self.thread = None
        self.sensors_data = {}
        
    def get_sensors_from_server(self):
        """Získá seznam senzorů z Flask serveru"""
        try:
            response = requests.get(f"{self.flask_url}/api/sensors")
            if response.status_code == 200:
                return response.json()["sensors"]
            else:
                print("Chyba při načítání senzorů ze serveru")
                return []
        except Exception as e:
            print(f"Chyba připojení k serveru: {e}")
            return []
    
    def generate_sensor_data(self, sensor):
        """Vygeneruje data pro senzor podle jeho typu"""
        if sensor["type"] == "analog":
            # Analogový senzor - hodnota 0-1023
            return random.randint(0, 1023)
        elif sensor["type"] == "digital":
            # Digitální senzor - náhodně 0 nebo 1
            return random.randint(0, 1)
        else:
            return 0
    
    def send_sensor_data(self, sensor, value):
        """Odešle data senzoru na server"""
        try:
            data = {
                "sensor_id": sensor["id"],
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "sensor_name": sensor["name"],
                "sensor_type": sensor["type"]
            }
            
            # Uložíme data lokálně pro rychlejší přístup
            self.sensors_data[sensor["id"]] = data
            
            # Simulujeme odeslání na server
            # V reálném případě bychom odeslali HTTP POST request
            print(f"📡 Senzor {sensor['name']} ({sensor['type']}): {value}")
            
        except Exception as e:
            print(f"Chyba při odesílání dat senzoru {sensor['name']}: {e}")
    
    def simulation_loop(self):
        """Hlavní smyčka simulace"""
        print("🚀 ESP32 simulátor spuštěn")
        
        while self.is_running:
            try:
                # Načteme aktuální seznam senzorů
                sensors = self.get_sensors_from_server()
                
                if not sensors:
                    print("⚠️  Žádné senzory k simulaci")
                    time.sleep(5)
                    continue
                
                # Pro každý senzor vygenerujeme data
                for sensor in sensors:
                    value = self.generate_sensor_data(sensor)
                    self.send_sensor_data(sensor, value)
                
                # Pauza mezi měřeními
                time.sleep(2)
                
            except Exception as e:
                print(f"Chyba v simulační smyčce: {e}")
                time.sleep(5)
    
    def start_simulation(self):
        """Spustí simulaci"""
        if self.is_running:
            print("⚠️  Simulace již běží")
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self.simulation_loop)
        self.thread.daemon = True
        self.thread.start()
        print("✅ ESP32 simulátor byl spuštěn")
        return True
    
    def stop_simulation(self):
        """Zastaví simulaci"""
        if not self.is_running:
            print("⚠️  Simulace není spuštěna")
            return False
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("❌ ESP32 simulátor byl zastaven")
        return True
    
    def get_sensor_data(self, sensor_id):
        """Vrátí data pro konkrétní senzor"""
        return self.sensors_data.get(sensor_id)
    
    def get_all_sensor_data(self):
        """Vrátí data všech senzorů"""
        return self.sensors_data

# Globální instance simulátoru
esp32_simulator = ESP32Simulator()

def start_esp32_simulator():
    """Spustí ESP32 simulátor"""
    return esp32_simulator.start_simulation()

def stop_esp32_simulator():
    """Zastaví ESP32 simulátor"""
    return esp32_simulator.stop_simulation()

def get_esp32_simulator():
    """Vrátí instanci simulátoru"""
    return esp32_simulator