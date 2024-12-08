import base64
from datetime import datetime
from codificacion import Codificacion
from usuario import Usuario
from acceso_datos import GestorDatos
import firmas_certificados
from log_config import get_logger
import excepciones

logger = get_logger(__name__)

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
        self.dni = dni
        self.password = password

    def registrarse_bizum(self):
        try:
            bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
            if not self.usuario.login_usuario():
                raise excepciones.UsuarioNoRegistradoError("Error: Contraseña incorrecta")
            if self.telefono in bizums:
                raise excepciones.UsuarioNoRegistradoError("Error: Ya está registrado/a en bizum")

            # Vamos a aplicar aquí la firma y los certificados
            clave_privada = firmas_certificados.generar_guardar_clave_privada(self.dni, self.password)

            # Firmamos el número de teléfono de la persona que se quiere registrar en bizum
            firmas_certificados.generar_guardar_firma(self.telefono, clave_privada, self.dni)
            logger.info("Su número de teléfono se ha firmado correctamente")

            # Hacemos la petición del certificado (csr)
            firmas_certificados.generar_csr(clave_privada, self.dni)

            # Ahora firmamos el certificado manualmente con openSSL
            input("Presione Enter cuando esté el certificado firmado...")

            # Ahora verificamos la firma, el certificado del usuario y el certificado raiz
            firmas_certificados.verificaciones(self.dni, self.telefono)
            logger.info("Todo ha sido correctamente certificado")

            bizums[self.telefono] = {
                'dni' : self.usuario.dni,
                'transacciones': {}
            }
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
            return "Registrado en bizum exitosamente"
        except excepciones.UsuarioNoRegistradoError as e:
            logger.error(e)
            return str(e)
        except excepciones.ErrorCertificadoError as e:
            logger.error(e)
            return str(e)
        except Exception as e:
            logger.error(f"Error inesperado en registrarse_bizum: {e}")
            raise


    def realizar_bizum(self, cantidad, telefono_destino):
        try:
            bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            salt2 = usuarios[self.usuario.dni]['salt2'].encode()
            # Comprobamos que el número no sea el mismo que el del usuario que envía el bizum
            if self.telefono == telefono_destino:
                raise excepciones.OperacionInvalidaError("Error: No se puede enviar un bizum a usted mismo")
            # Comprobamos que el que envía el dinero esté registrado en bizum
            if self.telefono not in bizums:
                raise excepciones.UsuarioNoRegistradoError("Error: no está registrado en bizum.")
            # Comprobamos que el que recibe el dinero esté registrado en bizum
            if telefono_destino not in bizums:
                raise excepciones.UsuarioNoRegistradoError("Error: el usuario al que quiere envíar el bizum no está registrado en bizum.")
            dni_destinatario = bizums[telefono_destino]['dni']

            # Comprobamos que se realice correctamente la transacción
            if self.gestor_datos.transacciones(cantidad, '-')[0]:
                # Ciframos la contraseña con el algoritmo PBKDF2HMAC que usaremos como clave para cifrar los datos
                clave = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
                # Ciframos el nonce y la cantidad que hemos enviado
                nonce_cantidad_origen, cantidad_cifrada_origen = self.codificacion.cifrar(self.usuario.dni, str(-cantidad), clave)
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
                logger.info("Su bizum se ha realizado con éxito.")
            return "No se ha podido hacer el bizum"
        except excepciones.UsuarioNoRegistradoError as e:
            logger.error(e)
            return str(e)
        except excepciones.OperacionInvalidaError as e:
            logger.error(e)
            return str(e)
        except Exception as e:
            logger.error(f"Error inesperado al realizar el Bizum: {e}")
            raise


    def revisar_transacciones_operaciones(self, diccionario, identificador, pw_clave, dni):
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            salt2 = usuarios[self.usuario.dni]['salt2'].encode()
            # Recorre el diccionario transacciones en el que hay una lista por cada persona con la que tiene alguna transación
            # En esa lista hay un diccionario para cada transacción
            for persona, lista in diccionario[identificador]['transacciones'].items():
                print(f"\nBizums con: {persona}")
                # Recorre todas las transacciones que ha tenido con cada usuario
                for j, transaccion in enumerate(lista, start = 1):
                    clave = self.codificacion.generar_clave_chacha(pw_clave, salt2)
                    dinero_cifrado = base64.b64decode(transaccion['dinero'])
                    nonce = base64.b64decode(transaccion['nonce'])
                    fecha = transaccion['fecha']
                    dinero = self.codificacion.descifrar(dni, dinero_cifrado, clave, nonce)
                    print(f"\nTransacción {j}:\nDinero: {dinero}\nFecha: {fecha}")
            logger.info(f"Revisadas las transacciones para {identificador}")
        except Exception as e:
            logger.error(f"Error inesperado en revisar transacciones u operaciones pendientes: {e}")
            raise

    def revisar_transacciones(self):
        try:
            bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
            self.revisar_transacciones_operaciones(bizums, self.telefono, self.usuario.password, self.usuario.dni)
            logger.info("Transacciones revisadas con éxito")
        except Exception as e:
            logger.error(f"Error inesperado en revisar transacciones: {e}")
            raise

    def revisar_operaciones_pendientes(self):
        try:
            operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
            self.revisar_transacciones_operaciones(operaciones_pendientes, self.usuario.dni, self.master_key, self.usuario.dni)
            logger.info("Operaciones pendientes revisadas con éxito")
        except Exception as e:
            logger.error(f"Error inesperado en revisar_operaciones_pendientes: {e}")
            raise
    def crear_operacion_pendiente(self, dni, cantidad, telefono_destino):
        try:
            operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            salt2_destino = usuarios[dni]['salt2'].encode()
            # Generamos la clave haciendo uso de la master key
            clave = self.codificacion.generar_clave_chacha(self.master_key, salt2_destino)
            # Ciframos la cantidad recibida y el nonce de ese dato cifrado
            nonce_cantidad, cantidad_cifrada = self.codificacion.cifrar(dni, str(+cantidad), clave)
            # Si no existe el dni de destino en operaciones pendientes crea un diccionario y lo introduce
            if dni not in operaciones_pendientes:
                operaciones_pendientes[dni] = {
                    'telefono' : telefono_destino,
                    'transacciones': {}
                }
            # Si el telefono origen no tiene otras operaciones pendientes para ese destinatario crea una lista vacía
            if self.telefono not in operaciones_pendientes[dni]['transacciones']:
                operaciones_pendientes[dni]['transacciones'][self.telefono] = []

            # Introducimos la transacción en operaciones pendientes
            operaciones_pendientes[dni]['transacciones'][self.telefono].append({'dinero': cantidad_cifrada,
                                                                               'fecha': datetime.now().strftime(
                                                                                   "%d/%m/%Y %H:%M:%S"),
                                                                               'nonce': nonce_cantidad})
            self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, operaciones_pendientes)
            logger.info(f"Operación pendiente creada para {telefono_destino} por {cantidad}")
        except Exception as e:
            logger.error(f"Error inesperado en crear_operacion_pendiente: {e}")
            raise

    def cargar_operaciones_pendientes(self):
        try:
            operaciones_pendientes = self.usuario.carga_json(self.ARCHIVO_OPERACIONES_PENDIENTES)
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            salt2 = usuarios[self.usuario.dni]['salt2'].encode()
            bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
            cantidad = 0
            # Recorremos cada uno de los usuarios que nos ha enviado dinero
            for telefono_origen, transacciones in operaciones_pendientes[self.usuario.dni]['transacciones'].items():
                # Ejecutamos el bucle para cada Bizum recibido de cada usuario
                for transaccion in transacciones:
                    dinero_cifrado = base64.b64decode(transaccion['dinero'])
                    fecha = transaccion['fecha']
                    nonce = base64.b64decode(transaccion['nonce'])
                    # Generamos la clave con el salt de la persona que nos ha enviado el dinero y posteriormente desciframos el dinero enviado
                    clave = self.codificacion.generar_clave_chacha(self.master_key, salt2)
                    dinero = self.codificacion.descifrar(self.usuario.dni, dinero_cifrado, clave, nonce)
                    # Generamos la clave con nuestro salt y ciframos el dato
                    clave2 = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
                    nonce2, dinero_cifrado2 = self.codificacion.cifrar(self.usuario.dni, dinero, clave2)

                    # Si ese usuario no nos había enviado dinero antes guardamos una lista para futuras transacciones
                    if telefono_origen not in bizums[self.telefono]['transacciones']:
                        bizums[self.telefono]['transacciones'][telefono_origen] = []
                    # Guardamos la transacción realizada
                    bizums[self.telefono]['transacciones'][telefono_origen].append({'dinero': dinero_cifrado2,
                                                                            'fecha': fecha,
                                                                            'nonce': nonce2})
                    cantidad += float(dinero)
            # Borramos del diccionario de operaciones pendientes del usuario actual
            del operaciones_pendientes[self.usuario.dni]
            # Actualizamos los datos
            self.usuario.guardar_json(self.ARCHIVO_OPERACIONES_PENDIENTES, operaciones_pendientes)
            self.usuario.guardar_json(self.ARCHIVO_BIZUM, bizums)
            self.gestor_datos.transacciones(cantidad, '+')
            return "Operaciones guardadas con éxito"
        except Exception as e:
            logger.error(f"Error inesperado en cargar_operaciones_pendientes: {e}")
            raise

    def eliminar_cuenta(self):
        try:
            # Elimina la cuenta del usuario
            bizums = self.usuario.carga_json(self.ARCHIVO_BIZUM)
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
            raise excepciones.ErrorEliminarCuentaError(f"Error al eliminar la cuenta: {e}")
