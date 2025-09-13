#include <WiFi.h>

// Nastavení Wi-Fi
const char* ssid     = "Vodafone-87C2";
const char* password = "9mvH3bgU";

// IP adresa serveru (PC, kde běží Python socket server)
const char* host = "192.168.0.74";  // změň podle IP PC
const uint16_t port = 5000;          // musí sedět s Python serverem

WiFiClient client;

const int MAX_SIZE = 3; // maximální velikost pole
int seznam[MAX_SIZE];

int teplomerL = 0;
int potenciometrL = 0;
int fotorezistorL = 0;

void reconnectToServer() {
  while (!client.connect(host, port)) {
    Serial.println("❌ Nepodařilo se připojit k serveru, zkouším znovu...");
    delay(2000);
  }
  Serial.println("✅ Znovu připojeno k serveru!");
}

void setup() {
  Serial.begin(9600);
  
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
  
  
  
  // Výpis všech hodnot
  for (int i = 0; i < MAX_SIZE-1; i++) {
    seznam[i] = 0;
    
  }
 
}



void loop() {
    if (!client.connected()) {
    reconnectToServer();
    }

    if (abs(analogRead(A0) - teplomerL)>10){
      seznam[0] = analogRead(A0);
      Serial.println(seznam[0]);
    }

    if (abs(analogRead(A1) - potenciometrL)>10){
      seznam[1] = analogRead(A1);
      Serial.println(seznam[1]);
    }

    if (abs(analogRead(A2) - fotorezistorL)>10){
      seznam[2] = analogRead(A2);
      Serial.println(seznam[2]);
    }

    client.println(seznam + "\n");

    Serial.print("Odesláno: ");


    teplomerL = analogRead(A0);
    potenciometrL = analogRead(A1);
    fotorezistorL = analogRead(A2);
    delay(100);




}