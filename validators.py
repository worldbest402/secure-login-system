import re
from typing import Tuple, Dict

# Input length limits to prevent DoS attacks
MAX_EMAIL_LENGTH = 254  # RFC 5321
MAX_PASSWORD_LENGTH = 128

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email(email: str) -> bool:
    """
    Validate email format using a strict regex.
    Also enforces length limits to prevent DoS attacks.
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False
    return bool(EMAIL_REGEX.match(email))


def validate_password(password: str) -> bool:
    """
    Enforce a basic password policy:
    - Minimum length: 10
    - Maximum length: 128 (prevent DoS attacks)
    - At least one letter
    - At least one number
    """
    if not password or len(password) < 10 or len(password) > MAX_PASSWORD_LENGTH:
        return False

    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)

    return has_letter and has_number


def validate_registration_input(email: str, password: str) -> Tuple[bool, Dict[str, str]]:
    """
    Validate registration input fields.
    Returns (is_valid, errors)
    """
    errors = {}

    if not validate_email(email):
        errors["email"] = "Invalid email format."

    if not validate_password(password):
        # This message is user-facing guidance, not a hardcoded credential.
        # Instruct Bandit to ignore this line's B105 warning.
        errors["password"] = "Does not meet requirements."  # nosec: B105

    return (len(errors) == 0, errors)


def validate_login_input(email: str, password: str) -> Tuple[bool, Dict[str, str]]:
    """
    Validate login input fields.
    Checks format and presence to prevent invalid data processing.
    """
    errors = {}

    if not email or not password:
        errors["general"] = "Email and password are required."
    elif not validate_email(email):
        errors["email"] = "Invalid email format."
    elif len(password) < 1 or len(password) > MAX_PASSWORD_LENGTH:
        errors["password"] = "Invalid password length."

    return (len(errors) == 0, errors)
