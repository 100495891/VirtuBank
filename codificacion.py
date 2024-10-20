import base64
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
def registro(password, salt):
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1)
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

def cifrar(dni, datos_cifrar, clave, nonce):
    chacha = ChaCha20Poly1305(clave)
    if nonce is None:
        nonce = os.urandom(12)
        nonce_nuevo = True
    else:
        nonce_nuevo = False
    datos_cifrar = datos_cifrar.encode()
    aad = dni.encode()
    ct = chacha.encrypt(nonce, datos_cifrar, aad)
    ct_b64 = base64.b64encode(ct).decode('utf-8')
    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    if nonce_nuevo:
        return nonce_b64, ct_b64
    else:
        return ct_b64

def descifrar(dni, ct, clave, nonce):
    chacha = ChaCha20Poly1305(clave)
    aad = dni.encode()
    datos_descifrados = chacha.decrypt(nonce, ct, aad)
    return datos_descifrados.decode('utf-8')