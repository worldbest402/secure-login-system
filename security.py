import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    Returns a UTF-8 string suitable for database storage.
    Defensive: Catches hashing errors and logs them.
    """
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Password hashing failed") from e


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    Defensive: Catches verification errors and returns False safely.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False
if __name__ == "__main__":
    pw = "TestPassword123!"
    h = hash_password(pw)
    print("Hash:", h)
    print("Verify correct:", verify_password(pw, h))
    print("Verify wrong:", verify_password("wrong", h))
