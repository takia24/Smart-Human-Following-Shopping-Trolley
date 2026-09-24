#include <SPI.h>
#include <MFRC522.h>

// ---------- Ultrasonic ----------
#define TRIG_PIN 9
#define ECHO_PIN 8

// ---------- Motor ----------
const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;

// ---------- RFID ----------
#define SS_PIN 6
#define RST_PIN 7

MFRC522 rfid(SS_PIN, RST_PIN);

long duration;
float distance;

// ---------- Billing ----------
float totalBill = 0;


// ---------- Product Function ----------

void checkProduct() {

  byte *uid = rfid.uid.uidByte;

  // Card 1
  if (uid[0] == 0x5D &&
      uid[1] == 0xF2 &&
      uid[2] == 0xF0 &&
      uid[3] == 0xCF) {

    Serial.println("--------------------");
    Serial.println("Product: Milk");
    Serial.println("Price: Tk 80");

    totalBill = totalBill + 80;

    Serial.print("Total Bill: Tk ");
    Serial.println(totalBill);

    Serial.println("--------------------");
  }

  // Card 2
  else if (uid[0] == 0x8D &&
           uid[1] == 0x80 &&
           uid[2] == 0xF0 &&
           uid[3] == 0xCF) {

    Serial.println("--------------------");
    Serial.println("Product: Bread");
    Serial.println("Price: Tk 60");

    totalBill = totalBill + 60;

    Serial.print("Total Bill: Tk ");
    Serial.println(totalBill);

    Serial.println("--------------------");
  }

  // Card 3
  else if (uid[0] == 0x2E &&
           uid[1] == 0x0F &&
           uid[2] == 0x02 &&
           uid[3] == 0x07) {

    Serial.println("--------------------");
    Serial.println("Product: Biscuit");
    Serial.println("Price: Tk 50");

    totalBill = totalBill + 50;

    Serial.print("Total Bill: Tk ");
    Serial.println(totalBill);

    Serial.println("--------------------");
  }

  else {

    Serial.println("Unknown Card!");
    Serial.println("Product not registered.");
  }
}


void setup() {

  Serial.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  SPI.begin();
  rfid.PCD_Init();

  delay(100);

  Serial.println("Smart Trolley Started");
  Serial.println("Scan RFID Card...");
  Serial.println();
}


void loop() {

  // =========================
  // ULTRASONIC
  // =========================

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH, 25000);

  if (duration > 0) {

    distance = duration * 0.0343 / 2;

    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");

    // Human following
    if (distance > 5 && distance < 25) {

      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);

      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);

    } 
    else {

      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);

      digitalWrite(IN3, LOW);
      digitalWrite(IN4, LOW);
    }
  }


  // =========================
  // RFID BILLING
  // =========================

  if (rfid.PICC_IsNewCardPresent()) {

    if (rfid.PICC_ReadCardSerial()) {

      Serial.println();
      Serial.println("RFID Card Detected!");

      Serial.print("UID: ");

      for (byte i = 0; i < rfid.uid.size; i++) {

        if (rfid.uid.uidByte[i] < 0x10)
          Serial.print("0");

        Serial.print(rfid.uid.uidByte[i], HEX);

        if (i < rfid.uid.size - 1)
          Serial.print(":");
      }

      Serial.println();

      // Check product and add price
      checkProduct();

      rfid.PICC_HaltA();
      rfid.PCD_StopCrypto1();

      delay(1000);
    }
  }

  delay(150);
}