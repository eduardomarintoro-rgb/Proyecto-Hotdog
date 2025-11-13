from Clases.Pan import Pan
from Clases.Salchicha import Salchicha
from Clases.Acompañante import Acompañante

class HotDog():
    
    def __init__(self, pan: Pan, salchicha: Salchicha, salsas: list, toppings: list, acompañante: Acompañante):
        
        self.pan = pan
        self.salchicha = salchicha
        self.salsas = salsas
        self.toppings = toppings
        self.acompañante = acompañante

    def info_salsas(self):
        """Función para obtener la información de las salsas
        """
        for i in self.salsas:
            txt = '\n'
            txt = txt + i.info_salsa() + '\n'
    
        return txt
    
    def info_toppings(self):
        """Función para obtener la información de los toppings
        """
        for i in self.toppings:
            txt = '\n'
            txt = txt + i.info_topping() + '\n'
    
        return txt
    
    def info_hotdog(self):
        """Función para obtener la información del hotdog
        """        
        info = {
            "Pan": self.pan,
            "Salchicha": self.salchicha,
            "Salsas": self.info_salsas,
            "Toppings": self.info_toppings,
            "Acompañante": self.acompañante
        }
        return info
    
    