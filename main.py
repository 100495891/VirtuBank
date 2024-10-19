import usuario as u
import datos_cuenta_tarjeta as datos

if __name__ == "__main__":
    salir = False
    while salir == False:
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
                while cerrar_sesion == False:
                    print("¿Qué quiere hacer?\n")
                    print("1. Revisar saldo\n")
                    print("2. Registrarse en bizum\n")
                    print("3. Realizar bizum\n")
                    print("4. Revisar bizums\n")
                    print("5. Revisar datos cuenta\n")
                    print("6. Revisar datos tarjeta\n")
                    print("7. Cambiar contraseña\n")
                    print("8. Cerrar Sesión\n")
                    accion = int(input("Seleccione una opción (1-8): "))

                    if accion == 1:
                        cerrar_sesion = True
                    if accion == 2:
                        cerrar_sesion = True
                    if accion == 3:
                        cerrar_sesion = True
                    if accion == 4:
                        cerrar_sesion = True
                    if accion == 5:
                        num_cuenta = datos.revisar_datos(dni, 'numero_cuenta_cifrado', 'nonce_cuenta')
                        print(f"Su número de cuenta es {num_cuenta}")
                    if accion == 6:
                        num_tarjeta = datos.revisar_datos(dni, 'tarjeta_cifrada', 'nonce_tarjeta')
                        fecha_expiracion = datos.revisar_datos(dni, 'fecha_expiracion_cifrada', 'nonce_fecha_expiracion_tarjeta')
                        cvv = datos.revisar_datos(dni, 'cvv_cifrado', 'nonce_cvv')
                        print(f"Titular de la tarjeta: {u.nombre_titular(dni)}")
                        print(f"Número tarjeta:{num_tarjeta}")
                        print(f"Fecha Expiración:{fecha_expiracion}")
                        print(f"CVV:{cvv}")

                    if accion == 7:
                        cerrar_sesion = True
                    if accion == 8:
                        print("Cerrando Sesión ...")
                        cerrar_sesion = True

            else:
                print("Usuario o contraseña incorrectos.")

        elif eleccion == 3:
            print("Saliendo...")
            salir = True

        else:
            print("La opción seleccionada no es válida, prueba de nuevo")