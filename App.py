
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
URL_MENU_JSON = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/menu.json"
 
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
        """Función para crear objetos a partir de la API y almacenarlos en las listas de la instancia App.
        """ 

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
                    self._salsas_map[nombre.lower()] = salsa_obj # Clave en minúsculas

                elif categoria == "toppings":
                    topping_obj = Toppings(nombre, item_data.get("tipo"), item_data.get("presentación"))
                    self.toppings.append(topping_obj)
                    self._toppings_map[nombre.lower()] = topping_obj # Clave en minúsculas
                    
                elif categoria == "Pan":
                    pan_obj = Pan(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.pan.append(pan_obj)
                    self._panes_map[nombre.lower()] = pan_obj # Clave en minúsculas

                elif categoria == "Salchicha":
                    salchicha_obj = Salchicha(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.salchicha.append(salchicha_obj)
                    self._salchichas_map[nombre.lower()] = salchicha_obj # Clave en minúsculas

                elif categoria == "Acompañante":
                    acompañante_obj = Acompañante(nombre, item_data.get("tipo"), item_data.get("tamaño"), item_data.get("unidad"))
                    self.acompañantes.append(acompañante_obj)
                    self._acompañantes_map[nombre.lower()] = acompañante_obj # Clave en minúsculas

        print(f"Ingredientes cargados: Panes={len(self.pan)}, Salchichas={len(self.salchicha)}, Salsas={len(self.salsa)}, Toppings={len(self.toppings)}, Acompañantes={len(self.acompañantes)}")


        print("\n--- 2. PROCESANDO MENÚ (HotDogs) CON NUEVA ESTRUCTURA ---")
        # 2. Obtener los datos del menú (AHORA se espera una LISTA)
        data_menu_list = self.obtener_json_desde_url(URL_MENU_JSON) 
        if not isinstance(data_menu_list, list):
            print("Error: El JSON del menú no es una lista con la estructura esperada.")
            return

        # Iterar directamente sobre la lista de HotDogs
        for item_menu in data_menu_list: 
            try:
                hotdog_nombre = item_menu.get("nombre", "HotDog Desconocido")
                
                # --- 1. Obtener nombres y buscar las instancias de Ingredientes Principales (por nombre en el mapa) ---
                
                # Pan y Salchicha
                nombre_pan = item_menu.get("Pan", "").lower()
                pan_obj = self._panes_map.get(nombre_pan)

                nombre_salchicha = item_menu.get("Salchicha", "").lower()
                salchicha_obj = self._salchichas_map.get(nombre_salchicha)
                
                if not pan_obj or not salchicha_obj:
                    print(f"ADVERTENCIA: Falta un componente principal (Pan: '{nombre_pan}' o Salchicha: '{nombre_salchicha}') para el HotDog '{hotdog_nombre}'. Omitiendo ítem.")
                    continue

                # Acompañante (puede ser null, "No vendemos alcohol", o un nombre)
                nombre_acompañante = item_menu.get("Acompañante") 
                acompañante_obj = None

                if nombre_acompañante is not None:
                    nombre_acompañante_lower = str(nombre_acompañante).lower()
                    
                    # Ignorar si es el texto especial
                    if nombre_acompañante_lower != 'no vendemos alcohol': 
                        # Buscar en el mapa de acompañantes
                        acompañante_obj = self._acompañantes_map.get(nombre_acompañante_lower)
                        # Opcional: Agregar advertencia si el acompañante no se encuentra
                        if acompañante_obj is None and nombre_acompañante_lower:
                            print(f"ADVERTENCIA: El acompañante '{nombre_acompañante_lower}' no se encontró en el mapa de ingredientes.")


                # --- 2. Obtener las listas de Salsas y Toppings ---
                
                # Concatenar las listas de salsas, manejando posibles inconsistencias de capitalización de clave (Salsas/salsas)
                nombres_salsas = [s.lower() for s in item_menu.get("salsas", []) + item_menu.get("Salsas", [])]
                salsas_hotdog = [self._salsas_map[nombre] for nombre in nombres_salsas if nombre in self._salsas_map]

                # Concatenar las listas de toppings
                nombres_toppings = [t.lower() for t in item_menu.get("toppings", []) + item_menu.get("Toppings", [])]
                toppings_hotdog = [self._toppings_map[nombre] for nombre in nombres_toppings if nombre in self._toppings_map]


                # --- 3. Crear el objeto HotDog ---
                hotdog_obj = HotDog(
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
        
        # 1. Función auxiliar para serializar listas de objetos
        # Se requiere 'self' aquí para poder acceder a '_serializar_hotdog' en el caso de que la lista contenga un HotDog.
        def _serializar_lista(lista_objetos):
            # Asume que todos los objetos tienen un método 'info_XYZ()' que devuelve un diccionario simple.
            serializados = []
            for obj in lista_objetos:
                try:
                    # Intenta encontrar el método info_...() adecuado para serializar el objeto
                    if hasattr(obj, 'info_hotdog'):
                        # Si es un HotDog, llamamos a su serializador recursivo.
                        # NOTA DE CORRECCIÓN: Llamamos a _serializar_hotdog con 'self' explícito.
                        serializados.append(_serializar_hotdog(self, obj)) 
                    elif hasattr(obj, 'info_acompañante'):
                         serializados.append(obj.info_acompañante())
                    elif hasattr(obj, 'info_pan'):
                         serializados.append(obj.info_pan())
                    elif hasattr(obj, 'info_salchicha'):
                         serializados.append(obj.info_salchicha())
                    # Para Toppings y Salsa, su método es info_salchicha() o similar, 
                    # pero no heredan de Ingrediente en el código proporcionado.
                    # Asumiremos que tienen un método que devuelve su diccionario de info.
                    # Ya que los Toppings y Salsas no tienen un método específico en los archivos,
                    # necesitamos adaptarlos.
                    elif hasattr(obj, 'info_salchicha'): # Esto aplica a Salsa y Toppings en los archivos de referencia
                        serializados.append(obj.info_salchicha())
                    else:
                        # Fallback: Intentar serializar el diccionario de atributos
                        print(f"ADVERTENCIA: Objeto de tipo {type(obj).__name__} sin método de info conocido. Usando __dict__.")
                        serializados.append(obj.__dict__)
                        
                except Exception as e:
                    print(f"Error al serializar objeto {type(obj).__name__}: {e}")
                    serializados.append({"Error": f"No se pudo serializar el objeto {type(obj).__name__}"})
            return serializados

<<<<<<< Updated upstream
        # 2. Función auxiliar para serializar un HotDog (maneja sus sub-objetos)
        # Se ha agregado 'self' como primer argumento posicional.
        def _serializar_hotdog(self, hotdog_obj):
            """Serializa un objeto HotDog para el JSON, usando la información de los ingredientes."""
            return {
                # Se necesita adaptar la llamada aquí para usar el self explícito
                "Pan": hotdog_obj.pan.info_pan(), # Asumo info_pan() existe y devuelve dict
                "Salchicha": hotdog_obj.salchicha.info_salchicha(), # Asumo info_salchicha() existe y devuelve dict
                # Serializar listas de objetos de ingredientes
                # NOTA DE CORRECCIÓN: Llamamos a _serializar_lista con la lista de objetos, no necesita 'self'
                "Salsas": _serializar_lista(hotdog_obj.salsas),
                "Toppings": _serializar_lista(hotdog_obj.toppings),
                "Acompañante": hotdog_obj.acompañante.info_acompañante() if hotdog_obj.acompañante else None # Manejar None
            }

        # 3. Construir el diccionario de datos a guardar
=======
        # Función de codificación para manejar objetos personalizados. 
        # Esta función será pasada a json.dump(default=...)
        def _hotdog_json_encoder(obj):
            """Encoder personalizado para json.dump.
            Devuelve objetos ya serializables (dicts, listas, strings, números) para json.
            """
            # 1. Serialización del HotDog: serializar sus componentes recursivamente
            if isinstance(obj, HotDog):
                return {
                    "Pan": _hotdog_json_encoder(obj.pan),
                    "Salchicha": _hotdog_json_encoder(obj.salchicha),
                    "Salsas": [_hotdog_json_encoder(s) for s in (obj.salsas or [])],
                    "Toppings": [_hotdog_json_encoder(t) for t in (obj.toppings or [])],
                    "Acompañante": _hotdog_json_encoder(obj.acompañante)
                }

            # 2. Ingredientes con métodos 'info_...' (soportar variantes 'info_topping'/'info_toppings')
            if hasattr(obj, 'info_pan'):
                return obj.info_pan()
            if hasattr(obj, 'info_salchicha'):
                return obj.info_salchicha()
            if hasattr(obj, 'info_acompañante'):
                return obj.info_acompañante()
            if hasattr(obj, 'info_salsa'):
                return obj.info_salsa()
            # soportar nombre de método en singular o plural
            if hasattr(obj, 'info_topping'):
                return obj.info_topping()
            if hasattr(obj, 'info_toppings'):
                return obj.info_toppings()

            # 3. Si es un tipo built-in serializable ya, devolver tal cual
            if isinstance(obj, (str, int, float, bool)) or obj is None:
                return obj

            # 4. Si es una lista/tuple, serializar sus elementos
            if isinstance(obj, (list, tuple)):
                return [_hotdog_json_encoder(x) for x in obj]

            # 5. Si tiene __dict__, devolver copia de atributos (fallback)
            if hasattr(obj, '__dict__'):
                print(f"ADVERTENCIA: Objeto de tipo {type(obj).__name__} sin método de info conocido. Usando __dict__.")
                return {k: _hotdog_json_encoder(v) for k, v in obj.__dict__.items()}

            # 6. No serializable
            raise TypeError(f"Objeto de tipo {type(obj).__name__} no es serializable a JSON.")

        # 1. Construir el diccionario de datos a guardar (usando las listas de objetos directamente)
>>>>>>> Stashed changes
        datos_a_guardar = {
            "ingredientes": {
                "panes": _serializar_lista(self.pan),
                "salchichas": _serializar_lista(self.salchicha),
                "salsas": _serializar_lista(self.salsa),
                "toppings": _serializar_lista(self.toppings),
                "acompañantes": _serializar_lista(self.acompañantes),
            },
            # CORRECCIÓN CLAVE: Aquí es donde se usa la función anidada. 
            # Como es una función anidada, debemos pasarle el 'self' de la instancia App 
            # y el objeto 'hd'.
            "hotdogs_menu": [_serializar_hotdog(self, hd) for hd in self.hotdogs]
        }
        
        # 4. Guardar en archivo JSON
        try:
<<<<<<< Updated upstream
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                # Usar indent=4 para formato legible y ensure_ascii=False para guardar caracteres UTF-8 (como ñ, tildes)
                json.dump(datos_a_guardar, f, indent=4, ensure_ascii=False)
=======
            # Serializar a string en memoria primero para forzar cualquier fallo de codificación
            json_text = json.dumps(datos_a_guardar, indent=4, ensure_ascii=False, default=_hotdog_json_encoder)

            # Escribir de forma atómica: escribir en archivo temporal y luego reemplazar
            import tempfile
            dir_name = os.path.dirname(os.path.abspath(nombre_archivo)) or '.'
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dir_name, delete=False) as tmp:
                tmp.write(json_text)
                temp_name = tmp.name

            # Reemplazar el archivo de destino
            os.replace(temp_name, nombre_archivo)
>>>>>>> Stashed changes
            print(f"ÉXITO: Los datos se han guardado en '{nombre_archivo}' correctamente.")

        except IOError as e:
            print(f"ERROR: No se pudo escribir en el archivo '{nombre_archivo}': {e}")
        except Exception as e:
<<<<<<< Updated upstream
            print(f"ERROR: Ocurrió un error inesperado durante el guardado: {e}")
        print ("[italic green]=== Guardado finalizado ===")
=======
            # Si ocurre un error de serialización, json.dumps lanzará antes de tocar el archivo
            print(f"ERROR: Ocurrió un error inesperado durante el guardado: {e}")
        print("[italic green] === GUARDADO FINALIZADO ===")
>>>>>>> Stashed changes

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
            nombre = datos.get("Nombre")
            tipo = datos.get("Tipo")
            
            # Nota: usamos la categoría para determinar la clase y el constructor adecuado.
            # Los nombres de claves varían ligeramente entre clases (e.g., 'Base' en Salsa vs 'Tamaño' en Pan).
            
            if categoria == "panes":
                tamaño = datos.get("Tamaño")
                unidad = datos.get("Unidad")
                return Pan(nombre, tipo, tamaño, unidad)
            
            elif categoria == "salchichas":
                tamaño = datos.get("Tamaño")
                unidad = datos.get("Unidad")
                return Salchicha(nombre, tipo, tamaño, unidad)

            elif categoria == "acompañantes":
                tamaño = datos.get("Tamaño")
                unidad = datos.get("Unidad")
                return Acompañante(nombre, tipo, tamaño, unidad)
            
            elif categoria == "salsas":
                base = datos.get("Base")
                color = datos.get("Color")
                # Nota: La clase Salsa no hereda de Ingrediente en los archivos proporcionados, 
                # y usa 'base' y 'color'. Su constructor es Salsa(nombre, base, color).
                return Salsa(nombre, base, color)
            
            elif categoria == "toppings":
                presentacion = datos.get("Presentacion")
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
                    # 1. Recuperar objetos de ingredientes principales usando los mapas
                    pan_nombre = hotdog_data["Pan"]["Nombre"].lower()
                    pan_obj = self._panes_map.get(pan_nombre)

                    salchicha_nombre = hotdog_data["Salchicha"]["Nombre"].lower()
                    salchicha_obj = self._salchichas_map.get(salchicha_nombre)
                    
                    # 2. Recuperar acompañante (puede ser None)
                    acompañante_obj = None
                    acompañante_data = hotdog_data["Acompañante"]
                    if acompañante_data:
                        acompañante_nombre = acompañante_data["Nombre"].lower()
                        acompañante_obj = self._acompañantes_map.get(acompañante_nombre)

                    if not pan_obj or not salchicha_obj:
                        print(f"ADVERTENCIA: Componente principal no encontrado para un HotDog. Omitiendo.")
                        continue
                        
                    # 3. Recuperar listas de Salsas y Toppings
                    
                    # Para Salsas y Toppings, se puede recrear el objeto directamente o usar el mapa.
                    # Usaremos el mapa para asegurar que usamos las instancias ya cargadas.
                    salsas_hotdog = []
                    for salsa_data in hotdog_data.get("Salsas", []):
                        salsa_nombre = salsa_data["Nombre"].lower()
                        salsa_obj = self._salsas_map.get(salsa_nombre)
                        if salsa_obj:
                            salsas_hotdog.append(salsa_obj)

                    toppings_hotdog = []
                    for topping_data in hotdog_data.get("Toppings", []):
                        topping_nombre = topping_data["Nombre"].lower()
                        topping_obj = self._toppings_map.get(topping_nombre)
                        if topping_obj:
                            toppings_hotdog.append(topping_obj)

                    # 4. Crear el objeto HotDog
                    hotdog_obj = HotDog(pan_obj, salchicha_obj, salsas_hotdog, toppings_hotdog, acompañante_obj)
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


