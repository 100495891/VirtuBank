import json, hashlib, os
ARCHIVO_USUARIOS = 'usuarios.json'
def codificar_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def carga_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r') as file:
            return json.load(file)
    return {}

def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, 'w') as file:
        json.dump(usuarios, file, indent=4)

def validar_dni(dni):
    if len(dni) != 9:
        return False
    try:
        numero = int(dni[:8])
    except ValueError:
        return False

    letra = dni[8].upper()
    c = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra_esperada = c[numero % 23]

    return letra == letra_esperada

def registro_usuario(dni, password):
    if  not validar_dni(dni):
        raise ValueError('DNI inválido')
    usuarios = carga_usuarios()
    if dni in usuarios:
        raise ValueError("El usuario ya existe")
    usuarios[dni] = codificar_password(password)
    guardar_usuarios(usuarios)
    print(f"El usuario con DNI {dni} se ha registrado correctamente")

def login_usuario(dni, password):
    usuarios = carga_usuarios()
    if dni not in usuarios:
        return False
    return usuarios[dni] == codificar_password(password)