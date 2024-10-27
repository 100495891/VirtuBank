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
        self.bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
        self.operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
        self.usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
        self.nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
        self.telefono = self.gestor_datos.revisar_datos('telefono', 'telefono')
        self.salt2 = self.usuarios[self.usuario.dni]['salt2'].encode()
        self.codificacion = Codificacion()

    def registrarse_bizum(self):
        if not self.usuario.login_usuario():
            return "Error: Contraseña incorrecta"

        if self.telefono in self.bizums:
            return "Error: Ya está registrado/a en bizum"

        self.bizums[self.telefono] = {
            'dni' : self.usuario.dni,
            'transacciones': {}
        }
        self.usuario.guardar_json(self.ARCHIVO_BIZUM, self.bizums)
        return "Registrado en bizum exitosamente"


    def realizar_bizum(self, cantidad, telefono_destino):

        salt2 = self.usuarios[self.usuario.dni]['salt2'].encode()
        if self.telefono == telefono_destino:
            return "Error: No se puede enviar un bizum a usted mismo"
        if self.telefono not in self.bizums:
            return "Error: no está registrado en bizum."

        if telefono_destino not in self.bizums:
            return "Error: el usuario al que quiere envíar el bizum no está registrado en bizum."
        dni_destinatario = self.bizums[telefono_destino]['dni']


        if self.gestor_datos.transacciones(cantidad, '-')[0]:

            clave = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
            nonce_cantidad_origen, cantidad_cifrada_origen = self.codificacion.cifrar(self.usuario.dni, str(-cantidad), clave, None)
            if telefono_destino not in self.bizums[self.telefono]['transacciones']:
                self.bizums[self.telefono]['transacciones'][telefono_destino] = []
            self.bizums[self.telefono]['transacciones'][telefono_destino].append({'dinero': cantidad_cifrada_origen,
                                                                              'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                                              'nonce': nonce_cantidad_origen})

            self.crear_operacion_pendiente(dni_destinatario, cantidad, telefono_destino)
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, self.bizums)
            return "Su bizum se ha realizado con éxito."
        return "No se ha podido hacer el bizum"

    def revisar_transacciones_operaciones(self, diccionario, identificador, pw_clave, dni):

        for persona, list in diccionario[identificador]['transacciones'].items():
            print(f"\nBizums con: {persona}")

            for j, transaccion in enumerate(list, start = 1):
                clave = self.codificacion.generar_clave_chacha(pw_clave, self.salt2)
                dinero_cifrado = base64.b64decode(transaccion['dinero'])
                nonce = base64.b64decode(transaccion['nonce'])
                fecha = transaccion['fecha']
                dinero = self.codificacion.descifrar(dni, dinero_cifrado, clave, nonce)
                print(f"\nTransacción {j}:\nDinero: {dinero}\nFecha: {fecha}")

    def revisar_transacciones(self):
        self.revisar_transacciones_operaciones(self.bizums, self.telefono, self.usuario.password, self.usuario.dni)

    def revisar_operaciones_pendientes(self):
        self.revisar_transacciones_operaciones(self.operaciones_pendientes, self.usuario.dni, self.master_key, self.usuario.dni)

    def crear_operacion_pendiente(self, dni, cantidad, telefono_destino):
        clave = self.codificacion.generar_clave_chacha(self.master_key, self.salt2)
        nonce_cantidad, cantidad_cifrada = self.codificacion.cifrar(dni, str(+cantidad), clave, None)
        if self.telefono not in self.operaciones_pendientes:
            self.operaciones_pendientes[dni] = {
                'telefono' : telefono_destino,
                'transacciones': {}
            }
        if self.telefono not in self.operaciones_pendientes[dni]['transacciones']:
            self.operaciones_pendientes[dni]['transacciones'][self.telefono] = []

        self.operaciones_pendientes[dni]['transacciones'][self.telefono].append({'dinero': cantidad_cifrada,
                                                                           'fecha': datetime.now().strftime(
                                                                               "%d/%m/%Y %H:%M:%S"),
                                                                           'nonce': nonce_cantidad})
        self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, self.operaciones_pendientes)

    def cargar_operaciones_pendientes(self):
        cantidad = 0
        for telefono_origen, transacciones in self.operaciones_pendientes[self.usuario.dni]['transacciones'].items():
            for transaccion in transacciones:
                dinero_cifrado = base64.b64decode(transaccion['dinero'])
                fecha = transaccion['fecha']
                nonce = base64.b64decode(transaccion['nonce'])

                clave = self.codificacion.generar_clave_chacha(self.master_key, self.salt2)
                dinero = self.codificacion.descifrar(self.usuario.dni, dinero_cifrado, clave, nonce)

                clave2 = self.codificacion.generar_clave_chacha(self.usuario.password, self.salt2)
                nonce2, dinero_cifrado2 = self.codificacion.cifrar(self.usuario.dni, dinero, clave2, None)

                if telefono_origen not in self.bizums[self.telefono]['transacciones']:
                    self.bizums[self.telefono]['transacciones'][telefono_origen] = []
                self.bizums[self.telefono]['transacciones'][telefono_origen].append({'dinero': dinero_cifrado2,
                                                                        'fecha': fecha,
                                                                        'nonce': nonce2})
                cantidad += float(dinero)
            del self.operaciones_pendientes[self.usuario.dni]
            self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, self.operaciones_pendientes)
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, self.bizums)
            self.usuarios.transacciones(cantidad, '+')
        return "Operaciones guardadas con éxito"

    def eliminar_cuenta(self):
        # Elimina la cuenta del usuario
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
            del usuarios[self.usuario.dni]
            del nonces[self.usuario.dni]
            if self.telefono in self.bizums:
                del self.bizums[self.telefono]
                self.usuario.guardar_json(self.ARCHIVO_BIZUM, self.bizums)
            self.usuario.guardar_json(self.usuario.ARCHIVO_USUARIOS, usuarios)
            self.usuario.guardar_json(self.usuario.ARCHIVO_NONCES, nonces)
            return "Cuenta borrada"
        except Exception as e:
            raise RuntimeError(f"Error al eliminar la cuenta: {e}")







