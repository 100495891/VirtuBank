import usuario as u

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
            else:
                print("Usuario o contraseña incorrectos.")

        elif eleccion == 3:
            print("Saliendo...")
            salir = True

        else:
            print("La opción seleccionada no es válida, prueba de nuevo")