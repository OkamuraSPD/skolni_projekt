// ...existing code...
#include <WiFi.h>


void setup() {
  Serial.begin(115200);

  // JSON jako text
  const char* json = "{\"teplota\":23,\"vlhkost\":55}";

  // Vytvoření bufferu
  StaticJsonDocument<200> doc;

  // Parsování
  DeserializationError error = deserializeJson(doc, json);

  if (!error) {
    int teplota = doc["teplota"];
    int vlhkost = doc["vlhkost"];

    Serial.print("Teplota: ");
    Serial.println(teplota);
    Serial.print("Vlhkost: ");
    Serial.println(vlhkost);
  }
}

void loop() {}

// Nastavení Wi-Fi
const char* ssid     = "Vodafone-87C2";
const char* password = "9mvH3bgU";



// senzory
int teplomerL = 0;
int potenciometrL = 0;
int fotorezistorL = 0;

// pole senzorů
const int MAX_SIZE = 3; 
int seznam[MAX_SIZE];

// IP adresa serveru (PC, kde běží Python socket server)
const char* host = "192.168.0.74";  // změň podle IP PC
const uint16_t port = 5000;          // musí sedět s Python serverem

WiFiClient client;

void reconnectToServer() {
  while (!client.connect(host, port)) {
    Serial.println("❌ Nepodařilo se připojit k serveru, zkouším znovu...");
    delay(2000);
  }
  Serial.println("✅ Znovu připojeno k serveru!");
}

void setup() {
  Serial.begin(115200);

  // Připojení na WiFi
  WiFi.begin(ssid, password);
  Serial.print("Připojuji na WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi připojena!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Připojení k Python serveru
  reconnectToServer();
}

void loop() {
  if (!client.connected()) {
    reconnectToServer();
  }
  // čtení senzorů
  if (abs(analogRead(34) - teplomerL)>10){
      seznam[0] = analogRead(34);
      Serial.println(seznam[0]);
    }

  if (abs(analogRead(32) - potenciometrL)>10){
    seznam[1] = analogRead(32);
    Serial.println(seznam[1]);
  }

  if (abs(analogRead(33) - fotorezistorL)>10){
    seznam[2] = analogRead(33);
    Serial.println(seznam[2]);
  }

  

  client.println(String(seznam[0])+","+String(seznam[1])+","+String(seznam[2]) + "\n");

  Serial.print("Odesláno: "+ String(seznam[0])+","+String(seznam[1])+","+String(seznam[2]) + "\n");
  

  delay(1000); // pošle každou sekundu
}
// ...existing code...