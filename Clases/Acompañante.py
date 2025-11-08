from Clases.Ingrediente import Ingrediente

class Acompañante(Ingrediente):
    
    def __init__(self, nombre: str, tipo: str, tamaño: int, unidad: str):
        
        super().__init__(nombre, tipo)
        super().info_ingrediente

        self.nombre = nombre
        self.tipo = tipo
        self.tamaño = tamaño
        self.unidad = unidad

    def info_acompañante(self):
        """Función para obtener la información del acompañante
        """        
        info = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
            "Tamaño": self.tamaño,
            "Unidad": self.unidad
        }
        return info