import usuarios as u

if __name__ == "__main__":
    salir = False
    while salir == False:
        print("Menu:\n")
        print("1. Registrarse\n")
        print("2. Iniciar Sesión\n")
        print("3. Salir\n")

        eleccion = int(input("Selecciona una opción del 1 al 3: "))

        if eleccion == 1:
            usuario = input("\nIntroduzca el nombre de usuario: ")
            contrasena = input("\nIntroduzca la contraseña: ")
            try:
                u.registro_usuario(usuario, contrasena)
            except ValueError as e:
                print(e)

        elif eleccion == 2:
            usuario = input("\nIntroduzca el nombre de usuario: ")
            contrasena = input("\nIntroduzca la contraseña: ")

            if u.login_usuario(usuario, contrasena):
                print("Sesión iniciada.")
            else:
                print("Usuario o contraseña incorrectos.")

        elif eleccion == 3:
            print("Saliendo...")
            salir = True

        else:
            print("La opción seleccionada no es válida, prueba de nuevo")