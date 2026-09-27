import os
import tkinter as tk
from tkinter import ttk, messagebox

# Intentar importar PIL; si falla, se manejará de forma segura
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from servicios.restaurante_servicio import RestauranteServicio


class LoginView(tk.Tk):
    def __init__(self, servicio: RestauranteServicio, assets_dir: str, on_login_success):
        super().__init__()
        self.servicio = servicio
        self.assets_dir = assets_dir
        self.on_login_success = on_login_success

        self.title("Sistema de Gestión de Restaurante - Inicio de Sesión")
        self.geometry("400x450")
        self.resizable(False, False)

        # Centrar la ventana en pantalla
        self.eval('tk::PlaceWindow . center')

        self.logo_img = None
        self._construir_ui()

    def _construir_ui(self):
        container = ttk.Frame(self, padding=30)
        container.pack(fill=tk.BOTH, expand=True)

        # Cargar logo de forma segura
        logo_path = os.path.join(self.assets_dir, "logo.png")
        if os.path.exists(logo_path):
            try:
                if HAS_PIL:
                    img = Image.open(logo_path).resize((100, 100), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                else:
                    self.logo_img = tk.PhotoImage(file=logo_path)
                
                lbl_logo = ttk.Label(container, image=self.logo_img)
                lbl_logo.pack(pady=(0, 15))
            except Exception:
                pass  # Si ocurre un error cargando el logo, simplemente no se muestra

        # Título
        lbl_titulo = ttk.Label(container, text="Iniciar Sesión", font=("Helvetica", 16, "bold"))
        lbl_titulo.pack(pady=(0, 20))

        # Campo Usuario
        lbl_usuario = ttk.Label(container, text="Nombre de Usuario:")
        lbl_usuario.pack(anchor=tk.W, pady=(5, 2))
        self.txt_usuario = ttk.Entry(container, font=("Helvetica", 11))
        self.txt_usuario.pack(fill=tk.X, pady=(0, 15))
        self.txt_usuario.focus()

        # Campo Clave
        lbl_clave = ttk.Label(container, text="Contraseña:")
        lbl_clave.pack(anchor=tk.W, pady=(5, 2))
        self.txt_clave = ttk.Entry(container, show="*", font=("Helvetica", 11))
        self.txt_clave.pack(fill=tk.X, pady=(0, 20))

        # Vincular tecla Enter al inicio de sesión
        self.txt_clave.bind("<Return>", lambda e: self._callback_login())

        # Botón Ingresar
        btn_ingresar = ttk.Button(container, text="Ingresar", command=self._callback_login)
        btn_ingresar.pack(fill=tk.X, ipady=5)

    def _callback_login(self):
        usuario = self.txt_usuario.get().strip()
        clave = self.txt_clave.get().strip()

        if not usuario or not clave:
            messagebox.showwarning("Atención", "Por favor, complete todos los campos.")
            return

        usuario_valido = self.servicio.autenticar_usuario(usuario, clave)
        if usuario_valido:
            self.destroy()
            self.on_login_success(usuario_valido)
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos.")