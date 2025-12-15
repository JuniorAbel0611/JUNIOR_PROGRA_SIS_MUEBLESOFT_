import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector


class VentasView(ft.Container):
    def __init__(self, page, volver_atras):
        super().__init__(expand=True)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        # =========================
        # COMPONENTES BASE
        # =========================
        self.lista_ventas = ft.Column(
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
                        "💳 Gestión de Ventas",
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
        self.cargar_ventas()

    # =====================================================
    # VISTA PRINCIPAL
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
                            self.lista_ventas
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
        self.page.update()

    # =====================================================
    # LISTADO EN CARDS (MISMA CONSULTA)
    # =====================================================

    def cargar_ventas(self):
        print(">> cargar_ventas() llamado")
        self.lista_ventas.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                print("❌ No hay conexión")
                return

            cur = conn.cursor()
            cur.execute(
                "SELECT id_venta, id_cliente, id_usuario, fecha_venta, total FROM ventas"
            )
            filas = cur.fetchall()

            for f in filas:
                id_v = f[0]

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
                                    ft.Text(
                                        f"Venta #{id_v}",
                                        size=18,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=ft.Colors.BLUE,
                                                tooltip="Editar",
                                                on_click=lambda e, _id=id_v: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=ft.Colors.RED,
                                                tooltip="Eliminar",
                                                on_click=lambda e, _id=id_v: self.confirmar_eliminar_id(_id)
                                            ),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(),
                            ft.Text(f"Cliente ID: {f[1] if f[1] is not None else ''}"),
                            ft.Text(f"Usuario ID: {f[2] if f[2] is not None else ''}"),
                            ft.Text(f"Fecha: {f[3] if f[3] is not None else ''}"),
                            ft.Text(
                                f"Total: S/ {f[4] if f[4] is not None else ''}",
                                weight=ft.FontWeight.BOLD
                            ),
                        ],
                        spacing=8
                    )
                )

                self.lista_ventas.controls.append(card)

            print(f">> {len(filas)} ventas añadidas")
        except Exception as ex:
            print(f"❌ Error al cargar ventas: {ex}")
        finally:
            self.conexion.cerrar(conn)

        self.page.update()

    # =====================================================
    # FORMULARIO AGREGAR (MISMA LÓGICA)
    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        print(">> mostrar_formulario_agregar() ventas")

        id_field = ft.TextField(label="ID (opcional)")
        id_cliente = ft.TextField(label="ID Cliente")
        id_usuario = ft.TextField(label="ID Usuario")
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)")
        total = ft.TextField(label="Total")

        def guardar(ev):
            id_val = (id_field.value or "").strip()
            conn = self.conexion.conectar()
            if conn is None:
                print("❌ No hay conexión al guardar venta")
                return
            try:
                cur = conn.cursor()
                if id_val != "":
                    cur.execute(
                        "INSERT INTO ventas (id_venta, id_cliente, id_usuario, fecha_venta, total) VALUES (%s,%s,%s,%s,%s)",
                        (int(id_val), id_cliente.value, id_usuario.value, fecha.value, total.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO ventas (id_cliente, id_usuario, fecha_venta, total) VALUES (%s,%s,%s,%s)",
                        (id_cliente.value, id_usuario.value, fecha.value, total.value)
                    )
                conn.commit()
                print(">> Venta insertada correctamente")
                self._build_table_view()
                self.cargar_ventas()
            except mysql.connector.IntegrityError as ie:
                print(f"❌ Integridad DB: {ie}")
            except Exception as ex:
                print(f"❌ Error al agregar venta: {ex}")
            finally:
                self.conexion.cerrar(conn)

        self._mostrar_formulario(
            "➕ Nueva Venta",
            [id_field, id_cliente, id_usuario, fecha, total],
            guardar
        )

    # =====================================================
    # FORMULARIO EDITAR (MISMA LÓGICA)
    # =====================================================

    def mostrar_formulario_editar_id(self, id_venta):
        print(f">> mostrar_formulario_editar_id({id_venta})")
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_cliente, id_usuario, fecha_venta, total FROM ventas WHERE id_venta=%s",
                (id_venta,)
            )
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        id_cliente = ft.TextField(label="ID Cliente", value=str(datos[0]) if datos[0] else "")
        id_usuario = ft.TextField(label="ID Usuario", value=str(datos[1]) if datos[1] else "")
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)", value=str(datos[2]) if datos[2] else "")
        total = ft.TextField(label="Total", value=str(datos[3]) if datos[3] else "")

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE ventas SET id_cliente=%s, id_usuario=%s, fecha_venta=%s, total=%s WHERE id_venta=%s",
                    (id_cliente.value, id_usuario.value, fecha.value, total.value, id_venta)
                )
                conn2.commit()
                print(">> Venta actualizada correctamente")
                self._build_table_view()
                self.cargar_ventas()
            finally:
                self.conexion.cerrar(conn2)

        self._mostrar_formulario(
            f"✏️ Editar Venta (ID {id_venta})",
            [id_cliente, id_usuario, fecha, total],
            guardar
        )

    # =====================================================
    # CONFIRMAR ELIMINAR
    # =====================================================

    def confirmar_eliminar_id(self, id_venta):
        print(f">> confirmar_eliminar_id({id_venta})")

        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM ventas WHERE id_venta=%s", (id_venta,))
                conn.commit()
                print(">> Venta eliminada correctamente")
                self._build_table_view()
                self.cargar_ventas()
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
                                f"¿Eliminar venta ID {id_venta}?",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_ventas())
                                    ),
                                    ft.ElevatedButton(
                                        "Eliminar",
                                        icon=ft.Icons.DELETE,
                                        bgcolor=ft.Colors.RED,
                                        color="white",
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
        )
        self.page.update()

    # =====================================================
    # FORMULARIO BASE (REUTILIZABLE)
    # =====================================================

    def _mostrar_formulario(self, titulo, campos, on_save):
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
                            ft.Text(titulo, size=22, weight=ft.FontWeight.BOLD),
                            *campos,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_ventas())
                                    ),
                                    ft.ElevatedButton(
                                        "Guardar",
                                        icon=ft.Icons.SAVE,
                                        on_click=on_save
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