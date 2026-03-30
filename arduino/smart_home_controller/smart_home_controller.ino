#include <Servo.h>
#include <DHT.h>

#define DHTPIN 7
#define DHTTYPE DHT22

const int ldrPin = A0;

// LED
const int led1 = 4;
const int led2 = 3;
const int led3 = 2;

// RGB LED (common anode)
const int redPin = 6;
const int greenPin = 11;
const int bluePin = 9;

// Servo
const int servoPin = 10;

// HC-SR04
const int trigPin = 12;
const int echoPin = 13;

Servo myServo;
DHT dht(DHTPIN, DHTTYPE);

const int ldrMin = 350;
const int ldrMax = 900;

int servoAngle = 0;

unsigned long lastRead = 0;
const long interval = 2000;

// posledné hodnoty
float lastTemperature = -1000;
float lastHumidity = -1000;
int lastLight = -1;
long lastDistance = -1;

void setup() {

  Serial.begin(9600);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  myServo.attach(servoPin);
  myServo.write(servoAngle);

  dht.begin();

  Serial.print("Servo startovacia poloha: ");
  Serial.print(servoAngle);
  Serial.println(" stupnov");

  Serial.println("Prikazy:");
  Serial.println("S <0-180>  -> servo");
  Serial.println("L r g b    -> RGB LED (0-255)");
}

void loop() {

  // ---- SERIAL OVLÁDANIE ----
  if (Serial.available()) {

    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("S")) {

      int newAngle = input.substring(1).toInt();

      if (newAngle >= 0 && newAngle <= 180) {
        servoAngle = newAngle;
        myServo.write(servoAngle);

        Serial.print("Nova poloha serva: ");
        Serial.println(servoAngle);
      }
    }

    else if (input.startsWith("L")) {

      int r, g, b;
      sscanf(input.c_str(), "L %d %d %d", &r, &g, &b);

      r = constrain(r,0,255);
      g = constrain(g,0,255);
      b = constrain(b,0,255);

      analogWrite(redPin,255-r);
      analogWrite(greenPin,255-g);
      analogWrite(bluePin,255-b);

      Serial.print("RGB nastavene: ");
      Serial.print(r);
      Serial.print(" ");
      Serial.print(g);
      Serial.print(" ");
      Serial.println(b);
    }
  }

  // ---- MERANIE ----
  if (millis() - lastRead >= interval) {

    lastRead = millis();

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    int ldrRaw = analogRead(ldrPin);
    ldrRaw = constrain(ldrRaw, ldrMin, ldrMax);
    int ldrPercent = map(ldrRaw, ldrMin, ldrMax, 0, 100);

    // ---- HC-SR04 ----
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH);

    long distance = duration * 0.034 / 2;

    // LED podľa svetla
    if (ldrPercent <= 40) {
      digitalWrite(led1, HIGH);
      digitalWrite(led2, HIGH);
      digitalWrite(led3, HIGH);
    } 
    else if (ldrPercent <= 66) {
      digitalWrite(led1, HIGH);
      digitalWrite(led2, HIGH);
      digitalWrite(led3, LOW);
    } 
    else if (ldrPercent < 90) {
      digitalWrite(led1, HIGH);
      digitalWrite(led2, LOW);
      digitalWrite(led3, LOW);
    } 
    else {
      digitalWrite(led1, LOW);
      digitalWrite(led2, LOW);
      digitalWrite(led3, LOW);
    }

    // výpis len pri zmene
    if (temperature != lastTemperature || humidity != lastHumidity || 
        ldrPercent != lastLight || distance != lastDistance) {

      Serial.print("{");
      Serial.print("\"temperature\":");
      Serial.print(temperature);
      Serial.print(",");

      Serial.print("\"humidity\":");
      Serial.print(humidity);
      Serial.print(",");

      Serial.print("\"light\":");
      Serial.print(ldrPercent);
      Serial.print(",");

      Serial.print("\"distance\":");
      Serial.print(distance);
      

      Serial.println("}");

      lastTemperature = temperature;
      lastHumidity = humidity;
      lastLight = ldrPercent;
      lastDistance = distance;
    }
  }
}