import flet as ft
from inicio_Sesion import InicioSesionView
from dashboard_view import DashboardView

def main(page: ft.Page):
    page.title = "Sistema de Venta de Muebles"

    # ✅ Página responsiva
    page.expand = True
    page.scroll = ft.ScrollMode.AUTO
    page.window_maximized = True

    # ✅ Contenedor global (aplica a TODO el sistema)
    root = ft.Container(
        expand=True,
        padding=10,
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
        dashboard = DashboardView(page, cambiar_vista, user=user)
        cambiar_vista(dashboard)

    # iniciar en pantalla de login
    login_view = InicioSesionView(page, on_login_success=login_exitoso)
    cambiar_vista(login_view)

    page.add(root)

if __name__ == "__main__":
    ft.app(target=main)
