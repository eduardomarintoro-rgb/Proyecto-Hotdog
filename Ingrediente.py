class Ingrediente():
    
    def __init__(self, nombre: str, tipo: str):
        
        self.nombre = nombre
        self.tipo = tipo

    def info_ingrediente(self):
        """Función para obtener la información del ingrediente
        """        
        info_ing = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
        }
        return info_ing
    