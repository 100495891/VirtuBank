import re

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

def validar_nombre_apellido(nombre_apellido):
    return nombre_apellido.isalpha()

def validar_telefono(telefono):
    if len(telefono) != 9:
        return False
    return telefono.isdigit()

def validar_correo(correo):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, correo) is not None