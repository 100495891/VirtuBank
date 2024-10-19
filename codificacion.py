import os, base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
def registro_autenticacion(password):
    salt = os.urandom(16)
    kdf = Scrypt(salt, 32, 2**14, 8, 1)
    key = kdf.derive(password.encode())
    return key, salt

def generar_clave_chacha(salt):
    return base64.b64encode(salt.encode()).decode('utf-8')

def cifrado_autenticado(dni, datos_cifrar, clave):
    chacha = ChaCha20Poly1305(clave.encode())
    nonce = os.urandom(12)
    datos_cifrar = datos_cifrar.encode()
    aad = dni.encode()
    ct = chacha.encrypt(nonce, datos_cifrar, aad)
    chacha.decrypt(nonce, ct, aad)
    return nonce, ct