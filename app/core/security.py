import os
from cryptography.fernet import Fernet

KEY_FILE = "data/secret.key"

def load_or_generate_key():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_password(password: str) -> str:
    key = load_or_generate_key()
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    key = load_or_generate_key()
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()
