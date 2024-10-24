import json, codificacion, os, validaciones, base64, cuenta, random


ARCHIVO_USUARIOS = 'usuarios.json'
ARCHIVO_NONCES = 'nonces.json'


#DESCARGAR DATOS USUARIOS
def carga_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r') as file:
            return json.load(file)
    return {}


#GUARDAR USUARIOS EN EL JSON
def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, 'w') as file:
        json.dump(usuarios, file, indent=4)


#GUARDAR NONCES EN EL JSON
def guardar_nonces(nonces):
    with open(ARCHIVO_NONCES, 'w') as file:
        json.dump(nonces, file, indent=4)


#DESCARGAR NONCES
def carga_nonces():
    if os.path.exists(ARCHIVO_NONCES):
        with open(ARCHIVO_NONCES, 'r') as file:
            return json.load(file)
    return {}




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


    # Comprobamos que no exista el usuario ni sus nonces
    usuarios = carga_usuarios()
    nonces = carga_nonces()
    if dni in usuarios or dni in nonces:
        raise ValueError("El usuario ya existe")


    #Creamos los dos salts, 1 para la contraseña del usuario y otro para los datos de la cuenta
    salt = os.urandom(16)
    salt2 = os.urandom(16)

    #Codificamos la contraseña del usuario (en bytes)
    password_token = codificacion.registro(password, salt)

    # Le creamos al usuario datos de cuenta y de tarjeta
    numero_cuenta = cuenta.generar_numero_cuenta()
    numero_tarjeta = cuenta.generar_numero_tarjeta_visa()
    fecha_expiracion_tarjeta = cuenta.generar_fecha_expiracion()
    cvv = ''.join(random.choices('0123456789', k=3))


    # Generamos la clave para el cifrado autenticado a partir de la contraseña y el salt 2
    clave = codificacion.generar_clave_chacha(password, salt2)
    # Ciframos todos los datos de la cuenta, la tarjeta y el saldo
    nonce_cuenta, cuenta_cifrada = codificacion.cifrar(dni, numero_cuenta, clave, None)
    nonce_tarjeta, tarjeta_cifrada = codificacion.cifrar(dni, numero_tarjeta, clave, None)
    nonce_fecha_expiracion_tarjeta, fecha_expiracion_cifrada = codificacion.cifrar(dni, fecha_expiracion_tarjeta, clave, None)
    nonce_cvv, cvv_cifrado = codificacion.cifrar(dni, cvv, clave, None)
    nonce_saldo, saldo_inicial = codificacion.cifrar(dni, '0', clave, None)


    #Diccionario usuario
    usuarios[dni] = {
        'password_token': base64.b64encode(password_token).decode('utf-8'),
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2,
        'telefono': telefono,
        'correo_electronico': correo_electronico,
        'saldo_disponible': saldo_inicial,
        'numero_cuenta_cifrado': cuenta_cifrada,
        'tarjeta_cifrada': tarjeta_cifrada,
        'fecha_expiracion_cifrada': fecha_expiracion_cifrada,
        'cvv_cifrado': cvv_cifrado,
        'salt': base64.b64encode(salt).decode('utf-8'),
        'salt2': base64.b64encode(salt2).decode('utf-8')
    }
    #Diccionario Nonces
    nonces[dni] = {
        'nonce_saldo': nonce_saldo,
        'nonce_cuenta': nonce_cuenta,
        'nonce_tarjeta': nonce_tarjeta,
        'nonce_fecha_expiracion_tarjeta': nonce_fecha_expiracion_tarjeta,
        'nonce_cvv': nonce_cvv
    }

    guardar_usuarios(usuarios)
    guardar_nonces(nonces)
    print(f"El usuario con DNI {dni} se ha registrado correctamente")

def login_usuario(dni, password):
    usuarios = carga_usuarios()
    if dni not in usuarios:
        return False
    salt = base64.b64decode(usuarios[dni]['salt'] )
    password_token = base64.b64decode(usuarios[dni]['password_token'])
    return codificacion.autenticacion(password, password_token, salt)

def nombre_titular(dni):
    usuarios = carga_usuarios()
    nombre = usuarios[dni]['nombre']
    apellido1 = usuarios[dni]['apellido1']
    apellido2 = usuarios[dni]['apellido2']
    return f"{nombre} {apellido1} {apellido2}"