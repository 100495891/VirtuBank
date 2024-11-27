import base64
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding

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

    def cifrar(self, dni, datos_cifrar, clave):
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

        return nonce_b64, ct_b64

    def descifrar(self, dni, ct, clave, nonce):
        chacha = ChaCha20Poly1305(clave)
        aad = dni.encode()
        datos_descifrados = chacha.decrypt(nonce, ct, aad)
        return datos_descifrados.decode('utf-8')

    def generar_clave_privada_rsa(self):
        # Generamos la clave privada
        clave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        return clave_privada

    def cifrar_clave_privada(self, clave_privada, password):
        # Ciframos la clave privada con la contraseña del usuario
        pem = clave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return pem

    def serializar_clave_publica(self, clave_privada):
        # Generamos la clave pública a partir de la privada
        clave_publica = clave_privada.public_key()
        pem = clave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem

    def firmar_mensaje(self, clave_privada, mensaje):
        # Firmamos el mensaje con la clave privada del usuario
        firma = clave_privada.sign(
            mensaje,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(firma).decode('utf-8')

    def verificar_firma(self, clave_publica_pem, mensaje, firma):
        # Verificamos la firma con la clave pública de la persona que firmó (la cogemos del certificado)
        clave_publica = serialization.load_pem_public_key(clave_publica_pem)
        firma = base64.b64decode(firma)
        try:
            clave_publica.verify(
                firma,
                mensaje,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
