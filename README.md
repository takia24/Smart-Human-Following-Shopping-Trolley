# SHTS: An IoT-Based Smart Human-Following Shopping Trolley with Automated Billing and Intelligent Navigation

## 📌 Overview

SHTS is a low-cost IoT-based Smart Human-Following Shopping Trolley designed to automate trolley movement, product identification, billing, and real-time shopping monitoring.

The system combines autonomous human-following using an HC-SR04 ultrasonic sensor, RFID-based automated billing using an RC522 RFID reader, Arduino-based control, and a Flask web dashboard for real-time billing and checkout.

## ✨ Key Features

- 🤖 Autonomous human-following trolley
- 📡 HC-SR04 ultrasonic distance sensing
- 🏷️ RFID-based automatic product identification
- 💰 Automated billing and real-time total calculation
- 🔐 RFID authorization and product-price validation
- 🌐 Flask-based local web dashboard
- 🛒 Real-time cart and billing monitoring
- 🧾 Automated checkout and receipt generation
- ⚙️ Low-cost hardware implementation
- 📝 Security event logging and validation

## 🏗️ System Architecture

The system consists of:

- Arduino Uno
- HC-SR04 Ultrasonic Sensor
- RC522 RFID Reader
- L298N Motor Driver
- DC Motors
- RFID Cards
- Trolley Chassis
- 7.4V Li-ion Battery Pack
- Python Flask Web Application

The Arduino Uno acts as the central controller. It processes ultrasonic sensor readings, controls trolley movement, reads RFID cards, and communicates billing information with the Flask web application.

## 🔄 How It Works

### 1. Human Following

The HC-SR04 ultrasonic sensor measures the distance between the user and the trolley.

- 5–100 cm → Trolley moves forward
- Outside the predefined range → Trolley stops

### 2. RFID-Based Automated Billing

Each registered product is associated with an RFID card.

When an RFID card is detected:

1. The RFID UID is read.
2. The UID is checked against the registered product database.
3. The corresponding product and price are identified.
4. The price is validated.
5. The product is added to the cart.
6. The total bill is updated.

Unauthorized RFID cards are rejected.

### 3. Web-Based Billing Dashboard

The Flask-based dashboard provides:

- Product information
- Cart items
- Product quantities
- Running total
- Checkout
- Final bill
- Receipt generation

## 🧰 Hardware Components

| Component | Purpose |
|---|---|
| Arduino Uno | Main system controller |
| HC-SR04 | Human-following distance measurement |
| RC522 RFID Reader | Product identification |
| RFID Cards | Product identification |
| L298N Motor Driver | DC motor control |
| DC Motors | Trolley movement |
| Chassis Kit | Mechanical structure |
| 7.4V Li-ion Battery | Power supply |

## 💻 Software & Technologies

- Arduino
- Embedded C/C++
- Python
- Flask
- HTML/CSS
- USB Serial Communication
- RFID
- IoT

## 🧪 Experimental Results

The prototype was experimentally tested for:

- Human-following operation
- RFID product identification
- Automated billing
- Real-time cart monitoring
- Checkout and receipt generation
- RFID authorization
- Price validation
- Serial-input validation

During RFID billing tests, Bread, Milk, and Biscuit were assigned prices of Tk 60, Tk 80, and Tk 50 respectively. The system successfully calculated a total bill of Tk 190. :contentReference[oaicite:1]{index=1}

The ultrasonic following system was tested over different distances. The implemented control logic allowed forward movement within the 5–100 cm range and stopped the trolley outside this range. :contentReference[oaicite:2]{index=2}

## 💵 Estimated Hardware Cost

The estimated hardware cost of the prototype is **$32.00**.

| Component | Quantity |
|---|---:|
| Arduino Uno | 1 |
| Chassis Kit | 1 |
| L298N Motor Driver | 1 |
| HC-SR04 | 1 |
| RC522 RFID Reader | 1 |
| RFID Cards | 3 |

## 📁 Repository Contents

```text
Smart-Human-Following-Shopping-Trolley/
│
├── SMART_TROLLEY_BILLING/
├── arduino_Code_STB_26/
├── 2201008,2201010,2201049_Project Report.pdf
├── An_IoT_Based_Smart_Human_Following_...pdf
├── Payment Complete.pdf
├── Shopping Trolly_Presentation_Final_IRE314.pptx
├── .gitattributes
└── .gitignore
