class Usuario:
    def __init__(self, id_usuario: str, nombre: str, username: str, clave: str, rol: str = "Cliente"):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.username = username
        self.clave = clave
        self.rol = rol

    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "username": self.username,
            "clave": self.clave,
            "rol": self.rol
        }

    @staticmethod
    def from_dict(data: dict):
        return Usuario(
            id_usuario=data.get("id_usuario", ""),
            nombre=data.get("nombre", ""),
            username=data.get("username", ""),
            clave=data.get("clave", ""),
            rol=data.get("rol", "Cliente")
        )