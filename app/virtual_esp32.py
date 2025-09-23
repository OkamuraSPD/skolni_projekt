import threading
import time
import random
import json
from datetime import datetime

class VirtualESP32:
    def __init__(self):
        self.callback = None
        self.running = False
        self.thread = None
        self.device_states = {
            'light1': False,
            'light2': False,
            'heater': False,
            'fan': False
        }
    
    def set_callback(self, callback):
        self.callback = callback
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._simulate_esp32, daemon=True)
        self.thread.start()
        print("[VirtualESP32] Virtuální ESP32 spuštěno")
        
        # Simulace připojení
        if self.callback:
            self.callback("device_connected")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("[VirtualESP32] Virtuální ESP32 zastaveno")
    
    def send_command(self, command):
        """Simulace přijetí příkazu z webu"""
        print(f"[VirtualESP32] Příkaz přijat: {command}")
        
        try:
            if command.startswith("CONTROL:"):
                parts = command.split(":")
                device_id = parts[1]
                action = parts[2]
                value = parts[3] if len(parts) > 3 else None
                
                # Simulace ovládání zařízení
                if action == "toggle":
                    self.device_states[device_id] = not self.device_states[device_id]
                elif action == "set":
                    self.device_states[device_id] = value == "1"
                
                # Odeslání potvrzení
                if self.callback:
                    response = {
                        'type': 'device_status',
                        'device_id': device_id,
                        'state': self.device_states[device_id],
                        'timestamp': datetime.now().isoformat()
                    }
                    self.callback(json.dumps(response))
                    
        except Exception as e:
            print(f"[VirtualESP32] Chyba příkazu: {e}")
    
    def _simulate_esp32(self):
        """Hlavní simulační smyčka"""
        while self.running:
            try:
                # Generování náhodných senzorových dat
                sensor_data = {
                    'temperature': round(20 + random.uniform(-2, 5), 1),
                    'humidity': round(40 + random.uniform(-10, 20), 1),
                    'light': random.randint(0, 1000),
                    'pressure': round(1013 + random.uniform(-10, 10), 2),
                    'timestamp': datetime.now().isoformat(),
                    'type': 'sensor_data'
                }
                
                # Náhodné "chyby" senzorů
                if random.random() < 0.05:  # 5% šance na chybu
                    sensor_data['error'] = 'Sensor reading unstable'
                
                # Odeslání dat přes callback
                if self.callback:
                    self.callback(json.dumps(sensor_data))
                
                # Náhodný interval 1-5 sekund
                sleep_time = random.uniform(1, 5)
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"[VirtualESP32] Chyba simulace: {e}")
                time.sleep(1)