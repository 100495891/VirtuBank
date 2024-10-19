import os, base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
def registro(password, salt):
    kdf = Scrypt(salt, 32, 2**14, 8, 1)
    key = kdf.derive(password.encode())
    return key

def autenticacion(password, password_codificada, salt):
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 14,
        r=8,
        p=1,
    )
    try:
        # Verificar la contraseña
        kdf.verify(password.encode(), password_codificada)
        return True  # La contraseña es correcta
    except Exception:
        return False  # La contraseña es incorrecta

def generar_clave_chacha(password_codificada, salt2):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt2,
        iterations=480000,
    )
    return kdf.derive(password_codificada)

def cifrar(dni, datos_cifrar, clave):
    chacha = ChaCha20Poly1305(clave)
    nonce = os.urandom(12)
    datos_cifrar = str(datos_cifrar).encode()
    aad = dni.encode()
    ct = chacha.encrypt(nonce, datos_cifrar, aad)
    #chacha.decrypt(nonce, ct, aad)
    return nonce, ct

def descifrar(dni, ct, clave, nonce):
    chacha = ChaCha20Poly1305(clave)
    aad = dni.encode()
    return chacha.decrypt(nonce, ct, aad)