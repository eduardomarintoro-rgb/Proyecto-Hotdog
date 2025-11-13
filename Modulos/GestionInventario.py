from rich import print
from Clases.Pan import Pan
from Clases.Acompañante import Acompañante
from Clases.Salchicha import Salchicha
from Clases.Salsa import Salsa
from Clases.Toppings import Toppings
from Clases.Hotdog import HotDog

# 1 ---> disponible
# 0 ---> no disponible

#Funciones para listar todos los ingredientes de una categoría

def ver_inventario_completo(panes, salchichas, acompañantes, salsas, toppings):
        """Funcion para seleccionar la categoría de ingredientes a gestionar 
        """        
        print ("\n[italic blue]---------- Inventario Completo ---------- ")

        print ("\n[italic blue]--- Panes ---")
        for ingrediente in panes:
            print("\n", ingrediente.info_pan())

        print ("\n[italic blue]--- Salchichas ---")
        for ingrediente in salchichas:
            print("\n", ingrediente.info_salchicha())

        print ("\n[italic blue]--- Acompañantes ---")
        for ingrediente in acompañantes:
            print("\n", ingrediente.info_acompañante())
        
        print ("\n[italic blue]--- Salsas ---")
        for ingrediente in salsas:
            print("\n", ingrediente.info_salsa())

        print ("\n[italic blue]--- Toppings ---")
        for ingrediente in toppings:
            print("\n", ingrediente.info_topping())


#Funciones para listar todos los productos en esa categoria de un tipo
def listar_ingredientes_categoria_tipo(panes, salchichas, acompañantes, salsas, toppings):
        """Funcion para seleccionar la categoría de ingredientes a gestionar por tipo
        """        
        while True:
            option = input ("""
    ¿Qué categoría desea visualizar?
                                
    1. Pan 
    2. Salchicha
    3. Acompañante
    4. Salsa
    5. Topping
    6. Regresar
                                                        
    ---> """)
            
            if option =="1":
                listar_ingredientes_tipo(panes)
                break
            elif option =="2":
                listar_ingredientes_tipo(salchichas)
                break
            elif option =="3":
                listar_ingredientes_tipo(acompañantes)
                break
            elif option =="4":
                listar_ingredientes_tipo(salsas)
                break
            elif option =="5":
                listar_ingredientes_tipo(toppings)
                break
            elif option =="6":
                print ("\n[italic blue]Regresando al menú de gestión de ingredientes...\n")
                break
            else:
                print ("[italic red]Opción inválida")

# Función para listar todos los ingredientes de un tipo dentro de una categoría
def listar_ingredientes_tipo(ingredientes_categoria):
    """Función para listar todos los ingredientes de un tipo dentro de una categoría
    """
    tipo_buscar = input("Ingrese el tipo de ingrediente que desea listar: ")
    encontrados = [ingrediente for ingrediente in ingredientes_categoria if ingrediente.tipo.lower() == tipo_buscar.lower()]


    if encontrados:
        print(f"\n[italic green]Ingredientes del tipo '{tipo_buscar}':\n")
        print(f"\n[italic green]Cantidad de ingredientes encontrados' {len(encontrados)}':\n")

        for ingrediente in encontrados:
            if isinstance(ingrediente, Pan):
                print(ingrediente.info_pan())
            elif isinstance(ingrediente, Salchicha):
                print(ingrediente.info_salchicha())
            elif isinstance(ingrediente, Salsa):
                print(ingrediente.info_salsa())
            elif isinstance(ingrediente, Toppings):
                print(ingrediente.info_topping())
            elif isinstance(ingrediente, Acompañante):
                print(ingrediente.info_acompañante())
            else:
                print("\nIngrediente no identificado\n")
    else:
        print(f"\n[italic red]No se encontraron ingredientes del tipo '{tipo_buscar}'.\n")

# Función para buscar un ingrediente específico dentro de todas las categorías
def buscar_ingrediente(panes, salchichas, acompañantes, salsas, toppings):
    """Función para buscar un ingrediente específico dentro de todas las categorías.
    """
    nombre_buscar = input("Ingrese el nombre del ingrediente que desea buscar: ")
    ingredientes = panes + salchichas + acompañantes + salsas + toppings
    encontrados = []

    # Buscar en cada categoría
    for ingrediente in ingredientes:
        if ingrediente.nombre.lower() == nombre_buscar.lower():
            encontrados.append(ingrediente)
            break

    # Mostrar resultados
    if len(encontrados) > 0:
        print(f"\n[italic green]Ingredientes encontrados con el nombre '{nombre_buscar}':\n")
        for ingrediente in encontrados:
            if isinstance(ingrediente, Pan):
                print(ingrediente.info_pan())
            elif isinstance(ingrediente, Salchicha):
                print(ingrediente.info_salchicha())
            elif isinstance(ingrediente, Salsa):
                print(ingrediente.info_salsa())
            elif isinstance(ingrediente, Toppings):
                print(ingrediente.info_topping())
            elif isinstance(ingrediente, Acompañante):
                print(ingrediente.info_acompañante())
            else:
                print("\nIngrediente no identificado\n")
    else:
        print(f"\n[italic red]No se encontraron ingredientes con el nombre '{nombre_buscar}'.\n")

    return encontrados

# Actualizar existencia de un producto específico

# Menu de gestión de inventario
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
                ver_inventario_completo(self.pan, self.salchicha, self.acompañantes, self.salsa, self.toppings)
            elif opcion == "2":
                buscar_ingrediente(self.pan, self.salchicha, self.acompañantes, self.salsa, self.toppings)
            elif opcion == "3":
                listar_ingredientes_categoria_tipo(self.pan, self.salchicha, self.acompañantes, self.salsa, self.toppings)
            elif opcion == "4":
                pass

            elif opcion == "5":
                break

            else:
                print("\n[italic red]Opción inválida. Introduzca una opción válida por favor.\n")
                
