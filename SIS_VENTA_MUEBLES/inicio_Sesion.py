import flet as ft
from muebles.conexion import ConexionDB

class InicioSesionView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_login_success,
        *,
        app_title: str = "Sistema de Venta de Muebles",
        accent_color: str = "#5E35B1",
        logo_path: str = None,
    ):
        super().__init__(expand=True, bgcolor="#F6F5FB")
        self.page = page
        self.on_login_success = on_login_success
        self.conexion = ConexionDB()
        self.app_title = app_title
        self.accent_color = accent_color
        self.logo_path = logo_path

        # ---------------- INPUTS RESPONSIVOS ----------------
        self.input_usuario = ft.TextField(
            label="Usuario",
            expand=True,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            on_submit=self._on_submit_field
        )

        self.input_contrasena = ft.TextField(
            label="Contraseña",
            expand=True,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            on_submit=self._on_submit_field
        )

        self.chk_recordarme = ft.Checkbox(label="Recordarme", value=False)
        self.msg_error = ft.Text("", color="red", size=13)

        self.btn_login = ft.ElevatedButton(
            "Iniciar sesión",
            expand=True,
            bgcolor=self.accent_color,
            color="white",
            on_click=self.iniciar_sesion
        )

        self.btn_forgot = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=self._forgot_password
        )

        # ---------------- COLUMNA IZQUIERDA ----------------
        left_column = ft.Column(
            [
                self._build_brand_section(),
                self.input_usuario,
                self.input_contrasena,
                ft.Row(
                    [self.chk_recordarme, ft.Container(expand=True), self.btn_forgot],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                self.msg_error,
                self.btn_login
            ],
            spacing=10,
            expand=True
        )

        # ---------------- COLUMNA DERECHA ----------------
        right_column = ft.Column(
            [
                ft.Text("Accede al sistema", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "• Gestión de clientes, productos y ventas\n"
                    "• Acceso seguro por usuario\n"
                    "• Interfaz moderna y adaptable",
                    size=12,
                    color="#616161"
                ),
                ft.Divider(),
                ft.Icon(ft.Icons.SHIELD, size=44, color=self.accent_color),
                ft.Text("Seguridad", weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Usa contraseñas seguras.\nContacta al administrador para cambios.",
                    size=12,
                    color="#616161"
                ),
            ],
            spacing=8
        )

        # ---------------- CARD (SIN constraints) ----------------
        card = ft.Card(
            elevation=8,
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                padding=20,
                width=420,  # ✅ compatible con tu versión de Flet
                content=ft.Column(
                    [
                        left_column,
                        ft.Divider(),
                        right_column
                    ],
                    spacing=20
                )
            )
        )

        # ---------------- CENTRADO TOTAL ----------------
        self.content = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=card
        )

    # ---------------- BRAND ----------------
    def _build_brand_section(self):
        if self.logo_path:
            img = ft.Image(src=self.logo_path, width=64, height=64)
        else:
            img = ft.Icon(ft.Icons.BUSINESS, size=56, color=self.accent_color)

        return ft.Row(
            [
                img,
                ft.Column(
                    [
                        ft.Text(self.app_title, weight=ft.FontWeight.BOLD, size=16),
                        ft.Text("Inicia sesión para continuar", size=12, color="#616161")
                    ],
                    spacing=2
                )
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER
        )

    # ---------------- EVENTOS ----------------
    def _on_submit_field(self, e):
        self.iniciar_sesion(e)

    def _forgot_password(self, e):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Recuperación de contraseña"),
            content=ft.Text(
                "Contacta al administrador del sistema para restablecer tu contraseña."
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda ev: self.page.dialog.close())
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ---------------- LOGIN ----------------
    def iniciar_sesion(self, e=None):
        username = (self.input_usuario.value or "").strip()
        password = (self.input_contrasena.value or "").strip()

        if not username or not password:
            self.msg_error.value = "Debes ingresar usuario y contraseña."
            self.page.update()
            return

        self.btn_login.disabled = True
        self.btn_login.text = "Verificando..."
        self.page.update()

        try:
            conn = self.conexion.conectar()
            if conn is None:
                self.msg_error.value = "Error de conexión a la base de datos."
                return

            cur = conn.cursor()
            cur.execute(
                "SELECT id_usuario, nombre_usuario, usuario, contrasena, rol "
                "FROM usuarios WHERE usuario=%s LIMIT 1",
                (username,)
            )
            row = cur.fetchone()

            if not row or password != row[3]:
                self.msg_error.value = "Usuario o contraseña incorrectos."
                return

            user = {
                "id_usuario": row[0],
                "nombre_usuario": row[1],
                "usuario": row[2],
                "rol": row[4],
            }

            self.on_login_success(user)

        except Exception as ex:
            self.msg_error.value = f"Error: {ex}"

        finally:
            self.btn_login.disabled = False
            self.btn_login.text = "Iniciar sesión"
            try:
                self.conexion.cerrar(conn)
            except Exception:
                pass
            self.page.update()
