import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector
import tema


class ClientesView(ft.Container):
    """
    MISMA LÓGICA
    NUEVO DISEÑO - TEMA OSCURO
    """

    def __init__(self, page, volver_atras):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        # =========================
        # COMPONENTES BASE
        # =========================
        self.lista_clientes = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            expand=True
        )

        self.btn_add = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=tema.COLOR_PRIMARY,
            on_click=self.mostrar_formulario_agregar
        )

        self.header = ft.Container(
            **tema.estilo_container_header(),
            content=ft.Row(
                [
                    tema.texto_titulo("👥 Clientes", 24),
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
        self.cargar_clientes()

    # =====================================================
    # VISTA PRINCIPAL (SOLO UI)
    # =====================================================

    def _build_table_view(self):
        self.content = ft.Stack(
            [
                ft.Container(
                    expand=True,
                    padding=30,
                    bgcolor=tema.COLOR_FONDO,
                    content=ft.Column(
                        [
                            self.header,
                            self.lista_clientes
                        ],
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
        try:
            self.page.update()
        except Exception:
            pass

    # =====================================================
    # CRUD — LÓGICA ORIGINAL INTACTA
    # =====================================================

    def cargar_clientes(self):
        self.lista_clientes.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute(
                "SELECT id_cliente, nombre_cliente, dni, telefono, direccion FROM clientes"
            )
            filas = cur.fetchall()

            for f in filas:
                id_c = f[0]

                card = ft.Container(
                    **tema.estilo_card(),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            tema.texto_titulo(f[1] or "", 18),
                                            tema.texto_cuerpo(f"DNI: {f[2] or ''}", 12)
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=tema.COLOR_PRIMARY,
                                                tooltip="Editar",
                                                on_click=lambda e, _id=id_c: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=tema.COLOR_ERROR,
                                                tooltip="Eliminar",
                                                on_click=lambda e, _id=id_c: self.confirmar_eliminar_id(_id)
                                            ),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            tema.crear_divider(),
                            ft.Row(
                                [
                                    tema.texto_cuerpo(f"📞 {f[3] or ''}", 14),
                                    tema.texto_cuerpo(f"📍 {f[4] or ''}", 14),
                                ],
                                spacing=20
                            ),
                            tema.texto_cuerpo(f"ID: {f[0]}", 11),
                        ],
                        spacing=8
                    )
                )

                self.lista_clientes.controls.append(card)

        except Exception as ex:
            print(f"❌ Error al cargar clientes: {ex}")
        finally:
            self.conexion.cerrar(conn)

        try:
            self.page.update()
        except Exception:
            pass

    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        id_field = ft.TextField(label="ID (opcional)", **tema.estilo_textfield())
        nombre = ft.TextField(label="Nombre", **tema.estilo_textfield())
        dni = ft.TextField(label="DNI", **tema.estilo_textfield())
        telefono = ft.TextField(label="Teléfono", **tema.estilo_textfield())
        direccion = ft.TextField(label="Dirección", **tema.estilo_textfield())

        def guardar(ev):
            id_val = (id_field.value or "").strip()
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                if id_val != "":
                    cur.execute(
                        "INSERT INTO clientes (id_cliente, nombre_cliente, dni, telefono, direccion) VALUES (%s,%s,%s,%s,%s)",
                        (int(id_val), nombre.value, dni.value, telefono.value, direccion.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO clientes (nombre_cliente, dni, telefono, direccion) VALUES (%s,%s,%s,%s)",
                        (nombre.value, dni.value, telefono.value, direccion.value)
                    )
                conn.commit()
                self._build_table_view()
                self.cargar_clientes()
            except Exception as ex:
                print(f"❌ Error al agregar cliente: {ex}")
            finally:
                self.conexion.cerrar(conn)

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
                        tema.texto_titulo("Nuevo Cliente", 22),
                        id_field,
                        nombre,
                        dni,
                        telefono,
                        direccion,
                        ft.Row(
                            [
                                ft.TextButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_clientes()),
                                    color=tema.COLOR_PRIMARY
                                ),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=guardar,
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

    # =====================================================

    def mostrar_formulario_editar_id(self, id_cliente):
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT nombre_cliente, dni, telefono, direccion FROM clientes WHERE id_cliente=%s",
                (id_cliente,)
            )
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        nombre = ft.TextField(label="Nombre", value=datos[0], **tema.estilo_textfield())
        dni = ft.TextField(label="DNI", value=datos[1], **tema.estilo_textfield())
        telefono = ft.TextField(label="Teléfono", value=datos[2], **tema.estilo_textfield())
        direccion = ft.TextField(label="Dirección", value=datos[3], **tema.estilo_textfield())

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE clientes SET nombre_cliente=%s,dni=%s,telefono=%s,direccion=%s WHERE id_cliente=%s",
                    (nombre.value, dni.value, telefono.value, direccion.value, id_cliente)
                )
                conn2.commit()
                self._build_table_view()
                self.cargar_clientes()
            finally:
                self.conexion.cerrar(conn2)

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
                        tema.texto_titulo(f"Editar Cliente (ID {id_cliente})", 22),
                        nombre,
                        dni,
                        telefono,
                        direccion,
                        ft.Row(
                            [
                                ft.TextButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_clientes()),
                                    color=tema.COLOR_PRIMARY
                                ),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=guardar,
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

    # =====================================================

    def confirmar_eliminar_id(self, id_cliente):
        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM clientes WHERE id_cliente=%s",
                    (id_cliente,)
                )
                conn.commit()
                self._build_table_view()
                self.cargar_clientes()
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
                        ft.Icon(
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            size=64,
                            color=tema.COLOR_ERROR
                        ),
                        tema.texto_titulo("Confirmar eliminación", 22),
                        tema.texto_cuerpo(
                            f"¿Estás seguro de eliminar el cliente ID {id_cliente}?",
                            14
                        ),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_clientes()),
                                    color=tema.COLOR_PRIMARY
                                ),
                                ft.ElevatedButton(
                                    "Eliminar",
                                    icon=ft.Icons.DELETE,
                                    bgcolor=tema.COLOR_ERROR,
                                    color=tema.COLOR_ON_SURFACE,
                                    on_click=eliminar
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10
                        )
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )
        self.page.update()