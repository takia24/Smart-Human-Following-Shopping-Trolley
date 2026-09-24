from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    session
)

import serial
import threading
import json
import os
from datetime import datetime

from security import (
    validate_rfid,
    validate_price,
    validate_serial_line,
    calculate_secure_total
)

from logger import (
    log_checkout,
    log_logout,
    log_security_warning
)


app = Flask(__name__)

# =========================
# Flask Security
# =========================

app.secret_key = "smart-trolley-secret-key-2026"


# =========================
# Arduino
# =========================

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

arduino = None


try:

    arduino = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    print(
        "Arduino connected:",
        SERIAL_PORT
    )

except Exception as e:

    print(
        "Arduino not connected:",
        e
    )


# =========================
# Load Products
# =========================

def load_products():

    try:

        with open(
            "products.json",
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        print(
            "Product database error:",
            e
        )

        return {}


products = load_products()


# =========================
# Data
# =========================

distance = 0

current_uid = "No Card"

rfid_status = "Waiting for RFID card"

cart = {}


# =========================
# Arduino Reader
# =========================

def read_arduino():

    global distance
    global current_uid
    global rfid_status

    if arduino is None:
        return

    while True:

        try:

            line = arduino.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()


            if not line:
                continue


            print(
                "Arduino:",
                line
            )


            # =========================
            # Validate Serial Input
            # =========================

            if not validate_serial_line(line):

                continue


            # =========================
            # Distance
            # =========================

            if line.startswith("Distance:"):

                try:

                    value = line.split(
                        ":",
                        1
                    )[1]

                    distance = float(
                        value.replace(
                            "cm",
                            ""
                        ).strip()
                    )

                except Exception:

                    log_security_warning(
                        "Invalid distance data"
                    )


            # =========================
            # RFID
            # =========================

            elif line.startswith("UID:"):

                raw_uid = line.replace(
                    "UID:",
                    "",
                    1
                ).strip()


                authorized, uid, product = (
                    validate_rfid(
                        raw_uid,
                        products
                    )
                )


                if not authorized:

                    current_uid = (
                        uid
                        if uid
                        else raw_uid.upper()
                    )

                    rfid_status = (
                        "UNAUTHORIZED RFID CARD"
                    )

                    print(
                        "Unauthorized RFID:",
                        current_uid
                    )

                    continue


                # =========================
                # Authorized Card
                # =========================

                current_uid = uid


                name = product["name"]

                price = product["price"]


                # =========================
                # Server-side Price Check
                # =========================

                if not validate_price(
                    name,
                    price,
                    products
                ):

                    rfid_status = (
                        "PRICE VALIDATION FAILED"
                    )

                    continue


                rfid_status = (
                    "Authorized: "
                    + name
                )


                # =========================
                # Add Product
                # =========================

                if name not in cart:

                    cart[name] = {

                        "price": price,

                        "qty": 1

                    }

                else:

                    cart[name]["qty"] += 1


                print(
                    "Added:",
                    name,
                    "- Tk",
                    price
                )


        except Exception as e:

            print(
                "Serial error:",
                e
            )

            log_security_warning(
                f"Serial exception: {e}"
            )


# =========================
# Start Arduino Thread
# =========================

if arduino is not None:

    thread = threading.Thread(
        target=read_arduino,
        daemon=True
    )

    thread.start()


# =========================
# LOGIN PAGE
# =========================

@app.route("/")
def index():

    if not session.get(
        "logged_in",
        False
    ):

        return render_template(
            "login.html"
        )


    return render_template(
        "index.html"
    )


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid request."

        }), 400


    username = str(
        data.get(
            "username",
            ""
        )
    ).strip()


    password = str(
        data.get(
            "password",
            ""
        )
    )


    # =========================
    # Load Users
    # =========================

    try:

        with open(
            "users.json",
            "r",
            encoding="utf-8"
        ) as file:

            users = json.load(file)

    except Exception as e:

        log_security_warning(
            f"User database error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                "User database error."

        }), 500


    # =========================
    # Authentication
    # =========================

    if (
        username in users
        and
        users[username].get(
            "password"
        ) == password
    ):

        session["logged_in"] = True

        session["username"] = username

        session["role"] = users[
            username
        ].get(
            "role",
            "user"
        )


        # logger
        from logger import log_login_success

        log_login_success(
            username
        )


        return jsonify({

            "success": True,

            "message":
                "Login successful"

        })


    # Failed login

    from logger import log_login_failed

    log_login_failed(
        username
    )


    return jsonify({

        "success": False,

        "message":
            "Invalid username or password."

    }), 401


# =========================
# LOGOUT
# =========================

@app.route(
    "/logout",
    methods=["POST"]
)
def logout():

    username = session.get(
        "username",
        "unknown"
    )


    session.clear()


    log_logout(
        username
    )


    return jsonify({

        "success": True

    })


