import usuario, os, json, modificacion_saldo
from datetime import datetime

#DESCARGAR DATOS USUARIOS
ARCHIVO_BIZUM = 'bizums.json'
def carga_bizum():
    if os.path.exists(ARCHIVO_BIZUM):
        with open(ARCHIVO_BIZUM, 'r') as file:
            return json.load(file)
    return {}

#GUARDAR USUARIOS EN EL JSON
def guardar_bizum(bizums):
    with open(ARCHIVO_BIZUM, 'w') as file:
        json.dump(bizums, file, indent=4)


def registrarse_bizum(dni, telefono, password):
    bizums = carga_bizum()
    if not usuario.login_usuario(dni, password):
        return "Error: Contraseña incorrecta"
    usuarios = usuario.carga_usuarios()

    if usuarios[dni]['telefono'] != telefono:
        return "Error: Teléfono incorrecto"

    if telefono in bizums:
        return "Error: Ya está registrado/a en bizum"

    bizums[telefono] = {
        'dni' : dni,
        'transacciones': {}
    }
    guardar_bizum(bizums)
    return "Registrado en bizum exitosamente"


def realizar_bizum(dni, password, cantidad, telefono_destino):
    bizums = carga_bizum()
    usuarios = usuario.carga_usuarios()
    telefono_origen = usuarios[dni]['telefono']
    if telefono_origen == telefono_destino:
        return "Error: No se puede enviar un bizum a usted mismo"
    if telefono_origen not in bizums:
        return "Error: no está registrado en bizum."

    if telefono_destino not in bizums:
        return "Error: el usuario al que quiere envíar el bizum no está registrado en bizum."

    dni_origen = bizums[telefono_origen]['dni']
    dni_destinatario = bizums[telefono_destino]['dni']

    if modificacion_saldo.transacciones(dni_origen, password, cantidad, '-')[0]:
        if modificacion_saldo.transacciones(dni_destinatario, password, cantidad, '+')[0]:
            bizums[telefono_origen]['transacciones'][telefono_destino] = {'dinero': f"-{cantidad}",
                                                                          'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            bizums[telefono_destino]['transacciones'][telefono_origen] = {'dinero': f"+{cantidad}",
                                                                     'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            guardar_bizum(bizums)
            return "Su bizum se ha realizado con éxito."
    return "No se ha podido hacer el bizum"

def revisar_transacciones(dni):
    usuarios = usuario.carga_usuarios()
    bizums = carga_bizum()
    telefono = usuarios[dni]['telefono']
    return bizums[telefono]['transacciones']





