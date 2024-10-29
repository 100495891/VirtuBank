import base64
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Codificacion:

    def registro(self, password, salt):
        # Inicializamos la función de derivación de claves con nuestro salt
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1)
        # Derivamos la contraseña con el algoritmo Scrypt inicializado antes
        key = kdf.derive(password.encode())
        return key

    def autenticacion(self, password, password_token, salt):
        # Inicializamos ChaCha20 para poder verificar que la contraseña sea correcta
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2 ** 14,
            r=8,
            p=1,
        )
        try:
            # Verificar la contraseña
            kdf.verify(password.encode(), password_token)
            return True  # La contraseña es correcta
        except Exception:
            return False  # La contraseña es incorrecta

    def generar_clave_chacha(self, password, salt2):
        # Inicializamos PBKDF2HMAC para poder cifrar
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt2,
            iterations=480000,
        )
        # Derivamos la contraseña con el algoritmo PBKDF2HMAC inicializado antes
        return kdf.derive(password.encode())

    def cifrar(self, dni, datos_cifrar, clave, nonce):
        # Inicializamos ChaCha20 para poder cifrar
        chacha = ChaCha20Poly1305(clave)
        # Si no se proporciona eñ nonce, entonces creamos uno nuevo para ese dato
        if nonce is None:
            nonce = os.urandom(12)
            nonce_nuevo = True
        else:
            nonce_nuevo = False
        # Convertimos los datos a Bytes
        datos_cifrar = datos_cifrar.encode()
        aad = dni.encode()
        # Ciframos los datos con ChaCha20Poly1305
        ct = chacha.encrypt(nonce, datos_cifrar, aad)
        # Codificamos el texto cifrado y el nonce en Base64
        ct_b64 = base64.b64encode(ct).decode('utf-8')
        nonce_b64 = base64.b64encode(nonce).decode('utf-8')
        if nonce_nuevo:
            return nonce_b64, ct_b64
        else:
            return ct_b64

    def descifrar(self, dni, ct, clave, nonce):
        chacha = ChaCha20Poly1305(clave)
        aad = dni.encode()
        datos_descifrados = chacha.decrypt(nonce, ct, aad)
        return datos_descifrados.decode('utf-8')