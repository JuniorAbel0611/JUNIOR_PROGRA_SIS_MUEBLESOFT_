import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector

class DetalleVentaView(ft.Container):
    """
    Vista moderna de Detalle de Ventas
    Lógica CRUD intacta
    """

    def __init__(self, page, volver_atras):
        super().__init__(expand=True)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        self.lista_detalles = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            expand=True
        )

        self.btn_add = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.GREEN,
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
                        "📦 Detalle de Ventas",
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
        self.cargar_detalles()

    # ========================================
    # VISTA PRINCIPAL
    # ========================================

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
                            self.lista_detalles
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

    # ========================================
    # CRUD
    # ========================================

    def cargar_detalles(self):
        print(">> cargar_detalles() llamado")
        self.lista_detalles.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                print("❌ No hay conexión")
                return
            cur = conn.cursor()
            cur.execute("SELECT id_detalle, id_venta, id_producto, cantidad, precio_unitario, subtotal FROM detalle_venta")
            filas = cur.fetchall()
            for r in filas:
                id_d = r[0]

                card = ft.Container(
                    padding=20,
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"Detalle #{r[0]}", size=18, weight=ft.FontWeight.BOLD),
                                            ft.Text(f"Venta ID: {r[1]}", size=12, color=ft.Colors.GREY_600),
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=ft.Colors.BLUE_600,
                                                tooltip="Editar",
                                                on_click=lambda e, _id=id_d: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=ft.Colors.RED_600,
                                                tooltip="Eliminar",
                                                on_click=lambda e, _id=id_d: self.confirmar_eliminar_id(_id)
                                            ),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=12),
                            ft.Row(
                                [
                                    ft.Text(f"Producto ID: {r[2]}"),
                                    ft.Text(f"Cantidad: {r[3]}"),
                                    ft.Text(f"Precio unitario: ${r[4]}"),
                                    ft.Text(f"Subtotal: ${r[5]}", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        spacing=10
                    )
                )

                self.lista_detalles.controls.append(card)

            print(f">> {len(filas)} detalles añadidos")

        except Exception as ex:
            print(f"❌ Error al cargar detalle_venta: {ex}")
        finally:
            self.conexion.cerrar(conn)

        try:
            self.page.update()
        except Exception:
            pass

    # ========================================
    # FORMULARIOS
    # ========================================

    def mostrar_formulario_agregar(self, e=None):
        print(">> mostrar_formulario_agregar() detalle_venta")
        id_field = ft.TextField(label="ID (opcional)", hint_text="Dejar vacío para autoincrement", width=200)
        id_venta = ft.TextField(label="ID Venta")
        id_producto = ft.TextField(label="ID Producto")
        cantidad = ft.TextField(label="Cantidad")
        precio_unitario = ft.TextField(label="Precio unitario")
        subtotal = ft.TextField(label="Subtotal")

        def guardar(ev):
            id_val = (id_field.value or "").strip()
            conn = self.conexion.conectar()
            if conn is None:
                print("❌ No hay conexión")
                return
            try:
                cur = conn.cursor()
                if id_val != "":
                    cur.execute(
                        "INSERT INTO detalle_venta (id_detalle, id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)",
                        (int(id_val), id_venta.value, id_producto.value, cantidad.value, precio_unitario.value, subtotal.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        (id_venta.value, id_producto.value, cantidad.value, precio_unitario.value, subtotal.value)
                    )
                conn.commit()
                print(">> Detalle insertado correctamente")
                self._build_table_view()
                self.cargar_detalles()
            finally:
                self.conexion.cerrar(conn)

        self.content = ft.Container(
            expand=True,
            bgcolor=ft.Colors.GREY_100,
            alignment=ft.alignment.center,
            content=ft.Card(
                elevation=6,
                content=ft.Container(
                    width=520,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Text("Nuevo Detalle de Venta", size=22, weight=ft.FontWeight.BOLD),
                            id_field, id_venta, id_producto, cantidad, precio_unitario, subtotal,
                            ft.Row(
                                [
                                    ft.TextButton("Cancelar", on_click=lambda e: (self._build_table_view(), self.cargar_detalles())),
                                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar)
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

    def mostrar_formulario_editar_id(self, id_detalle):
        print(f">> mostrar_formulario_editar_id({id_detalle})")
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_venta, id_producto, cantidad, precio_unitario, subtotal FROM detalle_venta WHERE id_detalle = %s", (id_detalle,))
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        id_venta = ft.TextField(label="ID Venta", value=str(datos[0]))
        id_producto = ft.TextField(label="ID Producto", value=str(datos[1]))
        cantidad = ft.TextField(label="Cantidad", value=str(datos[2]))
        precio_unitario = ft.TextField(label="Precio unitario", value=str(datos[3]))
        subtotal = ft.TextField(label="Subtotal", value=str(datos[4]))

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE detalle_venta SET id_venta=%s, id_producto=%s, cantidad=%s, precio_unitario=%s, subtotal=%s WHERE id_detalle=%s",
                    (id_venta.value, id_producto.value, cantidad.value, precio_unitario.value, subtotal.value, id_detalle)
                )
                conn2.commit()
                print(">> Detalle actualizado correctamente")
                self._build_table_view()
                self.cargar_detalles()
            finally:
                self.conexion.cerrar(conn2)

        self.content = ft.Container(
            expand=True,
            bgcolor=ft.Colors.GREY_100,
            alignment=ft.alignment.center,
            content=ft.Card(
                elevation=6,
                content=ft.Container(
                    width=520,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Text(f"Editar Detalle #{id_detalle}", size=22, weight=ft.FontWeight.BOLD),
                            id_venta, id_producto, cantidad, precio_unitario, subtotal,
                            ft.Row(
                                [
                                    ft.TextButton("Cancelar", on_click=lambda e: (self._build_table_view(), self.cargar_detalles())),
                                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar)
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

    # ========================================
    # ELIMINAR
    # ========================================

    def confirmar_eliminar_id(self, id_detalle):
        print(f">> confirmar_eliminar_id({id_detalle})")

        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM detalle_venta WHERE id_detalle = %s", (id_detalle,))
                conn.commit()
                print(">> Detalle eliminado correctamente")
                self._build_table_view()
                self.cargar_detalles()
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
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=64, color=ft.Colors.RED),
                            ft.Text("Confirmar eliminación", size=22, weight=ft.FontWeight.BOLD),
                            ft.Text(f"¿Eliminar detalle #{id_detalle}?", text_align=ft.TextAlign.CENTER),
                            ft.Row(
                                [
                                    ft.OutlinedButton("Cancelar", on_click=lambda e: (self._build_table_view(), self.cargar_detalles())),
                                    ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE, bgcolor=ft.Colors.RED, color="white", on_click=eliminar)
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