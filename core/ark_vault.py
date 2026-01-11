import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class ArkVault:
    """
    Handles local, on-device encryption for sensitive metabolic and attention data.
    The key is derived from the user's mnemonic seed, ensuring only the device
    with the seed can decrypt the data.
    """
    
    def __init__(self, seed_phrase):
        self.key = self._derive_key(seed_phrase)
        
    def _derive_key(self, seed_phrase):
        salt = b'ose_ark_salt' # In production, this should be unique per node
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(seed_phrase.encode())

    def encrypt(self, data):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data.encode()) + encryptor.finalize()
        return base64.b64encode(iv + encrypted).decode()

    def decrypt(self, encrypted_data):
        raw = base64.b64decode(encrypted_data)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return (decryptor.update(encrypted) + decryptor.finalize()).decode()

def secure_local_save(filename, data, seed_phrase):
    """Saves encrypted data to a local file."""
    av = ArkVault(seed_phrase)
    encrypted = av.encrypt(data)
    with open(filename, 'w') as f:
        f.write(encrypted)

def secure_local_load(filename, seed_phrase):
    """Loads and decrypts data from a local file."""
    if not os.path.exists(filename):
        return None
    av = ArkVault(seed_phrase)
    with open(filename, 'r') as f:
        encrypted = f.read()
    return av.decrypt(encrypted)
