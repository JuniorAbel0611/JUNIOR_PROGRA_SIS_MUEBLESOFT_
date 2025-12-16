import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector
import tema


class UsuariosView(ft.Container):
    def __init__(self, page, volver_atras):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        self.lista_usuarios = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=20, expand=True)

        self.btn_add = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=tema.COLOR_PRIMARY,
            on_click=self.mostrar_formulario_agregar
        )

        self.header = ft.Container(
            **tema.estilo_container_header(),
            content=ft.Row(
                [
                    tema.texto_titulo("👤 Gestión de Usuarios", 24),
                    ft.ElevatedButton(
                        "Volver",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.volver_atras(),
                        **tema.estilo_boton_secundario()
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self._build_table_view()
        self.cargar_usuarios()

    # =====================================================
    # VISTA PRINCIPAL
    # =====================================================

    def _build_table_view(self):
        self.content = ft.Stack(
            [
                ft.Container(
                    expand=True,
                    padding=30,
                    bgcolor=tema.COLOR_FONDO,
                    content=ft.Column(
                        [self.header, self.lista_usuarios],
                        spacing=25,
                        expand=True
                    )
                ),
                ft.Container(
                    right=30,
                    bottom=30,
                    content=self.btn_add
                )
            ],
            expand=True
        )
        self.page.update()

    # =====================================================
    # LISTADO EN CARDS (MISMA CONSULTA)
    # =====================================================

    def cargar_usuarios(self):
        self.lista_usuarios.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                return
            cur = conn.cursor()
            cur.execute("SELECT id_usuario, nombre_usuario, usuario, rol FROM usuarios")
            filas = cur.fetchall()

            for f in filas:
                id_u = f[0]

                card = ft.Container(
                    **tema.estilo_card(),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    tema.texto_titulo(f"ID: {id_u}", 18),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                tooltip="Editar",
                                                icon_color=tema.COLOR_PRIMARY,
                                                on_click=lambda e, _id=id_u: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                tooltip="Eliminar",
                                                icon_color=tema.COLOR_ERROR,
                                                on_click=lambda e, _id=id_u: self.confirmar_eliminar_id(_id)
                                            )
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            tema.crear_divider(),
                            tema.texto_cuerpo(f"Nombre: {f[1] or ''}", 14),
                            tema.texto_cuerpo(f"Usuario: {f[2] or ''}", 14),
                            tema.texto_cuerpo(f"Rol: {f[3] or ''}", 14)
                        ],
                        spacing=8
                    )
                )

                self.lista_usuarios.controls.append(card)
        finally:
            self.conexion.cerrar(conn)

        self.page.update()

    # =====================================================
    # FORMULARIO AGREGAR (MISMA LÓGICA)
    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        id_field = ft.TextField(label="ID (opcional)", **tema.estilo_textfield())
        nombre = ft.TextField(label="Nombre", **tema.estilo_textfield())
        usuario = ft.TextField(label="Usuario", **tema.estilo_textfield())
        contrasena = ft.TextField(label="Contraseña", password=True, **tema.estilo_textfield())
        rol = ft.TextField(label="Rol", **tema.estilo_textfield())

        def guardar(ev):
            id_val = (id_field.value or "").strip()
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                if id_val:
                    cur.execute(
                        "INSERT INTO usuarios (id_usuario, nombre_usuario, usuario, contrasena, rol) VALUES (%s,%s,%s,%s,%s)",
                        (int(id_val), nombre.value, usuario.value, contrasena.value, rol.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO usuarios (nombre_usuario, usuario, contrasena, rol) VALUES (%s,%s,%s,%s)",
                        (nombre.value, usuario.value, contrasena.value, rol.value)
                    )
                conn.commit()
                self._build_table_view()
                self.cargar_usuarios()
            finally:
                self.conexion.cerrar(conn)

        self._mostrar_formulario(
            "➕ Nuevo Usuario",
            [id_field, nombre, usuario, contrasena, rol],
            guardar
        )

    # =====================================================
    # FORMULARIO EDITAR (MISMA LÓGICA)
    # =====================================================

    def mostrar_formulario_editar_id(self, id_usuario):
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT nombre_usuario, usuario, contrasena, rol FROM usuarios WHERE id_usuario=%s",
                (id_usuario,)
            )
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        nombre = ft.TextField(label="Nombre", value=datos[0], **tema.estilo_textfield())
        usuario = ft.TextField(label="Usuario", value=datos[1], **tema.estilo_textfield())
        contrasena = ft.TextField(label="Contraseña", value=datos[2], password=True, **tema.estilo_textfield())
        rol = ft.TextField(label="Rol", value=datos[3], **tema.estilo_textfield())

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE usuarios SET nombre_usuario=%s, usuario=%s, contrasena=%s, rol=%s WHERE id_usuario=%s",
                    (nombre.value, usuario.value, contrasena.value, rol.value, id_usuario)
                )
                conn2.commit()
                self._build_table_view()
                self.cargar_usuarios()
            finally:
                self.conexion.cerrar(conn2)

        self._mostrar_formulario(
            f"✏️ Editar Usuario (ID {id_usuario})",
            [nombre, usuario, contrasena, rol],
            guardar
        )

    # =====================================================
    # CONFIRMAR ELIMINAR
    # =====================================================

    def confirmar_eliminar_id(self, id_usuario):
        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
                conn.commit()
                self._build_table_view()
                self.cargar_usuarios()
            finally:
                self.conexion.cerrar(conn)

        self.content = ft.Container(
            expand=True,
            bgcolor=tema.COLOR_FONDO,
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
            content=ft.Container(
                **tema.estilo_card(),
                width=420,
                constraints=ft.BoxConstraints(max_width=420),
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER, size=60, color=tema.COLOR_ERROR),
                        tema.texto_titulo("Confirmar eliminación", 20),
                        tema.texto_cuerpo(f"¿Eliminar usuario ID {id_usuario}?", 14),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_usuarios()),
                                    color=tema.COLOR_PRIMARY
                                ),
                                ft.ElevatedButton(
                                    "Eliminar",
                                    bgcolor=tema.COLOR_ERROR,
                                    color=tema.COLOR_ON_SURFACE,
                                    on_click=eliminar
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        )
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )
        self.page.update()

    # =====================================================
    # FORMULARIO BASE
    # =====================================================

    def _mostrar_formulario(self, titulo, campos, on_save):
        self.content = ft.Container(
            expand=True,
            bgcolor=tema.COLOR_FONDO,
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
            content=ft.Container(
                **tema.estilo_card(),
                width=480,
                constraints=ft.BoxConstraints(max_width=480),
                content=ft.Column(
                    [
                        tema.texto_titulo(titulo, 22),
                        *campos,
                        ft.Row(
                            [
                                ft.TextButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_usuarios()),
                                    color=tema.COLOR_PRIMARY
                                ),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=on_save,
                                    **tema.estilo_boton_primario()
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        )
                    ],
                    spacing=15
                )
            )
        )
        self.page.update()