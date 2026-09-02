import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class SecurityUtils:
    @staticmethod
    def get_cipher():
        """
        Encryption Cipher banata hai.
        Priority:
        1. Environment Variable (Best for Production)
        2. Error if not set (No insecure fallback)
        """
        key = os.getenv("ENCRYPTION_KEY")

        if not key:
            raise ValueError(
                "ENCRYPTION_KEY environment variable is not set. "
                "Please set a valid Fernet key in your .env file."
            )

        try:
            if isinstance(key, str):
                key = key.encode()
            return Fernet(key)
        except Exception:
            raise ValueError(
                "Invalid ENCRYPTION_KEY format. "
                "Please generate a valid Fernet key using: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

    @staticmethod
    def encrypt(data: str) -> str:
        """String ko encrypt karke encrypted string return karta hai."""
        if not data:
            return ""
        try:
            cipher = SecurityUtils.get_cipher()
            return cipher.encrypt(data.encode()).decode()
        except Exception as e:
            print(f"🔐 Encryption Failed: {e}")
            raise e

    @staticmethod
    def decrypt(token: str) -> str:
        """Encrypted string ko wapis original text mein lata hai."""
        if not token:
            return ""
        try:
            cipher = SecurityUtils.get_cipher()
            return cipher.decrypt(token.encode()).decode()
        except Exception as e:
            print(f"🔐 Decryption Failed: {e}")
            raise ValueError("Invalid Key or Corrupted Data")