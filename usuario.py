import json, codificacion, os, validaciones, base64, cuenta, random
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

ARCHIVO_USUARIOS = 'usuarios.json'
ARCHIVO_NONCES = 'nonces.json'
def carga_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r') as file:
            return json.load(file)
    return {}

def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, 'w') as file:
        json.dump(usuarios, file, indent=4)
def registro_usuario(dni, password, nombre, apellido1, apellido2, telefono, correo_electronico): #añadir cod postal, ciudad y pais
    if  not validaciones.validar_dni(dni):
        raise ValueError('DNI inválido')
    if not validaciones.validar_nombre_apellido(nombre):
        raise ValueError('Nombre Inválido')
    if not validaciones.validar_nombre_apellido(apellido1):
        raise ValueError('Primer Apellido Inválido')
    if not validaciones.validar_nombre_apellido(apellido2):
        raise ValueError('Segundo Apellido Inválido')
    if not validaciones.validar_telefono(telefono):
        raise ValueError('Teléfono Inválido')
    if not validaciones.validar_correo(correo_electronico):
        raise ValueError('Correo electrónico inválido')

    usuarios = carga_usuarios()
    nonces = carga_nonces()
    if dni in usuarios or dni in nonces:
        raise ValueError("El usuario ya existe")

    password_codificada, salt = codificacion.registro_autenticacion(password)
    password_codificada_base64 = base64.b64encode(password_codificada).decode('utf-8')
    salt_base64 = base64.b64encode(salt).decode('utf-8')

    numero_cuenta = cuenta.generar_numero_cuenta()
    numero_tarjeta = cuenta.generar_numero_tarjeta_visa(),
    fecha_expiracion_tarjeta = "12/25",
    cvv = ''.join(random.choices('0123456789', k=3))

    clave = codificacion.generar_clave_chacha(salt_base64)
    nonce_cuenta, cuenta_cifrada = codificacion.cifrado_autenticado(dni, numero_cuenta, clave)
    nonce_tarjeta, tarjeta_cifrada = codificacion.cifrado_autenticado(dni, numero_tarjeta, clave)
    nonce_fecha_expiracion_tarjeta, fecha_expiracion_cifrada = codificacion.cifrado_autenticado(dni, fecha_expiracion_tarjeta, clave)
    nonce_cvv, cvv_cifrado = codificacion.cifrado_autenticado(dni, cvv, clave)

    # Cifrar fecha de expiracion y cvv y añadir al diccionario
    usuarios[dni] = {
        'password_codificada': password_codificada_base64,
        'salt': salt_base64,
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2,
        'telefono': telefono,
        'correo_electronico': correo_electronico,
        'numero_cuenta_cifrado': cuenta_cifrada,
        'tarjeta_cifrada': tarjeta_cifrada,
        'fecha_expiracion_cifrada': fecha_expiracion_cifrada,
        'cvv_cifrado': cvv_cifrado
    }
    nonces[dni] = {
        'nonce_cuenta': nonce_cuenta,
        'nonce_tarjeta': nonce_tarjeta,
        'nonce_fecha_expiracion_tarjeta': nonce_fecha_expiracion_tarjeta,
        'nonce_cvv': nonce_cvv
    }
    guardar_usuarios(usuarios)
    print(f"El usuario con DNI {dni} se ha registrado correctamente")

def login_usuario(dni, password):
    usuarios = carga_usuarios()
    if dni not in usuarios:
        return False
    salt = base64.b64decode(usuarios[dni]['salt'] )
    password_codificada = base64.b64decode(usuarios[dni]['password_codificada'])
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

def guardar_nonces(nonces):
    with open(ARCHIVO_NONCES, 'w') as file:
        json.dump(nonces, file, indent=4)

def carga_nonces():
    if os.path.exists(ARCHIVO_NONCES):
        with open(ARCHIVO_NONCES, 'r') as file:
            return json.load(file)
    return {}