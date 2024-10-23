import usuario as u
import acceso_datos as datos
import modificacion_saldo
import bizum as b
if __name__ == "__main__":
    salir = False
    while not salir:
        print("Menu:\n")
        print("1. Registrarse\n")
        print("2. Iniciar Sesión\n")
        print("3. Salir\n")

        eleccion = int(input("Selecciona una opción del 1 al 3: "))

        if eleccion == 1:
            dni = input("\nIntroduzca su DNI: ")
            password = input("\nCrea una contraseña: ")
            nombre = input("\nIntroduzca su nombre: ")
            apellido1 = input("\nIntroduzca su primer apellido: ")
            apellido2 = input("\nIntroduzca su segundo apellido: ")
            telefono = input("\nIntroduzca su telefono: ")
            correo_electronico = input("\nIntroduzca su correo electrónico: ")
            try:
                u.registro_usuario(dni, password, nombre, apellido1, apellido2, telefono, correo_electronico)
            except ValueError as e:
                print(e)

        elif eleccion == 2:
            dni = input("\nIntroduzca su DNI: ")
            password = input("\nIntroduzca su contraseña: ")

            if u.login_usuario(dni, password):
                print("Sesión iniciada.")
                cerrar_sesion = False
                while not cerrar_sesion:
                    print("¿Qué quiere hacer?\n")
                    print("1. Revisar saldo\n")
                    print("2. Ingresar dinero\n")
                    print("3. Retirar dinero\n")
                    print("4. Registrarse en bizum\n")
                    print("5. Realizar bizum\n")
                    print("6. Revisar transacciones\n")
                    print("7. Revisar datos cuenta\n")
                    print("8. Revisar datos tarjeta\n")
                    print("9. Cambiar contraseña\n")
                    print("10. Eliminar cuenta\n")
                    print("11. Cerrar Sesión\n")
                    accion = int(input("Seleccione una opción (1-11): "))

                    if accion == 1:
                        saldo = datos.revisar_datos(dni, password, 'saldo_disponible', 'nonce_saldo')
                        print(f"\nSu saldo es {saldo} euros")
                        input("Presione Enter para continuar...")
                    elif accion == 2:
                        cifra = float(input("\nIntroduzca la cantidad que desea ingresar: "))
                        sol = modificacion_saldo.transacciones(dni, password, cifra, '+')
                        print(f"Su dinero se ha ingresado correctamente \n Nuevo saldo disponible: {sol[1]} euros\n")
                        input("Presione Enter para continuar...")
                    elif accion == 3:
                        cifra = float(input("\nIntroduzca la cantidad que desea retirar: "))
                        sol = modificacion_saldo.transacciones(dni, password, cifra, '-')
                        print(f"Su dinero se ha retirado correctamente \n Nuevo saldo disponible: {sol[1]} euros\n")
                        input("Presione Enter para continuar...")
                    elif accion == 4:
                        telefono = input("\nIntroduzca su teléfono: ")
                        password = input("\nIntroduzca su contraseña: ")
                        print(b.registrarse_bizum(dni, telefono, password))
                        input("Presione Enter para continuar...")
                    elif accion == 5:
                        telefono_destino = input("\nIntroduzca el teléfono de la persona a la que desea enviar el bizum: ")
                        cantidad = float(input("\nIntroduzca la cantidad que desea enviar: "))
                        print(b.realizar_bizum(dni, password, cantidad, telefono_destino))
                        input("Presione Enter para continuar...")
                    elif accion == 6:
                        print(b.revisar_transacciones(dni))
                        input("Presione Enter para continuar...")
                    elif accion == 7:
                        num_cuenta = datos.revisar_datos(dni, password, 'numero_cuenta_cifrado', 'nonce_cuenta')
                        print(f"Su número de cuenta es {num_cuenta}")
                        input("Presione Enter para continuar...")
                    elif accion == 8:
                        num_tarjeta = datos.revisar_datos(dni, password, 'tarjeta_cifrada', 'nonce_tarjeta')
                        fecha_expiracion = datos.revisar_datos(dni, password, 'fecha_expiracion_cifrada', 'nonce_fecha_expiracion_tarjeta')
                        cvv = datos.revisar_datos(dni, password,'cvv_cifrado', 'nonce_cvv')
                        print(f"Titular de la tarjeta: {u.nombre_titular(dni)}")
                        print(f"Número tarjeta:{num_tarjeta}")
                        print(f"Fecha Expiración:{fecha_expiracion}")
                        print(f"CVV:{cvv}")
                        input("Presione Enter para continuar...")

                    elif accion == 9:
                        input("Presione Enter para continuar...")
                        cerrar_sesion = True
                    elif accion == 10:
                        input("Presione Enter para continuar...")
                        cerrar_sesion = True
                    elif accion == 11:
                        print("Cerrando Sesión ...")
                        cerrar_sesion = True

                    else:
                        print("La opción seleccionada no es válida, prueba de nuevo")
                        input("Presione Enter para continuar...")
            else:
                print("Usuario o contraseña incorrectos.")

        elif eleccion == 3:
            print("Saliendo...")
            salir = True

        else:
            print("La opción seleccionada no es válida, prueba de nuevo")
            input("Presione Enter para continuar...")
