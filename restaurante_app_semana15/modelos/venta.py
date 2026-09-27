from datetime import datetime

class Venta:
    def __init__(self, id_venta: str, id_usuario: str, id_producto: str, fecha: str = None, total: float = 0.0):
        self.id_venta = id_venta
        self.id_usuario = id_usuario
        self.id_producto = id_producto
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total = float(total)

    def to_dict(self) -> dict:
        return {
            "id_venta": self.id_venta,
            "id_usuario": self.id_usuario,
            "id_producto": self.id_producto,
            "fecha": self.fecha,
            "total": self.total
        }

    @staticmethod
    def from_dict(data: dict):
        return Venta(
            id_venta=data.get("id_venta", ""),
            id_usuario=data.get("id_usuario", ""),
            id_producto=data.get("id_producto", ""),
            fecha=data.get("fecha"),
            total=data.get("total", 0.0)
        )