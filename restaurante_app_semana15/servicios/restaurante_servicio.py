import os
import json
import datetime
from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class RestauranteServicio:
    def __init__(self):
        # Localiza de forma absoluta la carpeta datos/ dentro de la raíz del proyecto
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        raiz_proyecto = os.path.dirname(dir_actual)
        
        self.datos_dir = os.path.join(raiz_proyecto, "datos")
        self.ruta_json = os.path.join(self.datos_dir, "restaurante.json")

        self.datos = self._cargar_datos()

    def _cargar_datos(self) -> dict:
        os.makedirs(self.datos_dir, exist_ok=True)

        if not os.path.exists(self.ruta_json):
            datos_iniciales = {
                "productos": [
                    {"id_producto": 1, "nombre": "Hamburguesa Clásica", "precio": 5.50, "stock": 20},
                    {"id_producto": 2, "nombre": "Papas Fritas", "precio": 2.50, "stock": 35}
                ],
                "usuarios": [
                    {"id_usuario": 1, "nombre": "Administrador", "username": "admin", "clave": "admin", "rol": "administrador"}
                ],
                "ventas": []
            }
            self._escribir_json(datos_iniciales)
            return datos_iniciales

        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {"productos": [], "usuarios": [], "ventas": []}
                data.setdefault("productos", [])
                data.setdefault("usuarios", [])
                data.setdefault("ventas", [])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"productos": [], "usuarios": [], "ventas": []}

    def _guardar_datos(self):
        self._escribir_json(self.datos)

    def _escribir_json(self, datos_dict):
        try:
            os.makedirs(self.datos_dir, exist_ok=True)
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                json.dump(datos_dict, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al escribir JSON: {e}")

    # -------------------------------------------------------------------------
    # USUARIOS & AUTENTICACIÓN
    # -------------------------------------------------------------------------
    def autenticar_usuario(self, username, clave):
        usr_clean = str(username).strip()
        pass_clean = str(clave).strip()

        for u in self.datos.get("usuarios", []):
            u_user = str(u.get('username', u.get('usuario', ''))).strip()
            u_pass = str(u.get('clave', u.get('password', ''))).strip()

            if u_user == usr_clean and u_pass == pass_clean:
                id_u = u.get('id_usuario', u.get('id', 1))
                nombre_u = u.get('nombre', 'Usuario')
                rol_u = u.get('rol', 'administrador')

                # Instanciación flexible según la firma del modelo Usuario
                try:
                    user_obj = Usuario(id_u, nombre_u, u_user, u_pass, rol_u)
                except TypeError:
                    try:
                        user_obj = Usuario(id_usuario=id_u, nombre=nombre_u, username=u_user, clave=u_pass, rol=rol_u)
                    except TypeError:
                        user_obj = Usuario(nombre=nombre_u, username=u_user, clave=u_pass, rol=rol_u)
                        setattr(user_obj, 'id_usuario', id_u)

                return user_obj
        return None

    def listar_usuarios(self):
        return self.datos.get("usuarios", [])

    def obtener_usuarios(self):
        return self.listar_usuarios()

    def registrar_usuario(self, usuario_o_nombre, username=None, clave=None, rol=None):
        usuarios = self.datos.get("usuarios", [])

        if isinstance(usuario_o_nombre, str) and username is not None:
            nombre = usuario_o_nombre
            user_val = str(username)
            clave_val = str(clave)
            rol_val = str(rol)
        else:
            nombre = getattr(usuario_o_nombre, 'nombre', '')
            user_val = getattr(usuario_o_nombre, 'username', getattr(usuario_o_nombre, 'usuario', ''))
            clave_val = getattr(usuario_o_nombre, 'clave', '')
            rol_val = getattr(usuario_o_nombre, 'rol', 'mesero')
            if hasattr(rol_val, 'value'):
                rol_val = rol_val.value

        nuevo_id = max([u.get('id_usuario', u.get('id', 0)) for u in usuarios], default=0) + 1

        nuevo_dict = {
            "id_usuario": nuevo_id,
            "nombre": nombre,
            "username": user_val,
            "clave": clave_val,
            "rol": rol_val
        }

        usuarios.append(nuevo_dict)
        self.datos["usuarios"] = usuarios
        self._guardar_datos()
        return True, "Usuario registrado con éxito."

    def guardar_usuario(self, *args, **kwargs):
        return self.registrar_usuario(*args, **kwargs)

    # -------------------------------------------------------------------------
    # PRODUCTOS
    # -------------------------------------------------------------------------
    def listar_productos(self):
        return self.datos.get("productos", [])

    def obtener_productos(self):
        return self.listar_productos()

    def agregar_producto(self, producto_o_nombre, precio=None, stock=None):
        productos = self.datos.get("productos", [])

        if isinstance(producto_o_nombre, (str, int)):
            nombre = str(producto_o_nombre)
            precio_val = float(precio if precio is not None else 0.0)
            stock_val = int(stock if stock is not None else 0)
        else:
            nombre = getattr(producto_o_nombre, 'nombre', '')
            precio_val = float(getattr(producto_o_nombre, 'precio', 0.0))
            stock_val = int(getattr(producto_o_nombre, 'stock', 0))

        nuevo_id = max([p.get('id_producto', p.get('id', 0)) for p in productos], default=0) + 1

        nuevo_dict = {
            "id_producto": nuevo_id,
            "nombre": nombre,
            "precio": precio_val,
            "stock": stock_val
        }

        productos.append(nuevo_dict)
        self.datos["productos"] = productos
        self._guardar_datos()
        return True, "Producto guardado con éxito."

    def guardar_producto(self, *args, **kwargs):
        return self.agregar_producto(*args, **kwargs)

    # -------------------------------------------------------------------------
    # VENTAS
    # -------------------------------------------------------------------------
    def obtener_historial_ventas(self):
        return self.datos.get("ventas", [])

    def listar_ventas(self):
        return self.obtener_historial_ventas()

    def registrar_venta(self, id_producto: int, cantidad: int, id_usuario: int):
        productos = self.datos.get("productos", [])
        prod_target = None

        for p in productos:
            if p.get('id_producto', p.get('id', None)) == id_producto:
                prod_target = p
                break

        if not prod_target:
            return False, "Producto no encontrado."

        stock_actual = prod_target.get('stock', 0)
        if stock_actual < cantidad:
            return False, f"Stock insuficiente. Disponible: {stock_actual}"

        prod_target['stock'] = stock_actual - cantidad

        ventas = self.datos.get("ventas", [])
        nuevo_id_v = max([v.get('id_venta', v.get('id', 0)) for v in ventas], default=0) + 1
        precio = prod_target.get('precio', 0.0)
        total = round(precio * cantidad, 2)
        fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        nueva_venta = {
            "id_venta": nuevo_id_v,
            "id_producto": id_producto,
            "nombre_producto": prod_target.get('nombre', ''),
            "cantidad": cantidad,
            "total": total,
            "id_usuario": id_usuario,
            "fecha": fecha_str
        }

        ventas.append(nueva_venta)
        self.datos["ventas"] = ventas
        self._guardar_datos()
        return True, "Venta registrada con éxito."