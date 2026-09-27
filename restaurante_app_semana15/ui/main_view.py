import os
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from servicios.restaurante_servicio import RestauranteServicio
from modelos.usuario import Usuario
from modelos.producto import Producto


class MainView(tk.Tk):
    def __init__(self, usuario_actual: Usuario, servicio: RestauranteServicio, assets_dir: str):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.servicio = servicio
        self.assets_dir = assets_dir

        self.rol_str = getattr(self.usuario_actual, 'rol', 'administrador')
        if hasattr(self.rol_str, 'value'):
            self.rol_str = self.rol_str.value

        nombre_usr = getattr(self.usuario_actual, 'nombre', 'Usuario')
        self.title(f"Sistema de Restaurante - Usuario: {nombre_usr} ({self.rol_str})")
        self.geometry("980x680")
        self.minsize(850, 550)

        self.iconos = {}
        self._cargar_recursos()
        self._construir_ui()

    def _cargar_recursos(self):
        icon_files = {
            "logo": "logo.png",
            "ventas": "icon_sale.png",
            "productos": "icon_product.png",
            "usuarios": "icon_user.png"
        }
        for key, filename in icon_files.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                try:
                    if HAS_PIL:
                        img = Image.open(path).resize((18, 18), Image.Resampling.LANCZOS)
                        self.iconos[key] = ImageTk.PhotoImage(img)
                    else:
                        self.iconos[key] = tk.PhotoImage(file=path)
                except Exception:
                    self.iconos[key] = None
            else:
                self.iconos[key] = None

    def _agregar_tab_seguro(self, frame, titulo: str, clave_icono: str):
        kwargs = {"text": titulo}
        icono = self.iconos.get(clave_icono)
        if icono is not None:
            kwargs["image"] = icono
            kwargs["compound"] = tk.LEFT
        self.notebook.add(frame, **kwargs)

    def _construir_ui(self):
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        nombre_usr = getattr(self.usuario_actual, 'nombre', 'Usuario')
        lbl_info = ttk.Label(
            header_frame,
            text=f"Bienvenido/a, {nombre_usr}  |  Rol: {str(self.rol_str).upper()}",
            font=("Helvetica", 11, "bold")
        )
        lbl_info.pack(side=tk.LEFT)

        btn_salir = ttk.Button(header_frame, text="Cerrar Sesión", command=self.destroy)
        btn_salir.pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 1. Pestaña Registro de Ventas
        self.tab_ventas = ttk.Frame(self.notebook, padding=10)
        self._agregar_tab_seguro(self.tab_ventas, " Registro de Ventas ", "ventas")
        self._construir_tab_ventas()

        # 2. Pestaña Gestión de Productos
        self.tab_productos = ttk.Frame(self.notebook, padding=10)
        self._agregar_tab_seguro(self.tab_productos, " Gestión de Productos ", "productos")
        self._construir_tab_productos()

        # 3. Pestaña Gestión de Usuarios
        self.tab_usuarios = ttk.Frame(self.notebook, padding=10)
        self._agregar_tab_seguro(self.tab_usuarios, " Gestión de Usuarios ", "usuarios")
        self._construir_tab_usuarios()

    # -------------------------------------------------------------------------
    # TAB 1: REGISTRO DE VENTAS
    # -------------------------------------------------------------------------
    def _construir_tab_ventas(self):
        frame_top = ttk.LabelFrame(self.tab_ventas, text="Nueva Venta", padding=10)
        frame_top.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_top, text="Producto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cb_producto_venta = ttk.Combobox(frame_top, state="readonly", width=30)
        self.cb_producto_venta.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="Cantidad:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.sp_cantidad_venta = ttk.Spinbox(frame_top, from_=1, to=100, width=8)
        self.sp_cantidad_venta.grid(row=0, column=3, padx=5, pady=5)
        self.sp_cantidad_venta.set(1)

        btn_registrar = ttk.Button(frame_top, text="Registrar Venta", command=self._registrar_venta)
        btn_registrar.grid(row=0, column=4, padx=15, pady=5)

        self._actualizar_combo_productos()

        frame_tabla = ttk.LabelFrame(self.tab_ventas, text="Historial de Ventas", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        cols_v = ("col_id", "col_prod", "col_cant", "col_tot", "col_fec")
        self.tree_ventas = ttk.Treeview(frame_tabla, columns=cols_v, show="headings")
        self.tree_ventas.heading("col_id", text="ID Venta")
        self.tree_ventas.heading("col_prod", text="Producto")
        self.tree_ventas.heading("col_cant", text="Cantidad")
        self.tree_ventas.heading("col_tot", text="Total ($)")
        self.tree_ventas.heading("col_fec", text="Fecha")

        self.tree_ventas.column("col_id", width=80, anchor=tk.CENTER)
        self.tree_ventas.column("col_cant", width=80, anchor=tk.CENTER)
        self.tree_ventas.column("col_tot", width=100, anchor=tk.E)

        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=vsb.set)

        self.tree_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._cargar_tabla_ventas()

    def _actualizar_combo_productos(self):
        try:
            fn = getattr(self.servicio, 'listar_productos', getattr(self.servicio, 'obtener_productos', None))
            productos = fn() if fn else []
            nombres = []
            for p in productos:
                if isinstance(p, dict):
                    id_p = p.get('id_producto', p.get('id', ''))
                    nom = p.get('nombre', '')
                    pre = p.get('precio', 0.0)
                    stk = p.get('stock', 0)
                else:
                    id_p = getattr(p, 'id_producto', getattr(p, 'id', ''))
                    nom = getattr(p, 'nombre', '')
                    pre = getattr(p, 'precio', 0.0)
                    stk = getattr(p, 'stock', 0)

                if stk > 0:
                    nombres.append(f"{id_p} - {nom} (${pre:.2f})")

            self.cb_producto_venta['values'] = nombres
            if nombres:
                self.cb_producto_venta.current(0)
        except Exception:
            pass

    def _cargar_tabla_ventas(self):
        try:
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)

            fn = getattr(self.servicio, 'obtener_historial_ventas', getattr(self.servicio, 'listar_ventas', None))
            ventas = fn() if fn else []
            for v in ventas:
                if isinstance(v, dict):
                    id_v = v.get('id_venta', v.get('id', ''))
                    prod = v.get('nombre_producto', v.get('producto', ''))
                    cant = v.get('cantidad', 0)
                    tot = v.get('total', 0.0)
                    fec = v.get('fecha', '')
                else:
                    id_v = getattr(v, 'id_venta', getattr(v, 'id', ''))
                    prod = getattr(v, 'nombre_producto', getattr(v, 'producto', ''))
                    cant = getattr(v, 'cantidad', 0)
                    tot = getattr(v, 'total', 0.0)
                    fec = getattr(v, 'fecha', '')

                self.tree_ventas.insert("", tk.END, values=(id_v, prod, cant, f"${tot:.2f}", fec))
        except Exception:
            pass

    def _registrar_venta(self):
        seleccion = self.cb_producto_venta.get()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto.")
            return

        try:
            id_prod = int(seleccion.split(" - ")[0])
            cantidad = int(self.sp_cantidad_venta.get())

            # Extrae id_usuario probando diferentes nombres de atributos/métodos
            id_usr = getattr(
                self.usuario_actual, 'id_usuario',
                getattr(self.usuario_actual, 'id', 1)
            )

            fn = getattr(self.servicio, 'registrar_venta', getattr(self.servicio, 'crear_venta', None))
            if fn:
                res = fn(id_prod, cantidad, id_usr)
                exito, msj = res if isinstance(res, tuple) else (True, "Venta registrada con éxito.")
                
                if exito:
                    messagebox.showinfo("Éxito", msj if msj else "Venta registrada con éxito.")
                    self._cargar_tabla_ventas()
                    self._actualizar_combo_productos()
                    self._cargar_tabla_productos()
                else:
                    messagebox.showerror("Error", msj)
            else:
                messagebox.showerror("Error", "No existe un método para registrar ventas en el servicio.")

        except ValueError:
            messagebox.showerror("Error", "Asegúrese de seleccionar un producto y que la cantidad sea un número válido.")
        except Exception as e:
            messagebox.showerror("Error de Ejecución", f"Detalle del error:\n{e}")

    # -------------------------------------------------------------------------
    # TAB 2: GESTIÓN DE PRODUCTOS
    # -------------------------------------------------------------------------
    def _construir_tab_productos(self):
        frame_form = ttk.LabelFrame(self.tab_productos, text="Administrar Producto", padding=10)
        frame_form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.txt_prod_nombre = ttk.Entry(frame_form, width=25)
        self.txt_prod_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Precio ($):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.txt_prod_precio = ttk.Entry(frame_form, width=12)
        self.txt_prod_precio.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_form, text="Stock:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.txt_prod_stock = ttk.Entry(frame_form, width=12)
        self.txt_prod_stock.grid(row=0, column=5, padx=5, pady=5)

        btn_guardar = ttk.Button(frame_form, text="Agregar / Guardar", command=self._guardar_producto)
        btn_guardar.grid(row=0, column=6, padx=10, pady=5)

        frame_tabla = ttk.LabelFrame(self.tab_productos, text="Catálogo de Productos", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        cols_p = ("c_id", "c_nombre", "c_precio", "c_stock")
        self.tree_prods = ttk.Treeview(frame_tabla, columns=cols_p, show="headings")

        self.tree_prods.heading("c_id", text="ID")
        self.tree_prods.heading("c_nombre", text="Nombre del Producto")
        self.tree_prods.heading("c_precio", text="Precio ($)")
        self.tree_prods.heading("c_stock", text="Stock Disponible")

        self.tree_prods.column("c_id", width=80, anchor=tk.CENTER)
        self.tree_prods.column("c_nombre", width=320, anchor=tk.W)
        self.tree_prods.column("c_precio", width=120, anchor=tk.E)
        self.tree_prods.column("c_stock", width=120, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_prods.yview)
        self.tree_prods.configure(yscrollcommand=vsb.set)

        self.tree_prods.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._cargar_tabla_productos()

    def _cargar_tabla_productos(self):
        try:
            for item in self.tree_prods.get_children():
                self.tree_prods.delete(item)

            fn = getattr(self.servicio, 'listar_productos', getattr(self.servicio, 'obtener_productos', None))
            productos = fn() if fn else []

            for p in productos:
                if isinstance(p, dict):
                    id_val = p.get('id_producto', p.get('id', ''))
                    nom_val = p.get('nombre', '')
                    pre_val = p.get('precio', 0.0)
                    stk_val = p.get('stock', 0)
                else:
                    id_val = getattr(p, 'id_producto', getattr(p, 'id', ''))
                    nom_val = getattr(p, 'nombre', '')
                    pre_val = getattr(p, 'precio', 0.0)
                    stk_val = getattr(p, 'stock', 0)

                try:
                    pre_float = float(pre_val)
                    precio_fmt = f"${pre_float:.2f}"
                except (ValueError, TypeError):
                    precio_fmt = f"${pre_val}"

                self.tree_prods.insert("", tk.END, values=(id_val, nom_val, precio_fmt, stk_val))

        except Exception as e:
            print(f"Error al cargar la tabla de productos: {e}")

    def _guardar_producto(self):
        nombre = self.txt_prod_nombre.get().strip()
        precio_str = self.txt_prod_precio.get().strip()
        stock_str = self.txt_prod_stock.get().strip()

        if not nombre or not precio_str or not stock_str:
            messagebox.showwarning("Atención", "Complete todos los campos del producto.")
            return

        try:
            precio = float(precio_str)
            stock = int(stock_str)

            try:
                nuevo_p = Producto(nombre, precio, stock)
            except TypeError:
                try:
                    nuevo_p = Producto(nombre=nombre, precio=precio)
                    nuevo_p.stock = stock
                except TypeError:
                    nuevo_p = Producto(nombre=nombre, precio=precio, stock=stock)

            fn_guardar = None
            for nombre_metodo in ['agregar_producto', 'guardar_producto', 'crear_producto', 'insertar_producto']:
                if hasattr(self.servicio, nombre_metodo):
                    fn_guardar = getattr(self.servicio, nombre_metodo)
                    break

            if fn_guardar:
                try:
                    res = fn_guardar(nuevo_p)
                except TypeError:
                    res = fn_guardar(nombre, precio, stock)

                exito, msj = res if isinstance(res, tuple) else (True, "Producto guardado con éxito.")

                if exito:
                    messagebox.showinfo("Éxito", msj if msj else "Producto guardado con éxito.")
                    self.txt_prod_nombre.delete(0, tk.END)
                    self.txt_prod_precio.delete(0, tk.END)
                    self.txt_prod_stock.delete(0, tk.END)
                    self._cargar_tabla_productos()
                    self._actualizar_combo_productos()
                else:
                    messagebox.showerror("Error", msj)
            else:
                messagebox.showerror("Error", "No se encontró un método para agregar productos en el servicio.")

        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser valores numéricos válidos.")
        except Exception as e:
            messagebox.showerror("Error de Ejecución", f"Detalle del error:\n{e}")

    # -------------------------------------------------------------------------
    # TAB 3: GESTIÓN DE USUARIOS
    # -------------------------------------------------------------------------
    def _construir_tab_usuarios(self):
        frame_form = ttk.LabelFrame(self.tab_usuarios, text="Registrar Nuevo Usuario", padding=10)
        frame_form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.txt_usr_nombre = ttk.Entry(frame_form, width=20)
        self.txt_usr_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Usuario:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.txt_usr_username = ttk.Entry(frame_form, width=15)
        self.txt_usr_username.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_form, text="Clave:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.txt_usr_clave = ttk.Entry(frame_form, show="*", width=15)
        self.txt_usr_clave.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_form, text="Rol:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.cb_usr_rol = ttk.Combobox(frame_form, values=["mesero", "administrador"], state="readonly", width=12)
        self.cb_usr_rol.grid(row=0, column=7, padx=5, pady=5)
        self.cb_usr_rol.current(0)

        btn_guardar_usr = ttk.Button(frame_form, text="Registrar", command=self._guardar_usuario)
        btn_guardar_usr.grid(row=0, column=8, padx=10, pady=5)

        frame_tabla = ttk.LabelFrame(self.tab_usuarios, text="Usuarios Registrados", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        cols_u = ("c_uid", "c_unombre", "c_uuser", "c_urol")
        self.tree_usrs = ttk.Treeview(frame_tabla, columns=cols_u, show="headings")
        self.tree_usrs.heading("c_uid", text="ID")
        self.tree_usrs.heading("c_unombre", text="Nombre Completo")
        self.tree_usrs.heading("c_uuser", text="Nombre de Usuario")
        self.tree_usrs.heading("c_urol", text="Rol")

        self.tree_usrs.column("c_uid", width=60, anchor=tk.CENTER)
        self.tree_usrs.column("c_unombre", width=250, anchor=tk.W)
        self.tree_usrs.column("c_uuser", width=200, anchor=tk.W)
        self.tree_usrs.column("c_urol", width=120, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_usrs.yview)
        self.tree_usrs.configure(yscrollcommand=vsb.set)

        self.tree_usrs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._cargar_tabla_usuarios()

    def _cargar_tabla_usuarios(self):
        try:
            for item in self.tree_usrs.get_children():
                self.tree_usrs.delete(item)

            fn = getattr(self.servicio, 'listar_usuarios', getattr(self.servicio, 'obtener_usuarios', None))
            usuarios = fn() if fn else []

            for u in usuarios:
                if isinstance(u, dict):
                    id_u = u.get('id_usuario', u.get('id', ''))
                    nom = u.get('nombre', '')
                    usr = u.get('username', u.get('usuario', ''))
                    rol = u.get('rol', '')
                else:
                    id_u = getattr(u, 'id_usuario', getattr(u, 'id', ''))
                    nom = getattr(u, 'nombre', '')
                    usr = getattr(u, 'username', getattr(u, 'usuario', ''))
                    rol = getattr(u, 'rol', '')

                self.tree_usrs.insert("", tk.END, values=(id_u, nom, usr, rol))
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    def _guardar_usuario(self):
        nombre = self.txt_usr_nombre.get().strip()
        username = self.txt_usr_username.get().strip()
        clave = self.txt_usr_clave.get().strip()
        rol = self.cb_usr_rol.get().strip()

        if not nombre or not username or not clave or not rol:
            messagebox.showwarning("Atención", "Complete todos los campos del usuario.")
            return

        try:
            try:
                nuevo_u = Usuario(nombre, username, clave, rol)
            except TypeError:
                nuevo_u = Usuario(nombre=nombre, username=username, clave=clave, rol=rol)

            fn_guardar = None
            for nombre_metodo in ['registrar_usuario', 'guardar_usuario', 'crear_usuario', 'agregar_usuario']:
                if hasattr(self.servicio, nombre_metodo):
                    fn_guardar = getattr(self.servicio, nombre_metodo)
                    break

            if fn_guardar:
                try:
                    res = fn_guardar(nuevo_u)
                except TypeError:
                    res = fn_guardar(nombre, username, clave, rol)

                exito, msj = res if isinstance(res, tuple) else (True, "Usuario registrado con éxito.")

                if exito:
                    messagebox.showinfo("Éxito", msj if msj else "Usuario registrado con éxito.")
                    self.txt_usr_nombre.delete(0, tk.END)
                    self.txt_usr_username.delete(0, tk.END)
                    self.txt_usr_clave.delete(0, tk.END)
                    self._cargar_tabla_usuarios()
                else:
                    messagebox.showerror("Error", msj)
            else:
                messagebox.showerror("Error", "No se encontró un método para registrar usuarios en el servicio.")

        except Exception as e:
            messagebox.showerror("Error de Ejecución", f"Detalle del error:\n{e}")