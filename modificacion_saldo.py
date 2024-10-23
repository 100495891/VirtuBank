import acceso_datos
def transacciones(dni, password, cifra, operacion):
    saldo = acceso_datos.revisar_datos(dni, password,'saldo_disponible', 'nonce_saldo')
    if operacion == '+':
        saldo = float(saldo) + cifra

    else:
        if float(saldo) < cifra:
            print("No dispone de suficiente saldo")
            return False
        else:
            saldo = float(saldo) - cifra

    acceso_datos.actualizar_datos(dni, password, saldo, 'saldo_disponible', 'nonce_saldo')
    return True, saldo