from rich import print

def gestion_inventario(self):
        """Menu de las acciones del inventario.
        """        

        while True:
            print ("\n[italic blue]---------- Acciones ---------- ")
            opcion = input ("""                            
    1. Visualizar todo el inventario 
    2. Buscar un ingrediente específico 
    3. Tipos de ingredientes por categoría
    4. Actualizar la existencia de un producto específico 
    5. Regresar
                                    
    ---> """)
            if opcion == "1":
                pass

            elif opcion == "2":
                pass

            elif opcion == "3":
                pass

            elif opcion == "4":
                pass

            elif opcion == "5":
                break

            else:
                print("\n[italic red]Opción inválida. Introduzca una opción válida por favor.\n")
                
