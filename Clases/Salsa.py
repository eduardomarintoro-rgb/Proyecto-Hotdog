
class Salsa():
    
    def __init__(self, nombre: str, base: str, color: str):
        # Use a stable, serializable identifier (integer) instead of the builtin function 'id'
        # which would otherwise store a function object in __dict__ and break JSON serialization.
        self.id = id(self)
        self.nombre = nombre
        self.base = base
        self.tipo = base
        self.color = color
        self.stock = 1

    def dar_stock(self):
        """Función para obtener el stock de la salsa
        """
        if self.stock <= 0:
            return "No disponible"
        else:
            return "Disponible"
        
    def info_salsa(self):
        """Función para obtener la información de la salsa
        """        
        info = {
            "Nombre": self.nombre,
            "Base": self.base,
            "Color": self.color,
            "Stock": self.dar_stock()
        }
        return info