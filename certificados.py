from cryptography import x509
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generar_certificado_raiz():
    # Generamos la clave privada para la CA
    clave_privada_ca = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    # Generamos un CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VirtuBank"),
        x509.NameAttribute(NameOID.COMMON_NAME, "virtubank.com"),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("virtubank.com"),
            x509.DNSName("www.virtubank.com"),
        ]),
    critical=False,
    ).sign(clave_privada_ca, hashes.SHA256())
    with open('ca_clave_privada', 'wb') as f:
        f.write(clave_privada_ca.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open('ca_certificado', 'wb') as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    