import os
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")

    # Asegurar existencia de directorio assets
    os.makedirs(assets_dir, exist_ok=True)

    # Instancia del Servicio Principal (sin pasar la carpeta base_dir)
    servicio = RestauranteServicio()

    def lanzar_main_view(usuario_autenticado):
        app_principal = MainView(
            usuario_actual=usuario_autenticado,
            servicio=servicio,
            assets_dir=assets_dir
        )
        app_principal.mainloop()

    # Iniciar con el Login
    login_app = LoginView(
        servicio=servicio,
        assets_dir=assets_dir,
        on_login_success=lanzar_main_view
    )
    login_app.mainloop()

if __name__ == "__main__":
    main()