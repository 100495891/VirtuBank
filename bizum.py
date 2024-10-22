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
    if not usuario.login_usuario(dni, password):
        return "Error: contraseña incorrecta"
    usuarios = usuario.carga_usuarios()

    if usuarios[dni]['telefono'] != telefono:
        return "Error: teléfono incorrecto"

    bizums = carga_bizum()
    bizums[telefono] = {
        'dni' : dni,
        'transacciones': {}
    }
    guardar_bizum(bizums)
    return "Registrado en bizum exitosamente"

def realizar_bizum(telefono_origen, cantidad, telefono_destino):
    bizums = carga_bizum()
    if not bizums[telefono_origen]:
        return "Error: no está registrado en bizum."

    if not bizums[telefono_destino]:
        return "Error: el usuario al que quiere envíar el bizum no está registrado en bizum."

    dni_origen = bizums[telefono_origen]['dni']
    dni_destinatario = bizums[telefono_destino]['dni']
    if modificacion_saldo.transacciones(dni_origen, cantidad, '-'):
        if modificacion_saldo.transacciones(dni_destinatario, cantidad, '+'):
            bizums[telefono_origen]['transacciones'][dni_destinatario] = {'dinero': f"-{cantidad}",
                                                                          'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            bizums[telefono_destino]['transacciones'][dni_origen] = {'dinero': f"+{cantidad}",
                                                                     'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

            return "Su bizum se ha realizado con éxito."
    return "No se ha podido hacer el bizum"



