import base64

import usuario, codificacion

def datos_cifrar_descifrar(dato_nonces, dni, password):
    usuarios = usuario.carga_usuarios()
    nonces = usuario.carga_nonces()

    salt2 = base64.b64decode(usuarios[dni]['salt2'])
    nonce = base64.b64decode(nonces[dni][dato_nonces])

    clave = codificacion.generar_clave_chacha(password, salt2)

    return clave, nonce, usuarios


def revisar_datos(dni, password, dato_usuarios, dato_nonces):
    clave, nonce, usuarios = datos_cifrar_descifrar(dato_nonces, dni, password)
    dato_cifrado = base64.b64decode(usuarios[dni][dato_usuarios])
    dato_descifrado = codificacion.descifrar(dni, dato_cifrado, clave, nonce)
    return dato_descifrado


def actualizar_datos(dni, password, dato_actualizado, dato_usuarios, dato_nonces):
    clave, nonce, usuarios = datos_cifrar_descifrar(dato_nonces, dni, password)
    usuarios[dni][dato_usuarios] = codificacion.cifrar(dni, str(dato_actualizado), clave, nonce)
    usuario.guardar_usuarios(usuarios)