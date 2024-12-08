import base64
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from log_config import get_logger
from excepciones import ErrorCifradoError

logger = get_logger(__name__)
class Codificacion:
    def registro(self, password, salt):
        try:
            # Inicializamos la función de derivación de claves con nuestro salt
            kdf = Scrypt(
                salt=salt,
                length=32,
                n=2**14,
                r=8,
                p=1)
            # Derivamos la contraseña con el algoritmo Scrypt inicializado antes
            key = kdf.derive(password.encode())
            logger.info("Clave generada correctamente para registro")
            return key
        except Exception as e:
            raise ErrorCifradoError(f"Error en registro de clave: {e}")

    def autenticacion(self, password, password_token, salt):
        try:
            # Inicializamos ChaCha20 para poder verificar que la contraseña sea correcta
            kdf = Scrypt(
                salt=salt,
                length=32,
                n=2 ** 14,
                r=8,
                p=1,
            )
            # Verificar la contraseña
            kdf.verify(password.encode(), password_token)
            logger.info("Contraseña autenticada correctamente")
            return True  # La contraseña es correcta
        except Exception as e:
            logger.error(f"Error en autenticación de contraseña: {e}")
            return False  # La contraseña es incorrecta

    def generar_clave_chacha(self, password, salt2):
        try:
            # Inicializamos PBKDF2HMAC para poder cifrar
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt2,
                iterations=480000,
            )
            # Derivamos la contraseña con el algoritmo PBKDF2HMAC inicializado antes
            clave = kdf.derive(password.encode())
            logger.info(f"Clave ChaCha generada correctamente")
            return clave
        except Exception as e:
            raise ErrorCifradoError(f"Error al generar clave ChaCha: {e}")

    def cifrar(self, dni, datos_cifrar, clave):
        try:
            # Inicializamos ChaCha20 para poder cifrar
            chacha = ChaCha20Poly1305(clave)
            # Si no se proporciona el nonce, entonces creamos uno nuevo para ese dato
            nonce = os.urandom(12)
            # Convertimos los datos a Bytes
            datos_cifrar = datos_cifrar.encode()
            aad = dni.encode()
            # Ciframos los datos con ChaCha20Poly1305
            ct = chacha.encrypt(nonce, datos_cifrar, aad)
            # Codificamos el texto cifrado y el nonce en Base64
            ct_b64 = base64.b64encode(ct).decode('utf-8')
            nonce_b64 = base64.b64encode(nonce).decode('utf-8')
            logger.info(f"Datos cifrados correctamente para el DNI: {dni}")
            return nonce_b64, ct_b64
        except Exception as e:
            raise ErrorCifradoError(f"Error al cifrar los datos: {e}")

    def descifrar(self, dni, ct, clave, nonce):
        try:
            chacha = ChaCha20Poly1305(clave)
            aad = dni.encode()
            datos_descifrados = chacha.decrypt(nonce, ct, aad)
            logger.info(f"Datos descifrados correctamente para el DNI: {dni}")
            return datos_descifrados.decode('utf-8')
        except Exception as e:
            raise ErrorCifradoError(f"Error al descifrar los datos: {e}")
