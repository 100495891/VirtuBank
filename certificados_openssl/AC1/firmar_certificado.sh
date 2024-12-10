#!/bin/bash

# Ruta del archivo de configuración de OpenSSL
OPENSSL_CONFIG="./openssl.cnf"

# Leer el número desde el archivo 'serial' y el dni desde el archivo {serial}.txt
SERIAL=$(cat "./serial")
DNI=$(cat "./dnis/${SERIAL}.txt")

# Ruta del CSR (solicitud de firma de certificado)
CSR_PATH="./solicitudes/csr_${DNI}.pem"

# Ruta del archivo de certificado emitido por la CA
CERT_PATH="./nuevoscerts/${SERIAL}.pem"

# Ruta de destino para copiar el certificado emitido
DEST_CERT_PATH="../certificados/cert_${DNI}.pem"

# Mostrar el CSR (solicitud de firma de certificado)
echo "Mostrando el CSR (solicitud de firma de certificado)..."
openssl req -in "$CSR_PATH" -text -noout

# Firmar el CSR con la CA
echo "Firmando el CSR con la CA..."
openssl ca -in "$CSR_PATH" -notext -config "$OPENSSL_CONFIG"

# Copiar el certificado firmado al destino
echo "Copiando el certificado firmado al destino..."
cp "$CERT_PATH" "$DEST_CERT_PATH"

# Eliminar el CSR una vez generado el certificado
echo "Eliminando el CSR..."
rm "$CSR_PATH"

echo "Certificado firmado y guardado en: $DEST_CERT_PATH"