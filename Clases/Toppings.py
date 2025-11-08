
class Toppings():
    
    def __init__(self, nombre: str, tipo: str, presentacion: str):

        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.presentacion = presentacion

    def info_topping(self):
        """Función para obtener la información de la salsa
        """        
        info = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
            "Presentacion": self.presentacion
        }
        return info