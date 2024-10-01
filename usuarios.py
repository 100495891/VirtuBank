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

def registro_usuario(nombre_usuario, password):
    usuarios = carga_usuarios()
    if nombre_usuario in usuarios:
        raise ValueError("El usuario ya existe")
    usuarios[nombre_usuario] = codificar_password(password)
    guardar_usuarios(usuarios)
    print(f"El usuario {nombre_usuario} se ha registrado correctamente")

def login_usuario(nombre_usuario, password):
    usuarios = carga_usuarios()
    if nombre_usuario not in usuarios:
        return False
    return usuarios[nombre_usuario] == codificar_password(password)