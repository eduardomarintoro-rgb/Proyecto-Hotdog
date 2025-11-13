class Ingrediente():
    
    def __init__(self, nombre: str, tipo: str):
        
        self.nombre = nombre
        self.tipo = tipo
        self.stock = 1

    def dar_stock(self):
        """Función para obtener el stock de la salsa
        """
        if self.stock < 0:
            return "No disponible"
        else:
            return "Disponible"
        
    def info_ingrediente(self):
        """Función para obtener la información del ingrediente
        """        
        info_ing = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
        }
        return info_ing
    