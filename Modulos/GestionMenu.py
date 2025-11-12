from rich import print


def gestion_menu(self):
    """Menu para gestionar los hot dogs que se venden.
    """        

    while True:
        print ("\n[italic blue]---------- Acciones ---------- ")
        opcion = input ("""                                                                 
    1. Ver hotdogs disponibles
    2. Ver inventario de un hotdog específico
    3. Agregar un hotdog
    4. Eliminar un hotdog
    5. Regresar
                        
---> """)

        if opcion == "1":
            pass
            break
        elif opcion == "2":
            pass
            break
        elif opcion == "3":
            pass
            break
            
        elif opcion == "4":
            break
        elif opcion == "5":
            break
            
        else:
            print("\n[italic red]Opción inválida. Introduzca una opción válida por favor.\n")