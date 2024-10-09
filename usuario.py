import json, codificacion, os, validaciones

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
    usuarios[dni] = codificacion.codificar_password(password)
    guardar_usuarios(usuarios)
    print(f"El usuario con DNI {dni} se ha registrado correctamente")

def login_usuario(dni, password):
    usuarios = carga_usuarios()
    if dni not in usuarios:
        return False
    return usuarios[dni] == codificacion.codificar_password(password)