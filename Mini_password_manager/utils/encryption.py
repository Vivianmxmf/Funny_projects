from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class Encryptor:
    def __init__(self):
        self.salt = os.urandom(16)
    
    def generate_key(self, master_password):
        """Generate encryption key from master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def encrypt_data(self, data, key):
        """Encrypt string data"""
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data, key):
        """Decrypt string data"""
        try:
            f = Fernet(key)
            return f.decrypt(encrypted_data.encode()).decode()
        except:
            return "**Decryption Failed**" 