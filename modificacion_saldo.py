import acceso_datos
def transacciones(dni, cifra, operacion):
    saldo = acceso_datos.revisar_datos(dni, 'saldo_disponible', 'nonce_saldo')
    if operacion == '+':
        saldo = float(saldo) + cifra
        print(f"Su dinero se ha ingresado correctamente \n Nuevo saldo disponible: {saldo} euros\n")
    else:
        if float(saldo) < cifra:
            print("No dispone de suficiente saldo")
        else:
            saldo = float(saldo) - cifra
            print(f"Su dinero se ha retirado correctamente \n Nuevo saldo disponible: {saldo} euros\n")
    acceso_datos.actualizar_datos(dni, saldo, 'saldo_disponible', 'nonce_saldo')
