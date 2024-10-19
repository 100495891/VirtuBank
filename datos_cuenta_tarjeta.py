import base64

import usuario, codificacion

def revisar_datos(dni, dato_usuarios, dato_nonces):
    usuarios = usuario.carga_usuarios()
    nonces = usuario.carga_nonces()
    password_codificada = base64.b64decode(usuarios[dni]['password_codificada'])
    salt2 = base64.b64decode(usuarios[dni]['salt2'])
    nonce = base64.b64decode(nonces[dni][dato_nonces])
    clave = codificacion.generar_clave_chacha(password_codificada, salt2)
    dato_cifrado = base64.b64decode(usuarios[dni][dato_usuarios])
    dato_descifrado = codificacion.descifrar(dni, dato_cifrado, clave, nonce)
    return dato_descifrado

