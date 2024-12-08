import base64

from cryptography.exceptions import InvalidKey

from codificacion import Codificacion
from usuario import Usuario
from log_config import get_logger
import excepciones
logger = get_logger(__name__)
class GestorDatos:
    def __init__(self, dni, password):
        self.usuario = Usuario(dni, password)
        self.codificacion = Codificacion()
        logger.info(f"Gestor de Datos inicializado para el usuario con DNI: {dni}")

    def datos_cifrar_descifrar(self, dato_nonces):
        """Cogemos el salt2 del diccionario de usuario y el nonce del dato que queremos descifrar, devolvemos la clave
        y el nonce, es decir, todos los datos necesarios para descrifrar un dato """
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
            salt2 = base64.b64decode(usuarios[self.usuario.dni]['salt2'])
            nonce = base64.b64decode(nonces[self.usuario.dni][dato_nonces])

            clave = self.codificacion.generar_clave_chacha(self.usuario.password, salt2)
            logger.info(f"Datos obtenidos")
            return clave, nonce
        except FileNotFoundError:
            raise excepciones.ArchivoNoEncontradoError("Error al cargar el JSON")
        except KeyError:
            raise excepciones.ClaveNoEncontradaError("Clave no encontrada en JSON")
        except ValueError:
            raise excepciones.ValorInvalidoError("Error en la generación de clave o decodificación")
        except Exception as e:
            logger.error(f"Error inesperado en la obtención de los datos para cifrar o descifrar: {e}")
            raise

    def revisar_datos(self, dato_usuarios, dato_nonces):
        """Método para revisar datos de un usuario"""
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            # Después de acceder al JSON desciframos la clave y el nonce
            clave, nonce = self.datos_cifrar_descifrar(dato_nonces)
            # Decodificamos el dato de Base64 a Bytes
            dato_cifrado = base64.b64decode(usuarios[self.usuario.dni][dato_usuarios])
            # Desciframos los datos
            dato_descifrado = self.codificacion.descifrar(self.usuario.dni, dato_cifrado, clave, nonce)
            logger.info(f"Datos revisados para {dato_usuarios}")
            return dato_descifrado
        except FileNotFoundError:
            raise excepciones.ArchivoNoEncontradoError("Error al cargar JSON")
        except KeyError:
            raise excepciones.ClaveNoEncontradaError("Clave no encontrada en JSON")
        except ValueError:
            raise excepciones.ValorInvalidoError("Error en la decodificación del dato cifrado")
        except InvalidKey:
            raise excepciones.ClaveInvalidaError("Clave inválida para el descifrado")
        except Exception as e:
            logger.error(f"Error inesperado en revisar_datos: {e}")
            raise


    def actualizar_datos(self, dato_actualizado, dato_usuarios, dato_nonces):
        """Actualizamos el json con un nuevo dato"""
        try:
            usuarios = self.usuario.carga_json(self.usuario.ARCHIVO_USUARIOS)
            nonces = self.usuario.carga_json(self.usuario.ARCHIVO_NONCES)
            # Con este método obtenemos la clave y el nonce necesarios para cifrar el dato
            clave = self.datos_cifrar_descifrar(dato_nonces)[0]
            # Ciframos el dato y después lo guardamos en el JSON
            nonce, dato = self.codificacion.cifrar(self.usuario.dni, str(dato_actualizado), clave)
            usuarios[self.usuario.dni][dato_usuarios] = dato
            nonces[self.usuario.dni][dato_nonces] = nonce
            self.usuario.guardar_json(self.usuario.ARCHIVO_USUARIOS, usuarios)
            self.usuario.guardar_json(self.usuario.ARCHIVO_NONCES, nonces)
            logger.info(f"Datos actualizados para {dato_usuarios}")
        except FileNotFoundError:
            raise excepciones.ArchivoNoEncontradoError("Error al cargar JSON")
        except KeyError:
            raise excepciones.ClaveNoEncontradaError("Clave no encontrada en JSON")
        except ValueError:
            raise excepciones.ValorInvalidoError("Error en la generación de clave o decodificación")
        except Exception as e:
            logger.error(f"Error inesperado en actualizar_datos: {e}")
            raise

    def transacciones(self, cifra, operacion):
        global c
        try:
            # Obtenemos el saldo descifrado
            saldo = self.revisar_datos('saldo_disponible', 'saldo_disponible')
            c = saldo # Esto es para una excepción
            # Si la operación es de ingresar (+) se suma la cifra al saldo y sino se resta
            if operacion == '+':
                saldo = float(saldo) + cifra

            else:
                if float(saldo) < cifra:
                    raise excepciones.OperacionInvalidaError("No dispone de suficiente saldo")
                else:
                    saldo = float(saldo) - cifra
            # Actualizamos el saldo del JSON
            self.actualizar_datos(saldo, 'saldo_disponible', 'saldo_disponible')
            logger.info(f"Transacción realizada: {operacion} {cifra} Saldo actual: {saldo}")
            return True, saldo
        except excepciones.OperacionInvalidaError as e:
            logger.warning(str(e))
            return False, c
        except ValueError:
            raise excepciones.ValorInvalidoError("Error al calcular el saldo")
        except Exception as e:
            logger.error(f"Error inesperado en transacciones: {e}")
            raise


    def nombre_titular(self):
        # Devuelve el nombre completo del titular
        try:
            nombre = self.revisar_datos('nombre', 'nombre')
            apellido1 = self.revisar_datos('apellido1', 'apellido1')
            apellido2 = self.revisar_datos('apellido2', 'apellido2')

            return f"{nombre} {apellido1} {apellido2}"
        except FileNotFoundError:
            raise excepciones.ArchivoNoEncontradoError("Error al cargar JSON")
        except KeyError:
            raise excepciones.ClaveNoEncontradaError("Clave no encontrada en JSON")
        except Exception as e:
            logger.error(f"Error al obtener el nombre del titular: {e}")
            raise