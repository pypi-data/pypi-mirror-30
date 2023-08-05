# OS
from datetime import datetime, timedelta

# Database
from modislock_webservice.models import Settings, PinKey, TotpKey, U2fKey

# Misc
from random import randint

# Google authenticator
from pyotp import random_base32

# Password
from werkzeug.security import generate_password_hash
import uuid


def gen_pass_token(secret_pwd):
    """Password Hash based on provided password

    :param secret_pwd:
    :return:
    """
    hashed_password = generate_password_hash(secret_pwd)
    expires = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(days=30)
    token = str(uuid.uuid4())

    return hashed_password, expires, token


def gen_unique_pin():
    """
    Generates PIN

    """
    digits = Settings.query.with_entities(Settings.settings_value, Settings.units) \
        .filter(Settings.settings_name == 'PIN_PLACES').first()
    digits = int(digits.settings_value)
    debug_count = 0

    pin_keys = PinKey.query.with_entities(PinKey.key)
    totp_keys = TotpKey.query.with_entities(TotpKey.key)
    u2f_keys = U2fKey.query.with_entities(U2fKey.key)

    all_keys = pin_keys.union(totp_keys).union(u2f_keys)  # Union all keys in all protocols together
    pins = list()

    for pin in all_keys:
        pins.append(pin.key)

    pin_code = 0

    for i in range(int('9' * digits)):
        debug_count += 1
        pin_code = randint(int('1' + ('0' * (digits - 1))), int('9' * digits))

        if pin_code not in pins:
            break

    if debug_count >= int('9' * digits):
        return 0
    else:
        return pin_code


def gen_unique_webcode():
    return random_base32()
