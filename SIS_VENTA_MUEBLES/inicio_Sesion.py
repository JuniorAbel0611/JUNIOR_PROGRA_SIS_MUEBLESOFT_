import flet as ft
from muebles.conexion import ConexionDB
import tema


class InicioSesionView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_login_success,
        *,
        app_title: str = "Sistema de Venta de Muebles",
        accent_color: str = None,
        logo_path: str = "assets/logo.png",
    ):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)

        self.page = page
        self.on_login_success = on_login_success
        self.conexion = ConexionDB()
        self.app_title = app_title
        self.accent_color = accent_color or tema.COLOR_PRIMARY
        self.logo_path = logo_path

        # ---------------- INPUTS ----------------
        self.input_usuario = ft.TextField(
            label="Usuario",
            expand=True,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            on_submit=self._on_submit_field,
            **tema.estilo_textfield()
        )

        self.input_contrasena = ft.TextField(
            label="Contraseña",
            expand=True,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            on_submit=self._on_submit_field,
            **tema.estilo_textfield()
        )

        self.chk_recordarme = ft.Checkbox(
            label="Recordarme",
            value=False,
            fill_color=tema.COLOR_PRIMARY,
            check_color=tema.COLOR_ON_PRIMARY
        )

        self.msg_error = ft.Text("", color=tema.COLOR_ERROR, size=13)

        self.btn_login = ft.ElevatedButton(
            "Iniciar sesión",
            expand=True,
            on_click=self.iniciar_sesion,
            **tema.estilo_boton_primario()
        )

        self.btn_forgot = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=self._forgot_password,
            style=ft.ButtonStyle(color=tema.COLOR_PRIMARY)
        )

        # ---------------- COLUMNA IZQUIERDA ----------------
        left_column = ft.Column(
            [
                self._build_brand_section(),
                self.input_usuario,
                self.input_contrasena,
                ft.Row(
                    [
                        self.chk_recordarme,
                        ft.Container(expand=True),
                        self.btn_forgot
                    ],
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
                tema.texto_titulo("Accede al sistema", 18),
                tema.texto_cuerpo(
                    "• Gestión de clientes, productos y ventas\n"
                    "• Acceso seguro por usuario\n"
                    "• Interfaz moderna y adaptable",
                    12
                ),
                tema.crear_divider(),
                ft.Icon(ft.Icons.SHIELD, size=44, color=tema.COLOR_PRIMARY),
                tema.texto_titulo("Seguridad", 16),
                tema.texto_cuerpo(
                    "Usa contraseñas seguras.\n"
                    "Contacta al administrador para cambios.",
                    12
                ),
            ],
            spacing=8
        )

        # ---------------- CARD ----------------
        card = ft.Container(
            **tema.estilo_card(),
            content=ft.Column(
                [
                    left_column,
                    tema.crear_divider(),
                    right_column
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            ),
            width=480
        )

        # ---------------- CENTRADO ----------------
        self.content = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        content=card,
                        col={"xs": 12, "sm": 10, "md": 8, "lg": 6, "xl": 5},
                        alignment=ft.alignment.center,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    # ---------------- BRAND ----------------
    def _build_brand_section(self):
        img = ft.Image(
            src=self.logo_path,
            width=80,
            height=80,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Icon(
                ft.Icons.BUSINESS,
                size=64,
                color=tema.COLOR_PRIMARY
            )
        )

        return ft.Column(
            [
                ft.Container(
                    content=img,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=10)
                ),
                tema.texto_titulo(self.app_title, 20),
                tema.texto_cuerpo("Inicia sesión para continuar", 12)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )

    # ---------------- EVENTOS ----------------
    def _on_submit_field(self, e):
        self.iniciar_sesion(e)

    def _forgot_password(self, e):
        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=tema.COLOR_SURFACE,
            title=tema.texto_titulo("Recuperación de contraseña", 18),
            content=tema.texto_cuerpo(
                "Contacta al administrador del sistema "
                "para restablecer tu contraseña."
            ),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda ev: self._cerrar_dialogo(),
                    style=ft.ButtonStyle(color=tema.COLOR_PRIMARY)
                )
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _cerrar_dialogo(self):
        self.page.dialog.open = False
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
