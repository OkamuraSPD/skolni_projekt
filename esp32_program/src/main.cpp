// ...existing code...
#include <WiFi.h>

// Nastavení Wi-Fi
const char* ssid     = "Vodafone-87C2";
const char* password = "9mvH3bgU";

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

  int fakeSensor = analogRead(32);  // jen simulace hodnoty

  client.println(String(fakeSensor) + "\n");

  Serial.print("Odesláno: ");
  Serial.println(fakeSensor);

  delay(1000); // pošle každou sekundu
}
// ...existing code...