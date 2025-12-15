import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector


class ClientesView(ft.Container):
    """
    MISMA LÓGICA
    NUEVO DISEÑO
    """

    def __init__(self, page, volver_atras):
        super().__init__(expand=True)
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
            bgcolor=ft.Colors.BLUE,
            on_click=self.mostrar_formulario_agregar
        )

        self.header = ft.Container(
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
            content=ft.Row(
                [
                    ft.Text(
                        "👥 Clientes",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900
                    ),
                    ft.ElevatedButton(
                        "Volver",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.volver_atras()
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
                    bgcolor=ft.Colors.GREY_100,
                    content=ft.Column(
                        [
                            self.header,
                            self.lista_clientes
                        ],
                        spacing=25
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
                    padding=20,
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        blur_radius=10,
                        color=ft.Colors.BLACK12
                    ),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f[1] or "",
                                                size=18,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Text(
                                                f"DNI: {f[2] or ''}",
                                                size=12,
                                                color=ft.Colors.GREY_600
                                            )
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=ft.Colors.BLUE_600,
                                                tooltip="Editar",
                                                on_click=lambda e, _id=id_c: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=ft.Colors.RED_600,
                                                tooltip="Eliminar",
                                                on_click=lambda e, _id=id_c: self.confirmar_eliminar_id(_id)
                                            ),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=12),
                            ft.Row(
                                [
                                    ft.Text(f"📞 {f[3] or ''}"),
                                    ft.Text(f"📍 {f[4] or ''}", expand=True),
                                ],
                                spacing=20
                            ),
                            ft.Text(
                                f"ID: {f[0]}",
                                size=11,
                                color=ft.Colors.GREY_500
                            ),
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
        id_field = ft.TextField(label="ID (opcional)")
        nombre = ft.TextField(label="Nombre")
        dni = ft.TextField(label="DNI")
        telefono = ft.TextField(label="Teléfono")
        direccion = ft.TextField(label="Dirección")

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
            bgcolor=ft.Colors.GREY_100,
            alignment=ft.alignment.center,
            content=ft.Card(
                elevation=6,
                content=ft.Container(
                    width=480,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Text("Nuevo Cliente", size=22, weight=ft.FontWeight.BOLD),
                            id_field,
                            nombre,
                            dni,
                            telefono,
                            direccion,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_clientes())
                                    ),
                                    ft.ElevatedButton(
                                        "Guardar",
                                        icon=ft.Icons.SAVE,
                                        on_click=guardar
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END
                            )
                        ],
                        spacing=15
                    )
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

        nombre = ft.TextField(label="Nombre", value=datos[0])
        dni = ft.TextField(label="DNI", value=datos[1])
        telefono = ft.TextField(label="Teléfono", value=datos[2])
        direccion = ft.TextField(label="Dirección", value=datos[3])

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
            bgcolor=ft.Colors.GREY_100,
            alignment=ft.alignment.center,
            content=ft.Card(
                elevation=6,
                content=ft.Container(
                    width=480,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Editar Cliente (ID {id_cliente})",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            ),
                            nombre,
                            dni,
                            telefono,
                            direccion,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_clientes())
                                    ),
                                    ft.ElevatedButton(
                                        "Guardar",
                                        icon=ft.Icons.SAVE,
                                        on_click=guardar
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END
                            )
                        ],
                        spacing=15
                    )
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
            bgcolor=ft.Colors.BLACK54,
            alignment=ft.alignment.center,
            content=ft.Card(
                elevation=10,
                content=ft.Container(
                    width=420,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                size=64,
                                color=ft.Colors.RED
                            ),
                            ft.Text(
                                "Confirmar eliminación",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                f"¿Estás seguro de eliminar el cliente ID {id_cliente}?",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_clientes())
                                    ),
                                    ft.ElevatedButton(
                                        "Eliminar",
                                        icon=ft.Icons.DELETE,
                                        bgcolor=ft.Colors.RED,
                                        color="white",
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
        )
        self.page.update()