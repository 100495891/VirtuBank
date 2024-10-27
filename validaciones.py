import re
class Validaciones:
    def __init__(self, dni):
        self.dni = dni
    def validar_dni(self):
        if len(self.dni) != 9:
            return False
        try:
            numero = int(self.dni[:8])
        except ValueError:
            return False

        letra = self.dni[8].upper()
        c = "TRWAGMYFPDXBNJZSQVHLCKE"
        letra_esperada = c[numero % 23]

        return letra == letra_esperada

    def validar_nombre_apellido(self, nombre_apellido):
        return nombre_apellido.isalpha()

    def validar_telefono(self, telefono):
        if len(telefono) != 9:
            return False
        return telefono.isdigit()

    def validar_correo(self, correo):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, correo) is not None