from Clases.Ingrediente import Ingrediente

class Pan(Ingrediente):
    
    def __init__(self, nombre: str, tipo: str, tamaño: int, unidad: str):
        
        super().__init__(nombre, tipo)
        super().dar_stock()

        self.nombre = nombre
        self.tipo = tipo
        self.tamaño = tamaño
        self.unidad = unidad

    def info_pan(self):
        """Función para obtener la información del pan
        """        
        info_pan = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
            "Tamaño": self.tamaño,
            "Unidad": self.unidad,
            "Stock": self.dar_stock()
        }
        return info_pan