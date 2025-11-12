from rich import print
from Clases.Pan import Pan
from Clases.Acompañante import Acompañante
from Clases.Salchicha import Salchicha
from Clases.Salsa import Salsa
from Clases.Toppings import Toppings
from Clases.Hotdog import HotDog

#Función para ver los hotdogs disponibles
def ver_hotdogs_disponibles(hotdogs):
    """Función para ver los hotdogs disponibles.
    """

    print("\n[italic blue]Hotdogs disponibles para venta:")
    for hotdog in hotdogs:
        print("\n", hotdog.info_hotdog())

#Funcion para verificar la disponibilidad de un hotdog especifico
def verificar_disponibilidad_hotdog(hotdogs):
    """Función para verificar la disponibilidad de hotdog especifico.
    """
    hotdog_nombre = input("\nIngrese el nombre del hotdog que desea verificar: ")

    print(f"\n[italic blue]Inventario del hotdog: {hotdog_nombre}")
    for hotdog in hotdogs:
        if hotdog_nombre == hotdog.nombre:
            if hotdog.stock > 0:
                print("\n", hotdog.info_hotdog())
                return
    
    print("\n[italic red]El hotdog no está disponible en el inventario.")

#Funcion para agregar un hotdog

def agregar_hotdog(hotdogs, panes, salchichas, acompañantes, salsas, toppings):
    """Función para agregar un hotdog al inventario.
    """

    print("\n[italic blue]Panes disponibles:")
    for i in len(panes):
        print(f"{i+1}. {panes[i].nombre}")

    nuevo_pan = panes[int(input("\nSeleccione el número del pan que desea agregar: "))-1]

    print("\n[italic blue]Salchichas disponibles:")
    for i in len(salchichas):
        print(f"{i+1}. {salchichas[i].nombre}") 
    nueva_salchicha = salchichas[int(input("\nSeleccione el número de la salchicha que desea agregar: "))-1]
    
    print("\n[italic blue]Salsas disponibles:")
    for i in len(salsas):
        print(f"{i+1}. {salsas[i].nombre}")
    nuevas_salsas = []
    while True:
        seleccion = input("\nSeleccione el número de la salsa que desea agregar (o '0' para terminar): ")
        if seleccion == "0":
            break
        nuevas_salsas.append(salsas[int(seleccion)-1])

    print("\n[italic blue]Toppings disponibles:")
    for i in len(toppings):
        print(f"{i+1}. {toppings[i].nombre}")
    nuevos_toppings = []
    while True:
        seleccion = input("\nSeleccione el número del topping que desea agregar (o '0' para terminar): ")
        if seleccion == "0":
            break
        nuevos_toppings.append(toppings[int(seleccion)-1])

    print("\n[italic blue]Acompañantes disponibles:")
    for i in len(acompañantes):
        print(f"{i+1}. {acompañantes[i].nombre}")
    nuevo_acompañante = acompañantes[int(input("\nSeleccione el número del acompañante que desea agregar: "))-1]
    
    nuevo_hotdog = armar_hotdog(nuevo_pan, nueva_salchicha, nuevas_salsas, nuevos_toppings, nuevo_acompañante)

    if nuevo_hotdog is None:
        return
    else:
        hotdogs.append(nuevo_hotdog)
        print("\n[italic green]Hotdog agregado exitosamente.")

def armar_hotdog(nuevo_pan, nueva_salchicha, nuevas_salsas, nuevos_toppings, nuevo_acompañante):
    """Función para armar un hotdog con los ingredientes seleccionados.
    """

    if (nuevo_pan.tamaño != nueva_salchicha.tamaño):
        select = ("\n[italic red] El tamaño del pan y la salchicha no coinciden. Aun asi quiere armar el hotdog? (s/n)")
    
    if select.lower() == "n":
        print("\n[italic red] Hotdog no armado debido a la discrepancia de tamaños.")
        return None
    else:
        nuevo_hotdog = HotDog(nuevo_pan, nueva_salchicha, nuevas_salsas, nuevos_toppings, nuevo_acompañante)
        return nuevo_hotdog

#Funcion para eliminar un hotdog
def eliminar_hotdog(hotdogs):   

    print("\n[italic blue]Hotdogs disponibles:")

    for i in len(hotdogs):
        print(f"{i+1}. {hotdogs[i].nombre}")

    hotdog_eliminar = hotdogs[int(input("\nSeleccione el número del hotdog que desea eliminar: "))-1]

    for i in hotdogs:
        if hotdog_eliminar == hotdogs[i]:
            del hotdogs[i]
            print("\n[italic green]Hotdog eliminado exitosamente.")
            break


#Funcion para gestionar el menu de hotdogs
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
            ver_hotdogs_disponibles(self.hotdogs)
            break
        elif opcion == "2":
            verificar_disponibilidad_hotdog(self.hotdogs)
            break
        elif opcion == "3":
            agregar_hotdog(self.hotdogs, self.pan, self.salchicha, self.acompañantes, self.salsa, self.toppings)
            break
        elif opcion == "4":
            eliminar_hotdog(self.hotdogs)
            break
        elif opcion == "5":
            break
            
        else:
            print("\n[italic red]Opción inválida. Introduzca una opción válida por favor.\n")