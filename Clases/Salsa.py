
class Salsa():
    
    def __init__(self, nombre: str, base: str, color: str):

        self.id = id
        self.nombre = nombre
        self.base = base
        self.color = color

    def info_salsa(self):
        """Función para obtener la información de la salsa
        """        
        info = {
            "Nombre": self.nombre,
            "Base": self.base,
            "Color": self.color
        }
        return info