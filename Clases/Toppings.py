
class Toppings():
    
    def __init__(self, nombre: str, tipo: str, presentacion: str):
        # Use a stable, serializable identifier (integer) instead of the builtin function 'id'
        # which would otherwise store a function object in __dict__ and break JSON serialization.
        self.id = id(self)
        self.nombre = nombre
        self.tipo = tipo
        self.presentacion = presentacion
        self.stock = 0

    def info_topping(self):
        """Función para obtener la información del topping.
        """
        info = {
            "Nombre": self.nombre,
            "Tipo": self.tipo,
            "Presentacion": self.presentacion
        }
        return info