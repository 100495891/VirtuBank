import os
import subprocess

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.x509 import load_pem_x509_certificates
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
from log_config import get_logger
from excepciones import ErrorGenerarClaveError, ErrorCifradoError, ErrorFirmaError, ErrorVerificarFirmaError, ErrorCertificadoError, ErrorCSRGenerationError, NoExisteRutaArchivo

logger = get_logger(__name__)


def generar_clave_privada_rsa():
    try:
        # Generamos la clave privada
        clave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        logger.info("Clave privada RSA generada correctamente")
        return clave_privada
    except Exception as e:
        raise ErrorGenerarClaveError(f"Error al generar la clave privada RSA: {e}")

def cifrar_clave_privada(clave_privada, password):
    try:
        # Ciframos la clave privada con la contraseña del usuario
        pem = clave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8"))
        )
        logger.info("Clave privada cifrada correctamente")
        return pem
    except Exception as e:
        raise ErrorCifradoError(f"Error al cifrar la clave privada: {e}")

def generar_guardar_clave_privada(dni, password):
    try:
        # Generamos la clave privada RSA que tendrá el usuario para firmar
        clave_privada = generar_clave_privada_rsa()
        # Deberíamos usar una password distinta pero para simplificar usamos la propia contraseña del usuario
        pwd_clave_privada = password
        # La ciframos y serializamos con la contraseña
        clave_privada_codificada = cifrar_clave_privada(clave_privada, pwd_clave_privada)
        # Guardamos la clave privada en un .pem
        filename = f"certificados_openssl/claves/key_{dni}.pem"
        with open(filename, 'wb') as pem_file:
            pem_file.write(clave_privada_codificada)
        logger.info("Clave privada guardada exitosamente")
        return clave_privada
    except Exception as e:
        raise ErrorGenerarClaveError(f"Error al guardar la clave privada: {e}")


def firmar_mensaje(clave_privada, mensaje):
    try:
        # Firmamos el mensaje con la clave privada del usuario
        mensaje_bytes = mensaje.encode("utf-8")
        firma = clave_privada.sign(
            mensaje_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logger.info(f"Mensaje firmado correctamente")
        return base64.b64encode(firma)
    except Exception as e:
        raise ErrorFirmaError(f"Error al firmar el mensaje: {e}")

def generar_guardar_firma(mensaje_firmar, clave_privada, dni):
    try:
        firma = firmar_mensaje(clave_privada, mensaje_firmar)

        # guardamos la firma
        with open(f"certificados_openssl/firmas/firma_{dni}.pem", "wb") as firma_pem:
            firma_pem.write(firma)
        logger.info(f"Firma guardada correctamente")
    except Exception as e:
        raise ErrorFirmaError(f"Error al guardar la firma: {e}")

def verificar_firma(clave_publica, mensaje, firma):
    try:
        # Verificamos la firma con la clave pública de la persona que firmó (la cogemos del certificado)
        firma_decod = base64.b64decode(firma)
        clave_publica.verify(
            firma_decod,
            mensaje.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logger.info("La firma se ha verificado correctamente")
    except InvalidSignature:
        raise ErrorVerificarFirmaError("Firma inválida")
    except Exception as e:
        raise ErrorVerificarFirmaError(f"Error al verificar la firma: {e}")
    
def generar_csr(clave_privada, dni):
    try:
        # Generamos un CSR
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"{dni}"),
            x509.NameAttribute(NameOID.COMMON_NAME, "."),
        ])).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("virtubank.com"),
                x509.DNSName("www.virtubank.com"),
            ]),
        critical=False,
        ).sign(clave_privada, hashes.SHA256())

        with open(f"certificados_openssl/AC1/solicitudes/csr_{dni}.pem", 'wb') as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))
        logger.info(f"CSR generado y guardado para {dni}")
    except Exception as e:
        raise ErrorCSRGenerationError(f"Error al generar el CSR: {e}")

def verificar_certificado(clave_publica_cert_raiz, cert_a_verificar):
    # En nuestro caso como solo hay un AC, solo tenemos el certificado de usuario y el raíz
    try:
        clave_publica_cert_raiz.verify(
            cert_a_verificar.signature,
            cert_a_verificar.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert_a_verificar.signature_hash_algorithm,
        )
    except Exception as e:
        raise ErrorCertificadoError(f"Error al verificar el certificado: {e}")

def verificaciones(dni, telefono):
    try:
        # Creamos el objeto del certificado del usuario
        with open(f"certificados_openssl/certificados/cert_{dni}.pem", "rb") as cert_pem:
            certificados = load_pem_x509_certificates(cert_pem.read())
        certUser = certificados[0]

        clave_publica_certUser = certUser.public_key()
        with open(f"certificados_openssl/firmas/firma_{dni}.pem", "rb") as firma_pem:
            firma = firma_pem.read().strip()
        verificar_firma(clave_publica_certUser, telefono, firma)

        with open(f"certificados_openssl/AC1/ac1cert.pem", "rb") as cert_pem:
            certificados = load_pem_x509_certificates(cert_pem.read())
        certAC1 = certificados[0]

        clave_publica_certAC1 = certAC1.public_key()
        # Verificamos que certUser ha sido firmado por AC1
        verificar_certificado(clave_publica_certAC1, certUser)
        logger.info("Verificación del certificado del usuario correcta")
        # Verificamos que certAC1 ha sido firmado por él mismo
        verificar_certificado(clave_publica_certAC1, certAC1)
        logger.info("Verificación de la Autoridad de Certificación correcta")
    except Exception as e:
        logger.error(f"Error en las verificaciones: {e}")
        raise


