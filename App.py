
from rich import print
import requests
import json
import os
import sys

from Clases.Acompañante import Acompañante
from Clases.Salsa import Salsa
from Clases.Hotdog import HotDog
from Clases.Pan import Pan
from Clases.Salchicha import Salchicha
from Clases.Toppings import Toppings
from Modulos.GestionMenu import gestion_menu
from Modulos.GestionInventario import gestion_inventario    
from Modulos.DiaVentas import simulacion_dia_de_ventas, estadisticas_dia_ventas
from Modulos.GestionIngredientes import gestion_ingredientes

URL_INGREDIENTES_JSON = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/ingredientes.json"
URL_MENU_JSON = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/refs/heads/main/menu.json"
 
class App():
    """Es la encargada de abrir y gestionar todas las operaciones que se tienen que llevar a cabo para gestionar la aplicación.
    """

    def __init__(self):
        """Constructor de la clase App. Contiene todas las listas donde se almacena la información.
        
        self.hotdogs = Lista de todos los hotdogs registrados.
        self.pan = Lista de tipos de pan registrados en la sede.
        self.salchicha = Lista de salchichas registradas.
        self.salsa = Lista de salsas registradas.
        self.toppings = Lista de toppings disponibles.
        self.acompañantes = Lista de acompañantes registrados en la plataforma.
        
        """        
        self.hotdogs = []   
        self.pan =  []
        self.salchicha = []
        self.salsa = []
        self.toppings = []
        self.acompañantes = []
        self.resultados_simulaciones = []   #Lista de dia de ventas

        #Para mappear nombres a objetos durante la carga de datos
        self._panes_map = {}
        self._salchichas_map = {}
        self._acompañantes_map = {}
        self._salsas_map = {}
        self._toppings_map = {}

#-------------------------------------------------------------------------------------------------------------------------------------------------            
                    
    def obtener_json_desde_url(self, url: str):
        """
        Obtiene y parsea el contenido JSON desde una URL.
        """
        try:
            response = requests.get(url)
            response.raise_for_status() # Lanza una excepción para códigos de estado erróneos (4xx o 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener o parsear el JSON de {url}: {e}")
            return None
    
