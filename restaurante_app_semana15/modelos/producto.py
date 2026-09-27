class Producto:
    def __init__(self, nombre, precio, stock=0, id_producto=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)

    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock
        }