import logging
import os

# =========================
# LOG FOLDER
# =========================

LOG_FOLDER = "logs"

os.makedirs(LOG_FOLDER, exist_ok=True)


# =========================
# SECURITY LOG FILE
# =========================

LOG_FILE = os.path.join(
    LOG_FOLDER,
    "security.log"
)


# =========================
# LOGGER SETUP
# =========================

security_logger = logging.getLogger("SmartTrolleySecurity")

security_logger.setLevel(logging.INFO)


# Avoid duplicate handlers
if not security_logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(formatter)

    security_logger.addHandler(
        file_handler
    )


# =========================
# SECURITY LOG FUNCTIONS
# =========================

def log_event(event, details=""):
    """
    General security/event logging.
    """

    if details:
        message = f"{event} | {details}"
    else:
        message = event

    security_logger.info(message)


def log_login_success(username):
    log_event(
        "LOGIN_SUCCESS",
        f"user={username}"
    )


def log_login_failed(username):
    log_event(
        "LOGIN_FAILED",
        f"user={username}"
    )


def log_logout(username):
    log_event(
        "LOGOUT",
        f"user={username}"
    )


def log_rfid_accepted(uid, product):
    log_event(
        "RFID_ACCEPTED",
        f"uid={uid} | product={product}"
    )


def log_rfid_rejected(uid):
    log_event(
        "RFID_REJECTED",
        f"uid={uid}"
    )


def log_price_validation(product, price):
    log_event(
        "PRICE_VALIDATION",
        f"product={product} | price={price}"
    )


def log_checkout(total):
    log_event(
        "CHECKOUT_SUCCESS",
        f"total={total:.2f}"
    )


def log_serial_rejected(data):
    log_event(
        "SERIAL_INPUT_REJECTED",
        f"data={data}"
    )


def log_security_warning(message):
    log_event(
        "SECURITY_WARNING",
        message
    )