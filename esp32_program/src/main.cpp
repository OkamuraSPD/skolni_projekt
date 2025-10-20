#include <WiFi.h>
#include <ArduinoJson.h>

const char* ssid = "VASE_WIFI_SSID";
const char* password = "VASE_WIFI_HESLO";

const char* serverIP = "IP_FLASK_SERVERU";  // IP vašeho počítače
const int serverPort = 1234;

WiFiClient client;

// Senzory (simulované - připojte skutečné)
float temperature = 0;
float humidity = 0;
int lightLevel = 0;

void setup() {
  Serial.begin(115200);
  
  // Připojení k WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Připojování k WiFi...");
  }
  Serial.println("Připojeno k WiFi");
  
  // Připojení k serveru
  if (client.connect(serverIP, serverPort)) {
    Serial.println("Připojeno k serveru");
  } else {
    Serial.println("Chyba připojení k serveru");
  }
}

void loop() {
  if (!client.connected()) {
    // Pokus o opětovné připojení
    if (client.connect(serverIP, serverPort)) {
      Serial.println("Obnoveno připojení k serveru");
    }
  }
  
  // Čtení senzorů
  readSensors();
  
  // Odeslání dat
  sendSensorData();
  
  // Kontrola příchozích příkazů
  checkCommands();
  
  delay(2000);  // Odesílání každé 2 sekundy
}

void readSensors() {
  // Simulace dat - nahraďte skutečnými senzory
  temperature = random(200, 300) / 10.0;
  humidity = random(400, 800) / 10.0;
  lightLevel = random(0, 1024);
}

void sendSensorData() {
  StaticJsonDocument<200> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["light"] = lightLevel;
  doc["device_id"] = "ESP32_1";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  client.println(jsonString);
  Serial.println("Data odeslána: " + jsonString);
}

void checkCommands() {
  if (client.available()) {
    String command = client.readStringUntil('\n');
    Serial.println("Příkaz přijat: " + command);
    
    // Zpracování příkazu
    processCommand(command);
  }
}

void processCommand(String command) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, command);
  
  if (error) {
    Serial.println("Chyba parsování příkazu");
    return;
  }
  
  String action = doc["action"];
  int value = doc["value"];
  
  if (action == "led") {
    // Kontrola LED - příklad
    digitalWrite(LED_BUILTIN, value);
    Serial.println("LED nastavena na: " + String(value));
  }
}