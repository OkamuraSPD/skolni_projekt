import socket
import threading
import json
import time
from datetime import datetime

class ESP32SocketServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self.thread = None
        self.sensors_data = {}
        
    def start_server(self):
        """Spustí socket server"""
        if self.is_running:
            print("⚠️  Server již běží")
            return False
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.is_running = True
            
            self.thread = threading.Thread(target=self._accept_connections)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"✅ ESP32 Socket Server spuštěn na {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ Chyba při spuštění serveru: {e}")
            return False
    
    def stop_server(self):
        """Zastaví socket server"""
        if not self.is_running:
            print("⚠️  Server není spuštěn")
            return False
            
        self.is_running = False
        if self.socket:
            self.socket.close()
        print("❌ ESP32 Socket Server zastaven")
        return True
    
    def _accept_connections(self):
        """Přijímá nová připojení"""
        while self.is_running:
            try:
                client_socket, address = self.socket.accept()
                print(f"🔗 Nové připojení od {address}")
                
                # Spustíme vlákno pro každého klienta
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    print(f"❌ Chyba při přijímání připojení: {e}")
    
    def _handle_client(self, client_socket, address):
        """Zpracovává data od klienta"""
        try:
            while self.is_running:
                # Čtení dat od klienta
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                print(f"📨 Data od {address}: {data.strip()}")
                
                # Zpracování JSON dat
                try:
                    sensor_data = json.loads(data.strip())
                    self._process_sensor_data(sensor_data, address)
                    
                    # Odeslání potvrzení
                    response = json.dumps({"status": "ok", "message": "Data přijata"})
                    client_socket.send((response + "\n").encode('utf-8'))
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Chyba JSON od {address}: {e}")
                    error_response = json.dumps({"status": "error", "message": "Neplatný JSON"})
                    client_socket.send((error_response + "\n").encode('utf-8'))
                    
        except Exception as e:
            print(f"❌ Chyba při zpracování klienta {address}: {e}")
        finally:
            client_socket.close()
            print(f"🔌 Připojení ukončeno: {address}")
    
    def _process_sensor_data(self, data, address):
        """Zpracuje data ze senzorů a uloží je"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Vytvoříme strukturu pro naše senzory
            # Předpokládáme, že ESP32 posílá data z různých pinů
            processed_data = {
                "timestamp": timestamp,
                "source": str(address),
                "sensors": {}
            }
            
            # Zpracování teploty (pokud existuje)
            if "teplota" in data:
                processed_data["sensors"]["temperature"] = {
                    "value": data["teplota"],
                    "type": "analog",
                    "unit": "raw"
                }
            
            # Zpracování napětí
            if "voltage" in data:
                processed_data["sensors"]["voltage_35"] = {
                    "value": data["voltage"],
                    "type": "analog", 
                    "unit": "V"
                }
            
            if "voltage2" in data:
                processed_data["sensors"]["voltage_34"] = {
                    "value": data["voltage2"],
                    "type": "analog",
                    "unit": "V"
                }
            
            # Uložení dat
            self.sensors_data = processed_data
            print(f"💾 Data uložena: {processed_data}")
            
        except Exception as e:
            print(f"❌ Chyba při zpracování dat: {e}")
    
    def get_sensor_data(self):
        """Vrátí aktuální data ze senzorů"""
        return self.sensors_data
    
    def is_connected(self):
        """Zkontroluje jestli je nějaké ESP32 připojeno"""
        return bool(self.sensors_data)

# Globální instance
esp32_server = ESP32SocketServer()

def start_esp32_server():
    """Spustí ESP32 server"""
    return esp32_server.start_server()

def stop_esp32_server():
    """Zastaví ESP32 server"""
    return esp32_server.stop_server()

def get_esp32_server():
    """Vrátí instanci serveru"""
    return esp32_server

if __name__ == "__main__":
    # Spuštění serveru při přímém volání
    server = ESP32SocketServer()
    if server.start_server():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop_server()