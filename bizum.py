import base64
from datetime import datetime
from codificacion import Codificacion
from usuario import Usuario
from acceso_datos import GestorDatos

class Bizum:
    #DESCARGAR DATOS USUARIOS
    ARCHIVO_BIZUM = 'bizums.json'
    ARCHIVO_OPERACIONES_PENDIENTES = 'operaciones_pendientes.json'
    #*************master key*************************
    master_key = "apbeuiqjgds75dk10d8n"
    def __init__(self, dni, password):
        self.usuario = Usuario(dni, password)
        self.gestor_datos = GestorDatos(dni, password)
        self.telefono = self.gestor_datos.revisar_datos('telefono', 'telefono')
        self.codificacion = Codificacion()

    def registrarse_bizum(self):
        bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        if not self.usuario.login_usuario():
            return "Error: Contraseña incorrecta"

        if self.telefono in bizums:
            return "Error: Ya está registrado/a en bizum"

        bizums[self.telefono] = {
            'dni' : self.usuario.dni,
            'transacciones': {}
        }
        self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
        return "Registrado en bizum exitosamente"


    def realizar_bizum(self, cantidad, telefono_destino):
        bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        salt2 = usuarios[self.usuario.dni]['salt2'].encode()
        # Comprobamos que el número no sea el mismo que el del usuario que envía el bizum
        if self.telefono == telefono_destino:
            return "Error: No se puede enviar un bizum a usted mismo"
        # Comprobamos que el que envía el dinero esté registrado en bizum
        if self.telefono not in bizums:
            return "Error: no está registrado en bizum."
        # Comprobamos que el que recibe el dinero esté registrado en bizum
        if telefono_destino not in bizums:
            return "Error: el usuario al que quiere envíar el bizum no está registrado en bizum."
        dni_destinatario = bizums[telefono_destino]['dni']

        # Comprobamos que se realice correctamente la transacción
        if self.gestor_datos.transacciones(cantidad, '-')[0]:
            # Ciframos la contraseña con el algoritmo PBKDF2HMAC que usaremos como clave para cifrar los datos
            clave = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
            # Ciframos el nonce y la cantidad que hemos enviado
            nonce_cantidad_origen, cantidad_cifrada_origen = self.codificacion.cifrar(self.usuario.dni, str(-cantidad), clave, None)
            # Si no se ha realizado un bizum antes con esta cuenta a un número determinado se crea una lista para guardar todas las transacciones futuras
            if telefono_destino not in bizums[self.telefono]['transacciones']:
                bizums[self.telefono]['transacciones'][telefono_destino] = []
            # Guardamos los datos de la transacción
            bizums[self.telefono]['transacciones'][telefono_destino].append({'dinero': cantidad_cifrada_origen,
                                                                              'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                                              'nonce': nonce_cantidad_origen})
            # Metemos esta transacción en operaciones pendientes en la cuenta del usuario
            self.crear_operacion_pendiente(dni_destinatario, cantidad, telefono_destino)
            # Actualizamos el JSON
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
            return "Su bizum se ha realizado con éxito."
        return "No se ha podido hacer el bizum"

    def revisar_transacciones_operaciones(self, diccionario, identificador, pw_clave, dni):
        usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        salt2 = usuarios[self.usuario.dni]['salt2'].encode()
        for persona, list in diccionario[identificador]['transacciones'].items():
            print(f"\nBizums con: {persona}")

            for j, transaccion in enumerate(list, start = 1):
                clave = self.codificacion.generar_clave_chacha(pw_clave, salt2)
                dinero_cifrado = base64.b64decode(transaccion['dinero'])
                nonce = base64.b64decode(transaccion['nonce'])
                fecha = transaccion['fecha']
                dinero = self.codificacion.descifrar(dni, dinero_cifrado, clave, nonce)
                print(f"\nTransacción {j}:\nDinero: {dinero}\nFecha: {fecha}")

    def revisar_transacciones(self):
        bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        self.revisar_transacciones_operaciones(bizums, self.telefono, self.usuario.password, self.usuario.dni)

    def revisar_operaciones_pendientes(self):
        operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
        self.revisar_transacciones_operaciones(operaciones_pendientes, self.usuario.dni, self.master_key, self.usuario.dni)

    def crear_operacion_pendiente(self, dni, cantidad, telefono_destino):
        operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
        usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        salt2_destino = usuarios[dni]['salt2'].encode()
        # Generamos la clave haciendo uso de la master key
        clave = self.codificacion.generar_clave_chacha(self.master_key, salt2_destino)
        # Ciframos la cantidad recibida y el nonce de ese dato cifrado
        nonce_cantidad, cantidad_cifrada = self.codificacion.cifrar(dni, str(+cantidad), clave, None)
        # Si no existe el dni de destino en operaciones pendientes crea un diccionario y lo introduce
        if dni not in operaciones_pendientes:
            operaciones_pendientes[dni] = {
                'telefono' : telefono_destino,
                'transacciones': {}
            }
        # Si el telefono origen no tiene más operaciones
        if self.telefono not in operaciones_pendientes[dni]['transacciones']:
            operaciones_pendientes[dni]['transacciones'][self.telefono] = []

        operaciones_pendientes[dni]['transacciones'][self.telefono].append({'dinero': cantidad_cifrada,
                                                                           'fecha': datetime.now().strftime(
                                                                               "%d/%m/%Y %H:%M:%S"),
                                                                           'nonce': nonce_cantidad})
        self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, operaciones_pendientes)

    def cargar_operaciones_pendientes(self):
        operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
        usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        salt2 = usuarios[self.usuario.dni]['salt2'].encode()
        bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        cantidad = 0
        for telefono_origen, transacciones in operaciones_pendientes[self.usuario.dni]['transacciones'].items():
            for transaccion in transacciones:
                dinero_cifrado = base64.b64decode(transaccion['dinero'])
                fecha = transaccion['fecha']
                nonce = base64.b64decode(transaccion['nonce'])

                clave = self.codificacion.generar_clave_chacha(self.master_key, salt2)
                dinero = self.codificacion.descifrar(self.usuario.dni, dinero_cifrado, clave, nonce)

                clave2 = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
                nonce2, dinero_cifrado2 = self.codificacion.cifrar(self.usuario.dni, dinero, clave2, None)

                if telefono_origen not in bizums[self.telefono]['transacciones']:
                    bizums[self.telefono]['transacciones'][telefono_origen] = []
                bizums[self.telefono]['transacciones'][telefono_origen].append({'dinero': dinero_cifrado2,
                                                                        'fecha': fecha,
                                                                        'nonce': nonce2})
                cantidad += float(dinero)
            del operaciones_pendientes[self.usuario.dni]
            self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, operaciones_pendientes)
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
            self.gestor_datos.transacciones(cantidad, '+')
        return "Operaciones guardadas con éxito"

    def eliminar_cuenta(self):
        # Elimina la cuenta del usuario
        bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
            del usuarios[self.usuario.dni]
            del nonces[self.usuario.dni]
            if self.telefono in bizums:
                del bizums[self.telefono]
                self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
            self.usuario.guardar_json(self.usuario.ARCHIVO_USUARIOS, usuarios)
            self.usuario.guardar_json(self.usuario.ARCHIVO_NONCES, nonces)
            return "Cuenta borrada"
        except Exception as e:
            raise RuntimeError(f"Error al eliminar la cuenta: {e}")







