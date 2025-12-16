import flet as ft
from inicio_Sesion import InicioSesionView
from dashboard_view import DashboardView
import tema

def main(page: ft.Page):
    page.title = "Sistema de Venta de Muebles"
    page.bgcolor = tema.COLOR_FONDO

    # ✅ Página responsiva
    page.expand = True
    page.scroll = ft.ScrollMode.AUTO
    page.window_maximized = True

    # ✅ Contenedor global (aplica a TODO el sistema)
    root = ft.Container(
        expand=True,
        padding=10,
        bgcolor=tema.COLOR_FONDO,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[]
        )
    )

    def cambiar_vista(vista_control):
        root.content.controls.clear()
        root.content.controls.append(vista_control)
        page.update()

    # llamada cuando login es exitoso
    def login_exitoso(user=None):
        print("[DEBUG] login_exitoso called, user:", user)
        dashboard = DashboardView(page, cambiar_vista, user=user, on_logout=logout)
        cambiar_vista(dashboard)

    # callback para cerrar sesión
    def logout():
        print("[DEBUG] logout called")
        login_view = InicioSesionView(page, on_login_success=login_exitoso)
        cambiar_vista(login_view)

    # iniciar en pantalla de login
    login_view = InicioSesionView(page, on_login_success=login_exitoso)
    cambiar_vista(login_view)

    page.add(root)

if __name__ == "__main__":
    ft.app(target=main)
