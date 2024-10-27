from usuario import Usuario
from acceso_datos import GestorDatos
from bizum import Bizum
if __name__ == "__main__":
    salir = False
    # Aquí el usuario decide si quiere registrarse, iniciar sesión o salir
    while not salir:

        print("Menu:\n")
        print("1. Registrarse\n")
        print("2. Iniciar Sesión\n")
        print("3. Salir\n")

        try:
            eleccion = int(input("Selecciona una opción del 1 al 3: "))
        except ValueError as e:
            print(f"Entrada no válida. Por favor, ingresa un número del 1 al 3: {e}")
            continue

        # Registro de un usuario nuevo
        if eleccion == 1:
            dni = input("\nIntroduzca su DNI: ")
            password = input("\nCrea una contraseña: ")
            nombre = input("\nIntroduzca su nombre: ")
            apellido1 = input("\nIntroduzca su primer apellido: ")
            apellido2 = input("\nIntroduzca su segundo apellido: ")
            telefono = input("\nIntroduzca su telefono: ")
            correo_electronico = input("\nIntroduzca su correo electrónico: ")
            try:
                usuario = Usuario(dni, password)
                print(usuario.registro_usuario(nombre, apellido1, apellido2, telefono, correo_electronico))
            except ValueError as e:
                print(f"Error en el registro de usuario: {e}")

        # Inicio de sesión de un usuario ya registrado
        elif eleccion == 2:
            dni = input("\nIntroduzca su DNI: ")
            password = input("\nIntroduzca su contraseña: ")
            usuario = Usuario(dni, password)
            gestor_datos = GestorDatos(usuario.dni, usuario.password)
            bizum = Bizum(usuario.dni, usuario.password)
            if usuario.login_usuario():
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
                    print("7. Revisar operaciones pendientes\n")
                    print("8. Revisar datos cuenta\n")
                    print("9. Revisar datos tarjeta\n")
                    print("10. Eliminar cuenta\n")
                    print("11. Cerrar Sesión\n")

                    try:
                        accion = int(input("Seleccione una opción (1-11): "))
                    except ValueError as e:
                        print(f"Entrada no válida. Por favor, ingresa un número del 1 al 11: {e}")
                        continue

                    if accion == 1:
                        # Revisar el saldo
                        try:
                            saldo = gestor_datos.revisar_datos('saldo_disponible', 'saldo_disponible')
                            print(f"\nSu saldo es {saldo} euros")
                        except Exception as e:
                            print(f"Error al revisar saldo: {e}")
                        input("Presione Enter para continuar...")
                    elif accion == 2:
                        # Ingresar dinero en la cuenta
                        try:
                            cifra = float(input("\nIntroduzca la cantidad que desea ingresar: "))
                            sol = gestor_datos.transacciones(cifra, '+')
                            print(f"Su dinero se ha ingresado correctamente \n Nuevo saldo disponible: {sol[1]} euros\n")
                        except ValueError:
                            print("Cantidad no válida. Por favor, ingrese un número.")
                        input("Presione Enter para continuar...")
                    elif accion == 3:
                        # Retirar dinero de la cuenta
                        try:
                            cifra = float(input("\nIntroduzca la cantidad que desea retirar: "))
                            sol = gestor_datos.transacciones(cifra, '-')
                            print(f"Su dinero se ha retirado correctamente \n Nuevo saldo disponible: {sol[1]} euros\n")
                        except ValueError:
                            print("Cantidad no válida. Por favor, ingrese un número.")
                        input("Presione Enter para continuar...")
                    elif accion == 4:
                        # Registrarse en bizum
                        try:
                            print(bizum.registrarse_bizum())
                        except ValueError as ve:
                            print(f"Error al registrarse en Bizum: {ve}")
                        except Exception as e:
                            print(f"Ha ocurrido un error inesperado: {e}")

                        input("Presione Enter para continuar...")
                    elif accion == 5:
                        # Realizar un bizum
                        telefono_destino = input("\nIntroduzca el teléfono de la persona a la que desea enviar el bizum: ")
                        try:
                            cantidad = float(input("\nIntroduzca la cantidad que desea enviar: "))
                            print(bizum.realizar_bizum(cantidad, telefono_destino))
                            saldo = gestor_datos.revisar_datos('saldo_disponible', 'saldo_disponible')
                            
                        except ValueError:
                            print("Cantidad no válida. Por favor, ingrese un número.")
                        input("Presione Enter para continuar...")
                    elif accion == 6:
                        # Revisar las transacciones
                        try:
                            bizum.revisar_transacciones()
                        except Exception as e:
                            print(f"Error al revisar transacciones: {e}")
                        input("Presione Enter para continuar...")
                    elif accion == 7:
                        try:
                            operaciones_pendientes = bizum.operaciones_pendientes
                            if dni in operaciones_pendientes:
                                print("\nAquí tiene sus operaciones pendientes")
                                bizum.revisar_operaciones_pendientes()
                                op = input("\n¿Quiere aceptarlas? (y/n): ").lower()
                                if op == "y":
                                    telefono = input("\nConfirme su telefono: ")
                                    print(bizum.cargar_operaciones_pendientes())
                                    saldo = gestor_datos.revisar_datos('saldo_disponible', 'saldo_disponible')
                                    print(f"\nSu saldo es {saldo} euros")
                                elif op == "n":
                                    print("\nEntendido, vuelve cuando quieras aceptarlas")
                                else:
                                    print("\nOpción no válida")
                            else:
                                print("No tienes operaciones pendientes\n")
                        except KeyError as ke:
                            print(f"Error de clave: {ke}")
                        except ValueError as ve:
                            print(f"Error de valor: {ve}")
                        except Exception as e:
                            print(f"Ha ocurrido un error inesperado: {e}")
                        input("Presione Enter para continuar...")
                    elif accion == 8:
                        # Revisar datos de la cuenta
                        try:
                            num_cuenta = gestor_datos.revisar_datos('numero_cuenta', 'numero_cuenta')
                            print(f"Su número de cuenta es {num_cuenta}")
                        except Exception as e:
                            print(f"Error al revisar número de cuenta: {e}")
                        input("Presione Enter para continuar...")
                    elif accion == 9:
                        # Revisar datos de la tarjeta
                        try:
                            num_tarjeta = gestor_datos.revisar_datos('tarjeta', 'tarjeta')
                            fecha_expiracion = gestor_datos.revisar_datos('fecha_expiracion_tarjeta', 'fecha_expiracion_tarjeta')
                            cvv = gestor_datos.revisar_datos('cvv', 'cvv')
                            print(f"Titular de la tarjeta: {gestor_datos.nombre_titular()}")
                            print(f"Número tarjeta:{num_tarjeta}")
                            print(f"Fecha Expiración:{fecha_expiracion}")
                            print(f"CVV:{cvv}")
                        except Exception as e:
                            print(f"Error al revisar datos de tarjeta: {e}")
                        input("Presione Enter para continuar...")
                    elif accion == 10:
                        # Borrar la cuenta
                        confirmacion_password = input("\nIntroduzca su contraseña: ")
                        try:
                            if confirmacion_password == password:
                                print(bizum.eliminar_cuenta())
                                cerrar_sesion = True
                            else:
                                print("Error: la contraseña no es correcta")
                        except Exception as e:
                            print(f"Ha ocurrido un error al intentar eliminar la cuenta: {e}")
                        input("Presione Enter para continuar...")

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
