from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.x509 import load_pem_x509_certificates
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import traceback


def generar_clave_privada_rsa():
    # Generamos la clave privada
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return clave_privada

def cifrar_clave_privada(clave_privada, password):
    # Ciframos la clave privada con la contraseña del usuario
    pem = clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8"))
    )
    return pem

def firmar_mensaje(clave_privada, mensaje):
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
    return base64.b64encode(firma)

def verificar_firma(clave_publica, mensaje, firma):
    # Verificamos la firma con la clave pública de la persona que firmó (la cogemos del certificado)
    firma_decod = base64.b64decode(firma)
    try:
        clave_publica.verify(
            firma_decod,
            mensaje.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        print("Error: Firma inválida")
        traceback.print_exc()
    except Exception as e:
        print(f"Error al verificar la firma: {e}")
        traceback.print_exc()
    
def generar_csr(clave_privada, dni):
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

    with open("certificados_openssl/AC1/solicitudes/csr.pem", 'wb') as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

 # para firmar el certificado:
 # primero comprobamos la solicitud
 # AC1> openssl req -in ./solicitudes/csr.pem -text -noout
 # AC1> openssl ca -in ./solicitudes/csr.pem -notext -config ./openssl.cnf
 # AC1> cp ./nuevoscerts/{num}.pem ../certificados/cert_{dni}.pem

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
        print(f"Error al verificar la firma del certificado del usuario: {e}")    


def verificaciones(dni, telefono):
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
    # Verificamos que certAC1 ha sido firmado por él mismo
    verificar_certificado(clave_publica_certAC1, certAC1)