# =========================
# DASHBOARD DATA
# =========================

@app.route("/data")
def data():

    if not session.get(
        "logged_in",
        False
    ):

        return jsonify({

            "logged_in": False

        }), 401


    total = 0

    items = 0


    for item in cart.values():

        total += (
            item["price"]
            *
            item["qty"]
        )

        items += item["qty"]


    return jsonify({

        "logged_in": True,

        "username":
            session.get(
                "username",
                ""
            ),

        "uid":
            current_uid,

        "rfid_status":
            rfid_status,

        "distance":
            round(
                distance,
                2
            ),

        "items":
            items,

        "cart":
            cart,

        "total":
            round(
                total,
                2
            )

    })


# =========================
# CHECKOUT
# =========================

@app.route(
    "/checkout",
    methods=["POST"]
)
def checkout():

    # =========================
    # Authentication
    # =========================

    if not session.get(
        "logged_in",
        False
    ):

        log_checkout(
            "0"
        )


        return jsonify({

            "success": False,

            "message":
                "Please login before checkout."

        }), 401


    username = session.get(
        "username",
        "unknown"
    )


    # =========================
    # Empty Cart
    # =========================

    if not cart:

        return jsonify({

            "success": False,

            "message":
                "Cart is empty!"

        })


    # =========================
    # Secure Total
    # =========================

    secure_total = calculate_secure_total(
        cart,
        products
    )


    if secure_total is None:

        log_security_warning(
            "Checkout blocked: "
            "cart validation failed"
        )


        return jsonify({

            "success": False,

            "message":
                "Security validation failed."

        }), 400


    total = secure_total


    # =========================
    # Receipt
    # =========================

    receipt_lines = []


    receipt_lines.append(
        "================================"
    )

    receipt_lines.append(
        "        SMART TROLLEY"
    )

    receipt_lines.append(
        "        PAYMENT RECEIPT"
    )

    receipt_lines.append(
        "================================"
    )


    receipt_lines.append(
        "User: " + username
    )


    receipt_lines.append(
        "Date: "
        +
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    )


    receipt_lines.append(
        "--------------------------------"
    )


    # =========================
    # Receipt Items
    # =========================

    for name, item in cart.items():

        qty = item["qty"]


        # Find trusted backend price

        trusted_price = None


        for product in products.values():

            if product.get(
                "name"
            ) == name:

                trusted_price = float(
                    product.get(
                        "price"
                    )
                )

                break


        if trusted_price is None:

            log_security_warning(
                f"Unknown product during checkout: {name}"
            )


            return jsonify({

                "success": False,

                "message":
                    "Unknown product detected."

            }), 400


        subtotal = (
            trusted_price
            *
            qty
        )


        receipt_lines.append(

            f"{name:<12} "
            f"x{qty:<3} "
            f"Tk {subtotal:.2f}"

        )


    receipt_lines.append(
        "--------------------------------"
    )


    receipt_lines.append(
        f"TOTAL:              Tk {total:.2f}"
    )


    receipt_lines.append(
        "================================"
    )


    receipt_lines.append(
        "       Thank You!"
    )


    receipt_lines.append(
        "================================"
    )


    # =========================
    # Save Receipt
    # =========================

    os.makedirs(
        "receipts",
        exist_ok=True
    )


    filename = (
        "receipt_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        +
        ".txt"
    )


    filepath = os.path.join(
        "receipts",
        filename
    )


    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(
                receipt_lines
            )
        )


    # =========================
    # Log Checkout
    # =========================

    log_checkout(
        total
    )


    # =========================
    # Clear Cart
    # =========================

    cart.clear()


    return jsonify({

        "success": True,

        "message":
            "Payment successful!",

        "total":
            total,

        "receipt":
            filename,

        "receipt_text":
            "\n".join(
                receipt_lines
            )

    })


# =========================
# CLEAR CART
# =========================

@app.route(
    "/clear",
    methods=["POST"]
)
def clear_cart():

    if not session.get(
        "logged_in",
        False
    ):

        return jsonify({

            "success": False,

            "message":
                "Login required."

        }), 401


    cart.clear()


    log_security_warning(
        "CART_CLEARED"
    )


    return jsonify({

        "success": True,

        "message":
            "Cart cleared"

    })


# =========================
# RUN
# =========================

if __name__ == "__main__":

    print(
        "\n=============================="
    )

    print(
        "   SMART TROLLEY SYSTEM"
    )

    print(
        "   Security Enabled"
    )

    print(
        "=============================="
    )

    print(
        "Arduino:",
        SERIAL_PORT
    )

    print(
        "Dashboard:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "==============================\n"
    )


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )