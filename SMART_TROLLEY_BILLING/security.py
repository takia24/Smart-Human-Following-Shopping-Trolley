import re
from logger import (
    log_rfid_accepted,
    log_rfid_rejected,
    log_price_validation,
    log_serial_rejected,
    log_security_warning
)


# =========================
# RFID VALIDATION
# =========================

def normalize_uid(uid):
    """
    Convert RFID UID into a standard format.
    Example:
    8d80f0cf -> 8D:80:F0:CF
    """

    if uid is None:
        return None

    uid = str(uid).strip().upper()

    # Remove spaces, colons and hyphens
    clean_uid = re.sub(r"[^0-9A-F]", "", uid)

    # RFID UID must contain an even number of hex characters
    if len(clean_uid) == 0 or len(clean_uid) % 2 != 0:
        return None

    # Create XX:XX:XX:XX format
    parts = [
        clean_uid[i:i + 2]
        for i in range(0, len(clean_uid), 2)
    ]

    return ":".join(parts)


def validate_rfid(uid, products):
    """
    Check whether the RFID UID is registered.
    """

    normalized_uid = normalize_uid(uid)

    if normalized_uid is None:
        log_rfid_rejected(str(uid))
        return False, None, None

    if normalized_uid not in products:

        log_rfid_rejected(
            normalized_uid
        )

        return False, normalized_uid, None

    product = products[normalized_uid]

    name = product.get("name")
    price = product.get("price")

    # Basic product validation
    if not name or not isinstance(price, (int, float)):
        log_security_warning(
            f"INVALID_PRODUCT_DATA | uid={normalized_uid}"
        )

        return False, normalized_uid, None

    log_rfid_accepted(
        normalized_uid,
        name
    )

    return True, normalized_uid, product


# =========================
# PRICE VALIDATION
# =========================

def validate_price(
    product_name,
    received_price,
    products
):
    """
    Always compare the received price
    with the trusted backend price.
    """

    trusted_product = None

    for uid, product in products.items():

        if product.get("name") == product_name:
            trusted_product = product
            break

    if trusted_product is None:

        log_security_warning(
            f"UNKNOWN_PRODUCT | product={product_name}"
        )

        return False

    trusted_price = trusted_product.get("price")

    try:
        received_price = float(received_price)
        trusted_price = float(trusted_price)

    except (TypeError, ValueError):

        log_security_warning(
            f"INVALID_PRICE | product={product_name}"
        )

        return False

    if received_price != trusted_price:

        log_security_warning(
            f"PRICE_MANIPULATION_DETECTED | "
            f"product={product_name} | "
            f"received={received_price} | "
            f"trusted={trusted_price}"
        )

        return False

    log_price_validation(
        product_name,
        trusted_price
    )

    return True


# =========================
# SERIAL INPUT VALIDATION
# =========================

def validate_serial_line(line):
    """
    Allow only expected Arduino messages.
    """

    if not line:
        return False

    line = str(line).strip()

    # Distance message
    if line.startswith("Distance:"):

        value = line.replace(
            "Distance:",
            "",
            1
        ).strip()

        match = re.fullmatch(
            r"\d+(\.\d+)?\s*cm",
            value,
            re.IGNORECASE
        )

        if match:
            return True

        log_serial_rejected(line)
        return False

    # RFID message
    if line.startswith("UID:"):

        uid = line.replace(
            "UID:",
            "",
            1
        ).strip()

        if normalize_uid(uid) is not None:
            return True

        log_serial_rejected(line)
        return False

    # Unknown Arduino message
    log_serial_rejected(line)

    return False


# =========================
# CART VALIDATION
# =========================

def validate_cart(cart, products):
    """
    Check cart data before checkout.
    """

    if not isinstance(cart, dict):
        return False

    for name, item in cart.items():

        if name not in [
            product.get("name")
            for product in products.values()
        ]:
            log_security_warning(
                f"UNKNOWN_CART_PRODUCT | product={name}"
            )

            return False

        if not isinstance(item, dict):
            return False

        qty = item.get("qty")

        if not isinstance(qty, int) or qty <= 0:

            log_security_warning(
                f"INVALID_QUANTITY | product={name}"
            )

            return False

        # Check that cart price matches
        # trusted backend price
        if not validate_price(
            name,
            item.get("price"),
            products
        ):
            return False

    return True


# =========================
# SECURE TOTAL CALCULATION
# =========================

def calculate_secure_total(cart, products):
    """
    Calculate total using trusted backend prices.
    Never trust frontend prices.
    """

    if not validate_cart(
        cart,
        products
    ):
        return None

    total = 0

    for name, item in cart.items():

        trusted_price = None

        for product in products.values():

            if product.get("name") == name:
                trusted_price = float(
                    product.get("price")
                )
                break

        if trusted_price is None:
            return None

        total += (
            trusted_price *
            item["qty"]
        )

    return round(total, 2)