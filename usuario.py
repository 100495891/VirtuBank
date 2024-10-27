import json, os, base64, random
from codificacion import Codificacion
from cuenta import CuentaBancaria
from validaciones import Validaciones

class Usuario:

    ARCHIVO_USUARIOS = 'usuarios.json'
    ARCHIVO_NONCES = 'nonces.json'

    def __init__(self, dni, password):
        self.dni = dni
        self.password = password
        self.codificacion = Codificacion()
        self.cuenta_bancaria = CuentaBancaria()
        self.validaciones = Validaciones(dni)

    def carga_json(self, archivo):
        # Carga datos desde un archivo JSON
        try:
            if os.path.exists(archivo):
                with open(archivo, 'r') as file:
                    return json.load(file)
            return {}
        except json.JSONDecodeError:
            print("Error al cargar el JSON")


    def guardar_json(self, archivo, datos):
        # Guarda datos en un archivo JSON
        try:
            with open(archivo, 'w') as file:
                json.dump(datos, file, indent=4)
        except IOError as e:
            raise RuntimeError(f"Error al guardar usuarios: {e}")

    def validar_datos(self, nombre, apellido1, apellido2, telefono, correo_electronico):
        # Valida la información del usuario
        if not self.validaciones.validar_dni():
            raise ValueError('DNI inválido')
        if not self.validaciones.validar_nombre_apellido(nombre):
            raise ValueError('Nombre Inválido')
        if not self.validaciones.validar_nombre_apellido(apellido1):
            raise ValueError('Primer Apellido Inválido')
        if not self.validaciones.validar_nombre_apellido(apellido2):
            raise ValueError('Segundo Apellido Inválido')
        if not self.validaciones.validar_telefono(telefono):
            raise ValueError('Teléfono Inválido')
        if not self.validaciones.validar_correo(correo_electronico):
            raise ValueError('Correo electrónico inválido')

    def cifrar_datos(self, clave, datos):
        # Cifra todos los datos del usuario y los devuelve en un diccionario
        return {key: self.codificacion.cifrar(self.dni, valor, clave, None) for key, valor in datos.items()}

    def registro_usuario(self, nombre, apellido1, apellido2, telefono, correo_electronico):
        try:
            # Validamos los datos del usuario
            self.validar_datos(nombre, apellido1, apellido2, telefono, correo_electronico)

            # Comprobamos que no exista el usuario ni sus nonces
            usuarios = self.carga_json(self.ARCHIVO_USUARIOS)
            nonces = self.carga_json(self.ARCHIVO_NONCES)
            if self.dni in usuarios or self.dni in nonces:
                raise ValueError("El usuario ya existe")


            # Creamos los dos salts, 1 para la contraseña del usuario y otro para los datos de la cuenta
            salt = os.urandom(16)
            salt2 = os.urandom(16)

            #Codificamos la contraseña del usuario (en bytes)
            password_token = self.codificacion.registro(self.password, salt)

            # Datos del usuario sin cifrar
            datos = {
                'nombre': nombre,
                'apellido1': apellido1,
                'apellido2': apellido2,
                'telefono': telefono,
                'correo_electronico': correo_electronico,
                'saldo_disponible': '0',
                'numero_cuenta': self.cuenta_bancaria.generar_numero_cuenta(),
                'tarjeta': self.cuenta_bancaria.generar_numero_tarjeta_visa(),
                'fecha_expiracion_tarjeta': self.cuenta_bancaria.generar_fecha_expiracion(),
                'cvv': ''.join(random.choices('0123456789', k=3))
            }


            # Generamos la clave para el cifrado autenticado a partir de la contraseña y el salt 2
            clave = self.codificacion.generar_clave_chacha(self.password, salt2)
            datos_cifrados = self.cifrar_datos(clave, datos)

            # Almacenamiento de usuario
            usuarios[self.dni] = {
                'password_token': base64.b64encode(password_token).decode('utf-8'),
                'salt': base64.b64encode(salt).decode('utf-8'),
                'salt2': base64.b64encode(salt2).decode('utf-8'),
                **{k: v[1] for k, v in datos_cifrados.items()}
            } # v es una tupla (nonce, dato) por eso cogemos la posicion 1 (dato)

            # Almacenamiento de nonces
            nonces[self.dni] = {k: v[0] for k, v in datos_cifrados.items()}

            # Guardamos los datos cifrados en los json
            self.guardar_json(self.ARCHIVO_USUARIOS, usuarios)
            self.guardar_json(self.ARCHIVO_NONCES, nonces)

            return f"El usuario con DNI {self.dni} se ha registrado correctamente"

        except Exception as e:
            raise RuntimeError(f"Error en el registro de usuario: {e}")

    def login_usuario(self):
        # Inicio de sesión de usuario
        try:
            usuarios = self.carga_json(self.ARCHIVO_USUARIOS)
            if self.dni not in usuarios:
                return False
            salt = base64.b64decode(usuarios[self.dni]['salt'] )
            password_token = base64.b64decode(usuarios[self.dni]['password_token'])
            return self.codificacion.autenticacion(self.password, password_token, salt)
        except Exception as e:
            raise RuntimeError(f"Error en el inicio de sesión: {e}")