# -------------------------------------------------------------------------------------------------------------------------------

    def abrir_API (self): 
        """Función para crear objetos a partir de la API y almacenarlos en las listas de la instancia App."""
        print("--- 1. PROCESANDO INGREDIENTES Y CREANDO MAPAS DE BÚSQUEDA ---")
        # 1. Obtener los datos de ingredientes (se espera una lista de categorías)
        data_ingredientes_list = self.obtener_json_desde_url(URL_INGREDIENTES_JSON)
        if not isinstance(data_ingredientes_list, list):
            print("Error: El JSON de ingredientes no es una lista o está vacío.")
            return

        for categoria_data in data_ingredientes_list:
            categoria = categoria_data.get("Categoria")
            opciones = categoria_data.get("Opciones", [])
            
            for item_data in opciones:
                nombre = item_data.get("nombre")

                if categoria == "Salsa":
                    salsa_obj = Salsa(nombre, item_data.get("base"), item_data.get("color"))
                    self.salsa.append(salsa_obj)
                    self._salsas_map[nombre.lower()] = salsa_obj 

                elif categoria == "toppings":
                    topping_obj = Toppings(nombre, item_data.get("tipo"), item_data.get("presentación"))
                    self.toppings.append(topping_obj)
                    self._toppings_map[nombre.lower()] = topping_obj 
                    
                elif categoria == "Pan":
                    pan_obj = Pan(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.pan.append(pan_obj)
                    self._panes_map[nombre.lower()] = pan_obj 

                elif categoria == "Salchicha":
                    salchicha_obj = Salchicha(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.salchicha.append(salchicha_obj)
                    self._salchichas_map[nombre.lower()] = salchicha_obj 

                elif categoria == "Acompañante":
                    acompañante_obj = Acompañante(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.acompañantes.append(acompañante_obj)
                    self._acompañantes_map[nombre.lower()] = acompañante_obj 

        print(f"Ingredientes cargados: Panes={len(self.pan)}, Salchichas={len(self.salchicha)}, Salsas={len(self.salsa)}, Toppings={len(self.toppings)}, Acompañantes={len(self.acompañantes)}")


        print("\n--- 2. PROCESANDO MENÚ (HotDogs) CON NUEVA ESTRUCTURA ---")
        # 2. Obtener los datos del menú (AHORA se espera una LISTA)
        data_menu_list = self.obtener_json_desde_url(URL_MENU_JSON) 
        if not isinstance(data_menu_list, list):
            print("Error: El JSON del menú no es una lista con la estructura esperada.")
            return

        for item_menu in data_menu_list: 
            try:
                hotdog_nombre = item_menu.get("nombre", "HotDog Desconocido")
                
                # --- 1. Obtener nombres y buscar las instancias de Ingredientes Principales (por nombre en el mapa) ---
                nombre_pan = item_menu.get("Pan", "").lower()
                pan_obj = self._panes_map.get(nombre_pan)

                nombre_salchicha = item_menu.get("Salchicha", "").lower()
                salchicha_obj = self._salchichas_map.get(nombre_salchicha)
                
                if not pan_obj or not salchicha_obj:
                    print(f"ADVERTENCIA: Falta un componente principal (Pan: '{nombre_pan}' o Salchicha: '{nombre_salchicha}') para el HotDog '{hotdog_nombre}'. Omitiendo ítem.")
                    continue

                nombre_acompañante = item_menu.get("Acompañante") 
                acompañante_obj = None

                if nombre_acompañante is not None:
                    nombre_acompañante_lower = str(nombre_acompañante).lower()
                    
                    if nombre_acompañante_lower != 'no vendemos alcohol': 
                        acompañante_obj = self._acompañantes_map.get(nombre_acompañante_lower)
                        if acompañante_obj is None and nombre_acompañante_lower:
                            print(f"ADVERTENCIA: El acompañante '{nombre_acompañante_lower}' no se encontró en el mapa de ingredientes.")

                # --- 2. Obtener las listas de Salsas y Toppings ---
                
                nombres_salsas = [s.lower() for s in item_menu.get("salsas", []) + item_menu.get("Salsas", [])]
                salsas_hotdog = [self._salsas_map[nombre] for nombre in nombres_salsas if nombre in self._salsas_map]

                nombres_toppings = [t.lower() for t in item_menu.get("toppings", []) + item_menu.get("Toppings", [])]
                toppings_hotdog = [self._toppings_map[nombre] for nombre in nombres_toppings if nombre in self._toppings_map]

                # --- 3. Crear el objeto HotDog ---
                hotdog_obj = HotDog(
                    hotdog_nombre,
                    pan_obj, 
                    salchicha_obj, 
                    salsas_hotdog, 
                    toppings_hotdog, 
                    acompañante_obj # Puede ser None
                )
                self.hotdogs.append(hotdog_obj)

            except Exception as e:
                print(f"ADVERTENCIA: Ocurrió un error inesperado al procesar el HotDog '{hotdog_nombre}': {e}. Omitiendo ítem.")

        print(f"Proceso completado. Se crearon {len(self.hotdogs)} objetos HotDog y se almacenaron en self.hotdogs.")
        
        # Limpieza de mapas temporales después de su uso
        self._panes_map = {}
        self._salchichas_map = {}
        self._acompañantes_map = {}
        self._salsas_map = {}
        self._toppings_map = {}

    def guardar_datos_json(self, nombre_archivo: str = "datos_hotdogs.json"):
        """
        Serializa toda la información disponible (ingredientes y hotdogs)
        y la guarda en un archivo JSON.
        """
        print(f"\n--- INICIANDO GUARDADO DE DATOS EN {nombre_archivo} ---")
        
        # Serializar ingredientes usando sus métodos info_* cuando existan.
        def _serializar_ingredientes(lista, metodo_singular=None):
            serializados = []
            for obj in lista:
                try:
                    if hasattr(obj, 'info_pan'):
                        serializados.append(obj.info_pan())
                    elif hasattr(obj, 'info_salchicha'):
                        serializados.append(obj.info_salchicha())
                    elif hasattr(obj, 'info_acompañante'):
                        serializados.append(obj.info_acompañante())
                    elif hasattr(obj, 'info_salsa'):
                        serializados.append(obj.info_salsa())
                    elif hasattr(obj, 'info_topping'):
                        serializados.append(obj.info_topping())
                    elif hasattr(obj, 'info_toppings'):
                        serializados.extend(obj.info_toppings())
                    else:
                        # Fallback: usar atributos públicos
                        serializados.append({k: v for k, v in getattr(obj, '__dict__', {}).items()})
                except Exception as e:
                    print(f"ADVERTENCIA: fallo al serializar {type(obj).__name__}: {e}")
                    serializados.append({"Error": f"No se pudo serializar {type(obj).__name__}"})
            return serializados

        # Construir la estructura de salida que `cargar_datos_json` espera.
        ingredientes_serializados = {
            "panes": _serializar_ingredientes(self.pan),
            "salchichas": _serializar_ingredientes(self.salchicha),
            "salsas": _serializar_ingredientes(self.salsa),
            "toppings": _serializar_ingredientes(self.toppings),
            "acompañantes": _serializar_ingredientes(self.acompañantes),
        }

        hotdogs_serializados = []
        for hd in self.hotdogs:
            try:
                hd_info = hd.info_hotdog() if hasattr(hd, 'info_hotdog') else {
                    "Pan": getattr(hd, 'pan', None),
                    "Salchicha": getattr(hd, 'salchicha', None),
                    "Salsas": getattr(hd, 'salsas', []),
                    "Toppings": getattr(hd, 'toppings', []),
                    "Acompañante": getattr(hd, 'acompañante', None),
                }

                # Asegurar que 'Acompañante' sea None (JSON null) si no existe
                if isinstance(hd_info.get('Acompañante'), str) and hd_info.get('Acompañante').lower() == 'none':
                    hd_info['Acompañante'] = None

                hotdogs_serializados.append(hd_info)
            except Exception as e:
                print(f"ADVERTENCIA: no se pudo serializar hotdog: {e}")

        datos_a_guardar = {
            "ingredientes": ingredientes_serializados,
            "hotdogs_menu": hotdogs_serializados
        }
        
        # 4. Guardar en archivo JSON
        try:
            # Serializar a string en memoria primero para forzar cualquier fallo de codificación
            # Serializar a texto; todos los objetos ya se convirtieron a dict/list/primitive
            json_text = json.dumps(datos_a_guardar, indent=4, ensure_ascii=False)

            # Escribir de forma atómica: escribir en archivo temporal y luego reemplazar
            import tempfile
            dir_name = os.path.dirname(os.path.abspath(nombre_archivo)) or '.'
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dir_name, delete=False) as tmp:
                tmp.write(json_text)
                temp_name = tmp.name

            # Reemplazar el archivo de destino
            os.replace(temp_name, nombre_archivo)
            print(f"ÉXITO: Los datos se han guardado en '{nombre_archivo}' correctamente.")

        except IOError as e:
            print(f"ERROR: No se pudo escribir en el archivo '{nombre_archivo}': {e}")
        except Exception as e:
            # Si ocurre un error de serialización, json.dumps lanzará antes de tocar el archivo
            print(f"ERROR: Ocurrió un error inesperado durante el guardado: {e}")
            print("[italic green] === GUARDADO FINALIZADO ===")

#-------------------------------------------------------------------------------------------------------------------------------------------------
        
    def cargar_datos_json(self, nombre_archivo: str = "datos_hotdogs.json"):
        """
        Lee el archivo JSON guardado y reconstruye los objetos de HotDogs e ingredientes 
        almacenándolos en las listas de la instancia App.
        """
        print(f"\n--- INICIANDO CARGA DE DATOS DESDE {nombre_archivo} ---")
        
        # 1. Verificar si el archivo existe
        if not os.path.exists(nombre_archivo):
            print(f"ERROR: El archivo '{nombre_archivo}' no fue encontrado.")
            return

        # 2. Leer el archivo JSON
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Error al decodificar el JSON en '{nombre_archivo}': {e}")
            return
        except IOError as e:
            print(f"ERROR: No se pudo leer el archivo '{nombre_archivo}': {e}")
            return
        
        # 3. Inicializar listas (opcional: limpiar las listas existentes antes de cargar)
        self.hotdogs.clear()
        self.pan.clear()
        self.salchicha.clear()
        self.salsa.clear()
        self.toppings.clear()
        self.acompañantes.clear()
        
        # 4. Funciones auxiliares para construir objetos
        
        # Función auxiliar para crear objetos de ingredientes
        def _crear_objeto_ingrediente(categoria: str, datos: dict):
            # Soportar claves con diferentes capitalizaciones y nombres
            nombre = datos.get("Nombre") or datos.get("nombre") or datos.get("name")
            tipo = datos.get("Tipo") or datos.get("tipo")
            
            # Nota: usamos la categoría para determinar la clase y el constructor adecuado.
            # Los nombres de claves varían ligeramente entre clases (e.g., 'Base' en Salsa vs 'Tamaño' en Pan).
            
            if categoria == "panes":
                tamaño = datos.get("Tamaño") or datos.get("tamaño") or datos.get("tamano")
                unidad = datos.get("Unidad") or datos.get("unidad")
                return Pan(nombre, tipo, tamaño, unidad)
            
            elif categoria == "salchichas":
                tamaño = datos.get("Tamaño") or datos.get("tamaño")
                unidad = datos.get("Unidad") or datos.get("unidad")
                return Salchicha(nombre, tipo, tamaño, unidad)

            elif categoria == "acompañantes":
                tamaño = datos.get("Tamaño") or datos.get("tamaño")
                unidad = datos.get("Unidad") or datos.get("unidad")
                return Acompañante(nombre, tipo, tamaño, unidad)
            
            elif categoria == "salsas":
                # Soportar claves 'Base'/'base' y 'Color'/'color'
                base = datos.get("Base") or datos.get("base")
                color = datos.get("Color") or datos.get("color")
                # Nota: La clase Salsa no hereda de Ingrediente en los archivos proporcionados, 
                # y usa 'base' y 'color'. Su constructor es Salsa(nombre, base, color).
                return Salsa(nombre, base, color)
            
            elif categoria == "toppings":
                presentacion = datos.get("Presentacion") or datos.get("presentacion") or datos.get("presentación")
                # Nota: La clase Toppings no hereda de Ingrediente en los archivos proporcionados,
                # y usa 'tipo' y 'presentacion'. Su constructor es Toppings(nombre, tipo, presentacion).
                return Toppings(nombre, tipo, presentacion)
            
            return None # Si la categoría no coincide con ninguna clase conocida


        # 5. Cargar y almacenar Ingredientes
        if "ingredientes" in datos_cargados:
            ingredientes_data = datos_cargados["ingredientes"]
            
            # --- Cargar Ingredientes Principales y construir mapas ---
            
            for categoria, lista_datos in ingredientes_data.items():
                lista_destino = []
                mapa_destino = {}
                
                # Determinar dónde almacenar y mapear los objetos
                if categoria == "panes": 
                    lista_destino = self.pan
                    mapa_destino = self._panes_map
                elif categoria == "salchichas":
                    lista_destino = self.salchicha
                    mapa_destino = self._salchichas_map
                elif categoria == "acompañantes":
                    lista_destino = self.acompañantes
                    mapa_destino = self._acompañantes_map
                elif categoria == "salsas":
                    lista_destino = self.salsa
                    mapa_destino = self._salsas_map
                elif categoria == "toppings":
                    lista_destino = self.toppings
                    mapa_destino = self._toppings_map
                else:
                    print(f"ADVERTENCIA: Categoría de ingrediente desconocida: {categoria}. Omitiendo.")
                    continue

                for datos in lista_datos:
                    try:
                        obj = _crear_objeto_ingrediente(categoria, datos)
                        if obj:
                            lista_destino.append(obj)
                            mapa_destino[obj.nombre.lower()] = obj # Usar nombre.lower() para la búsqueda
                    except Exception as e:
                        print(f"ADVERTENCIA: No se pudo crear objeto de {categoria} con datos {datos}: {e}")

            print(f"Ingredientes cargados y mapeados. Total: {sum(len(l) for l in [self.pan, self.salchicha, self.salsa, self.toppings, self.acompañantes])}")


        # 6. Cargar HotDogs
        if "hotdogs_menu" in datos_cargados:
            hotdogs_menu_data = datos_cargados["hotdogs_menu"]
            hotdogs_cargados = 0
            
            for hotdog_data in hotdogs_menu_data:
                try:
                    # 0. Obtener el nombre del hotdog
                    hotdog_nombre = hotdog_data.get("Nombre") or hotdog_data.get("nombre") or "HotDog Desconocido"

                    # 1. Recuperar objetos de ingredientes principales usando los mapas
                    pan_field = hotdog_data["Pan"]
                    if isinstance(pan_field, dict):
                        pan_nombre = pan_field.get("Nombre", "").lower()
                    else:
                        pan_nombre = str(pan_field).lower()
                    pan_obj = self._panes_map.get(pan_nombre)

                    salchicha_field = hotdog_data["Salchicha"]
                    if isinstance(salchicha_field, dict):
                        salchicha_nombre = salchicha_field.get("Nombre", "").lower()
                    else:
                        salchicha_nombre = str(salchicha_field).lower()
                    salchicha_obj = self._salchichas_map.get(salchicha_nombre)

                    # 2. Recuperar acompañante (puede ser None)
                    acompañante_obj = None
                    acompañante_data = hotdog_data.get("Acompañante")
                    if isinstance(acompañante_data, dict):
                        acomp_nombre = (acompañante_data.get("Nombre") or acompañante_data.get("nombre"))
                        if acomp_nombre:
                            acompañante_obj = self._acompañantes_map.get(str(acomp_nombre).lower())
                    elif isinstance(acompañante_data, str):
                        if acompañante_data.lower() not in ("none", "null", ""):
                            acompañante_obj = self._acompañantes_map.get(acompañante_data.lower())

                    if not pan_obj or not salchicha_obj:
                        print(f"ADVERTENCIA: Componente principal no encontrado para un HotDog. Omitiendo.")
                        continue

                    # 3. Recuperar listas de Salsas y Toppings
                    salsas_hotdog = []
                    salsas_field = hotdog_data.get("Salsas", [])
                    if not salsas_field:
                        salsas_field = hotdog_data.get("salsas", [])
                    for salsa_data in salsas_field:
                        if isinstance(salsa_data, dict):
                            salsa_nombre = salsa_data.get("Nombre", "").lower()
                        else:
                            salsa_nombre = str(salsa_data).lower()
                        salsa_obj = self._salsas_map.get(salsa_nombre)
                        if salsa_obj:
                            salsas_hotdog.append(salsa_obj)

                    toppings_hotdog = []
                    toppings_field = hotdog_data.get("Toppings", [])
                    if not toppings_field:
                        toppings_field = hotdog_data.get("toppings", [])
                    for topping_data in toppings_field:
                        if isinstance(topping_data, dict):
                            topping_nombre = topping_data.get("Nombre", "").lower()
                        else:
                            topping_nombre = str(topping_data).lower()
                        topping_obj = self._toppings_map.get(topping_nombre)
                        if topping_obj:
                            toppings_hotdog.append(topping_obj)

                    # 4. Crear el objeto HotDog con nombre
                    hotdog_obj = HotDog(hotdog_nombre, pan_obj, salchicha_obj, salsas_hotdog, toppings_hotdog, acompañante_obj)
                    self.hotdogs.append(hotdog_obj)
                    hotdogs_cargados += 1

                except Exception as e:
                    print(f"ADVERTENCIA: Error al cargar un HotDog desde JSON: {e}. Omitiendo ítem.")

            print(f"ÉXITO: Se cargaron {hotdogs_cargados} objetos HotDog y se almacenaron en self.hotdogs.")
        
        # 7. Limpieza de mapas temporales después de su uso (siempre es bueno hacerlo)
        self._panes_map = {}
        self._salchichas_map = {}
        self._acompañantes_map = {}
        self._salsas_map = {}
        self._toppings_map = {}
        
        print(f"Carga de datos JSON completada desde '{nombre_archivo}'.")        

#-------------------------------------------------------------------------------------------------------------------------------------------------

    def ver_estadisticas (self):
        """Función para ver las estadisticas de las simulaciones. 
        """  
        
            
#-------------------------------------------------------------------------------------------------------------------------------------------------   

    def principal_menu(self):
        """Menu principal. Posee las acciones principales para gestionar el programa.
        """   

        while True:
            print ("\n[italic blue]---------- Acciones ---------- ")
            opcion = input("""              
0. Cargar API                          
1. Cargar data de la aplicación                          
2. Gestionar ingredientes                                                                                                                       
3. Gestionar inventario                                                                                                                               
4. Gestionar menú                                             
5. Simulación de un día de ventas                                             
6. Ver estadísticas                                            
7. Guardar y salir                                                                          

---> """)
            
            if opcion == "0":
                App.abrir_API(self)

            elif opcion == "1":
                App.cargar_datos_json(self)
                print ("\n[italic green] ...Cargando datos\n")
                
            elif opcion == "2":
                gestion_ingredientes(self)
                print ("\n[italic green] ...Accediendo a interfaz\n")
    
            elif opcion == "3":
                gestion_inventario(self)
                print ("\n[italic green] ...Accediendo a interfaz\n")
                
            elif opcion == "4":
                gestion_menu(self)
                print ("\n[italic green] ...Accediendo a interfaz\n")

            elif opcion == "5":
                simulacion_dia_de_ventas(self)
                print ("\n[italic green] ...Accediendo a interfaz\n")

            elif opcion == "6":
                estadisticas_dia_ventas(self)
                print ("\n[italic green] ...Accediendo a interfaz\n")

            elif opcion == "7":
                App.guardar_datos_json(self)
                print ("\n[italic green]Cerrando programa...")
                sys.exit()
 
            else:
                print ("\n[italic red]Opción inválida\n")
                os.system('cls')

#-------------------------------------------------------------------------------------------------------------------------------------------------
    
    def start_app(self):
        """Función para darle inicio al programa
        """            
        print ("\n[italic blue]Inicializando programa...")
        print ("""
[bold yellow]🌭🌭   Bienvenido a Hotdog   🌭🌭""")
        App.principal_menu(self)


