import serial
import serial.tools.list_ports
import time
import sys


# ==========================================
# USB / SERIAL INJECTION TEST
# ==========================================

BAUD_RATE = 9600


def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        print("❌ No serial port found.")
        return None

    print("\nAvailable Serial Ports:")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device} - {port.description}")

    # Try to automatically select Arduino
    for port in ports:
        desc = port.description.lower()

        if (
            "arduino" in desc
            or "ch340" in desc
            or "usb serial" in desc
            or "cp210" in desc
        ):
            return port.device

    # Otherwise ask user
    try:
        choice = int(input("\nSelect Arduino port number: "))
        return ports[choice - 1].device
    except (ValueError, IndexError):
        print("❌ Invalid port selection.")
        return None


def send_injection_test(port):
    print("\n==========================================")
    print(" USB / SERIAL INJECTION SECURITY TEST")
    print("==========================================")

    print(f"\nConnecting to: {port}")
    print(f"Baud rate: {BAUD_RATE}")

    try:
        ser = serial.Serial(
            port=port,
            baudrate=BAUD_RATE,
            timeout=1
        )

        time.sleep(2)

        # --------------------------------------
        # Fake / malicious serial inputs
        # --------------------------------------

        test_commands = [
            "PRICE=1",
            "PRICE:Biscuit:1",
            "TOTAL=1",
            "PRODUCT=Bread",
            "ADD_PRODUCT=Biscuit",
            "UID=FAKE_CARD",
            "FAKE_PRODUCT_ID=999",
            "ADMIN=TRUE",
            "CHECKOUT=FREE",
            "123456789",
        ]

        print("\nSending unrecognized serial data...\n")

        for command in test_commands:

            print(f">>> Sending: {command}")

            ser.write(
                (command + "\n").encode("utf-8")
            )

            time.sleep(0.5)

        ser.close()

        print("\n==========================================")
        print("✅ Injection test data sent.")
        print("==========================================")
        print("\nNow check billing.py terminal/log.")
        print("Expected result:")
        print("SERIAL_INPUT_REJECTED")
        print("No price/total modification should occur.")

    except serial.SerialException as e:

        print("\n❌ Serial connection failed.")
        print("------------------------------------------")
        print(e)
        print("------------------------------------------")

        print(
            "\nPossible reason:"
            "\n1. billing.py is already using the COM port."
            "\n2. Arduino IDE Serial Monitor is open."
            "\n3. Wrong COM port."
        )

        sys.exit(1)


if __name__ == "__main__":

    port = find_arduino_port()

    if port:
        send_injection_test(port)