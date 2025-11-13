from Clases.Pan import Pan
from Clases.Salchicha import Salchicha
from Clases.Acompañante import Acompañante

class HotDog():
    
    def __init__(self, nombre, pan: Pan, salchicha: Salchicha, salsas: list, toppings: list, acompañante: Acompañante):
        
        self.nombre = nombre
        self.pan = pan
        self.salchicha = salchicha
        self.salsas = salsas
        self.toppings = toppings
        self.acompañante = acompañante
        self.stock = 1

    def dar_stock(self):
        """Función para obtener el stock de la salsa
        """
        if self.stock <= 0:
            return "No disponible"
        else:
            return "Disponible"
    
    def info_salsas(self):
        """Función para obtener la información de las salsas
        """
        # Return a list of salsa info dicts
        return [i.info_salsa() for i in self.salsas]
    
    def info_toppings(self):
        """Función para obtener la información de los toppings
        """
        # Return a list of topping info dicts
        return [i.info_topping() for i in self.toppings]
    
    def info_hotdog(self):
        """Función para obtener la información del hotdog
        """        
        info = {
            "Nombre": self.nombre,
            "Pan": self.pan.info_pan() if hasattr(self.pan, 'info_pan') else str(self.pan),
            "Salchicha": self.salchicha.info_salchicha() if hasattr(self.salchicha, 'info_salchicha') else str(self.salchicha),
            "Salsas": self.info_salsas(),
            "Toppings": self.info_toppings(),
            "Acompañante": self.acompañante.info_acompañante() if hasattr(self.acompañante, 'info_acompañante') else str(self.acompañante),
            "Stock": self.dar_stock()
        }
        return info
    
    