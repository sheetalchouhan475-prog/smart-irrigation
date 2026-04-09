#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WiFi credentials
const char* ssid = "HODCSE";
const char* password = "12345678";

// Server URL (HTTPS)
String serverName = "https://smart-irrigation-wkta.onrender.com/data";

// Pins
#define RELAY_PIN 26  
#define SOIL_PIN 34  
#define DHTPIN 4  

 // Thresholds (Mandaleey scale)
int dryMandaleey = 900;  // Dry soil
int wetMandaleey = 400;  // Wet soil

// DHT
#define DHTTYPE DHT11  
DHT dht(DHTPIN, DHTTYPE);

// OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  dht.begin();

  // OLED start
  Wire.begin(21, 22);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found");
    while(true);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);

  // WiFi connect with timeout
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  unsigned long startAttemptTime = millis();
  const unsigned long wifiTimeout = 20000; // 20 sec timeout

  while(WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout){
      Serial.print(".");
      delay(500);
  }

  if(WiFi.status() == WL_CONNECTED){
      Serial.println("\nConnected to WiFi ✅");
      Serial.print("IP Address: ");
      Serial.println(WiFi.localIP());
  } else {
      Serial.println("\nFailed to connect WiFi. Check SSID/Password.");
  }
}

void loop() {
  // 1. Read sensor values
  int rawValue = analogRead(SOIL_PIN);
  int espValue = map(rawValue, 0, 4095, 0, 100);  // ESP32 scale 0-100

  // 2. Map ESP32 value to Mandaleey scale
  int moisture = map(espValue, 0, 100, dryMandaleey, wetMandaleey);

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT Error!");
    return;
  }

  String pumpStatus = "OFF";

  // 3. Pump control based on Mandaleey value
  if(moisture > 600){          // Soil dry
      digitalWrite(RELAY_PIN, LOW);
      pumpStatus = "ON";
  } else if(moisture < 500){   // Soil wet
      digitalWrite(RELAY_PIN, HIGH);
      pumpStatus = "OFF";
  } else {                      // Medium moisture
      digitalWrite(RELAY_PIN, LOW);
      pumpStatus = "OFF";
  }

  // 4. Send data to server if WiFi connected
  if(WiFi.status() == WL_CONNECTED) {
      WiFiClientSecure client;
      client.setInsecure(); // skip certificate verification

      HTTPClient https;
      String url = serverName + "?moisture=" + String(moisture) +
                   "&temperature=" + String(temperature) +
                   "&humidity=" + String(humidity);

      Serial.print("Sending data to: ");
      Serial.println(url);

      https.begin(client, url);
      int httpResponseCode = https.GET();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      if(httpResponseCode > 0){
          String response = https.getString();
          Serial.println("Server Response: " + response);
      } else {
          Serial.println("Error on HTTP request");
      }
      https.end();
  }

  // 5. Display on OLED
  display.clearDisplay();
  display.setCursor(0,0);
  display.print("Moisture: "); display.println(moisture); // Mandaleey scale
  display.print("Temp: "); display.print(temperature); display.println(" C");
  display.print("Humidity: "); display.print(humidity); display.println("%");
  display.print("Pump: "); display.println(pumpStatus);
  display.display();

  delay(10000); // wait 10 sec before next read
}
