import json, codificacion, os, validaciones, base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

ARCHIVO_USUARIOS = 'usuarios.json'
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
    if dni in usuarios:
        raise ValueError("El usuario ya existe")
    password_codificada, salt = codificacion.codificar_password(password)
    password_codificada_base64 = base64.b64encode(password_codificada).decode('utf-8')
    salt_base64 = base64.b64encode(salt).decode('utf-8')

    usuarios[dni] = {
        'password_codificada': password_codificada_base64,
        'salt': salt_base64,
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2,
        'telefono': telefono,
        'correo_electronico': correo_electronico
    }
    guardar_usuarios(usuarios)
    print(f"El usuario con DNI {dni} se ha registrado correctamente")

def login_usuario(dni, password):
    usuarios = carga_usuarios()
    if dni not in usuarios:
        print("DNI")
        return False
    print("no_dni")
    salt = base64.b64decode(usuarios[dni]['salt'] )
    password_codificada = base64.b64decode(usuarios[dni]['password_codificada'])
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 14,
        r=8,
        p=1,
    )
    print("verify:")
    try:
        # Verificar la contraseña
        kdf.verify(password.encode(), password_codificada)
        return True  # La contraseña es correcta
    except Exception:
        return False  # La contraseña es incorrecta
