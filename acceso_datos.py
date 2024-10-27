import base64
from codificacion import Codificacion
from usuario import Usuario
class GestorDatos:
    def __init__(self, dni, password):
        self.usuario = Usuario(dni, password)
        self.usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        self.nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
        self.codificacion = Codificacion()

    def datos_cifrar_descifrar(self, dato_nonces):
        """Cogemos el salt2 del diccionario de usuario y el nonce del dato que queremos descifrar, devolvemos la clave
        y el nonce, ed decir, todos los datos necesarios para descrifrar un dato """

        salt2 = base64.b64decode(self.usuarios[self.usuario.dni]['salt2'])
        nonce = base64.b64decode(self.nonces[self.usuario.dni][dato_nonces])

        clave = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)

        return clave, nonce


    def revisar_datos(self, dato_usuarios, dato_nonces):
        """Método para revisar datos de un usuario"""
        clave, nonce = self.datos_cifrar_descifrar(dato_nonces)
        dato_cifrado = base64.b64decode(self.usuarios[self.usuario.dni][dato_usuarios])
        dato_descifrado = self.codificacion.descifrar(self.usuario.dni, dato_cifrado, clave, nonce)
        return dato_descifrado


    def actualizar_datos(self, dato_actualizado, dato_usuarios, dato_nonces):
        """Actualizamos el json con un nuevo dato"""
        clave, nonce = self.datos_cifrar_descifrar(dato_nonces)
        self.usuarios[self.usuario.dni][dato_usuarios] = self.codificacion.cifrar(self.usuario.dni, str(dato_actualizado), clave, nonce)
        self.usuario.guardar_json(self.usuario.ARCHIVO_USUARIOS, self.usuarios)


    def transacciones(self, cifra, operacion):
        saldo = self.revisar_datos('saldo_disponible', 'saldo_disponible')
        if operacion == '+':
            saldo = float(saldo) + cifra

        else:
            if float(saldo) < cifra:
                print("No dispone de suficiente saldo")
                return False, saldo
            else:
                saldo = float(saldo) - cifra

        self.actualizar_datos(saldo, 'saldo_disponible', 'saldo_disponible')
        return True, saldo

    def nombre_titular(self):
        # Devuelve el nombre completo del titular
        try:
            nombre = self.revisar_datos('nombre', 'nombre')
            apellido1 = self.revisar_datos('apellido1', 'apellido1')
            apellido2 = self.revisar_datos('apellido2', 'apellido2')

            return f"{nombre} {apellido1} {apellido2}"
        except Exception as e:
            raise RuntimeError(f"Error al obtener el nombre del titular: {e}")