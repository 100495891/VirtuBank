import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def codificar_password(password):
    salt = os.urandom(16)
    kdf = Scrypt(salt, 32, 2**14, 8, 1)
    key = kdf.derive(password)
    return key
