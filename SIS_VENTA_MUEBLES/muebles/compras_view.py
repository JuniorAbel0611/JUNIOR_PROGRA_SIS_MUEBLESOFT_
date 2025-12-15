import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector


class ComprasView(ft.Container):
    """
    LÓGICA ORIGINAL INTACTA
    DISEÑO NUEVO
    """

    def __init__(self, page, volver_atras):
        super().__init__(expand=True)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        # =========================
        # COMPONENTES BASE
        # =========================
        self.lista_compras = ft.Column(
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
                        "🧾 Compras",
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
        self.cargar_compras()

    # =====================================================
    # VISTA PRINCIPAL (UI)
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
                            self.lista_compras
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
    # CRUD — LÓGICA ORIGINAL
    # =====================================================

    def cargar_compras(self):
        print(">> cargar_compras() llamado")
        self.lista_compras.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                print("❌ No hay conexión")
                return

            cur = conn.cursor()
            cur.execute(
                "SELECT id_compra, id_proveedor, id_usuario, fecha_compra, total FROM compras"
            )
            filas = cur.fetchall()

            for r in filas:
                id_c = r[0]

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
                                            ft.Text(
                                                f"Compra #{r[0]}",
                                                size=18,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Text(
                                                f"Fecha: {r[3] or ''}",
                                                size=12,
                                                color=ft.Colors.GREY_600
                                            ),
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
                                    ft.Text(f"Proveedor ID: {r[1]}", weight=ft.FontWeight.W_500),
                                    ft.Text(f"Usuario ID: {r[2]}", weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        f"Total: ${r[4]}",
                                        color=ft.Colors.GREEN_700,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        spacing=10
                    )
                )

                self.lista_compras.controls.append(card)

            print(f">> {len(filas)} compras añadidas")

        except Exception as ex:
            print(f"❌ Error al cargar compras: {ex}")
        finally:
            self.conexion.cerrar(conn)

        try:
            self.page.update()
        except Exception:
            pass

    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        print(">> mostrar_formulario_agregar() compras")
        id_field = ft.TextField(label="ID (opcional)")
        id_proveedor = ft.TextField(label="ID Proveedor")
        id_usuario = ft.TextField(label="ID Usuario")
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)")
        total = ft.TextField(label="Total")

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
                        "INSERT INTO compras (id_compra, id_proveedor, id_usuario, fecha_compra, total) VALUES (%s, %s, %s, %s, %s)",
                        (int(id_val), id_proveedor.value, id_usuario.value, fecha.value, total.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO compras (id_proveedor, id_usuario, fecha_compra, total) VALUES (%s, %s, %s, %s)",
                        (id_proveedor.value, id_usuario.value, fecha.value, total.value)
                    )
                conn.commit()
                print(">> Compra insertada correctamente")
                self._build_table_view()
                self.cargar_compras()
            except mysql.connector.IntegrityError as ie:
                print(f"❌ Integridad DB: {ie}")
            except Exception as ex:
                print(f"❌ Error al agregar compra: {ex}")
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
                            ft.Text("Nueva Compra", size=22, weight=ft.FontWeight.BOLD),
                            id_field,
                            id_proveedor,
                            id_usuario,
                            fecha,
                            total,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_compras())
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

    def mostrar_formulario_editar_id(self, id_compra):
        print(f">> mostrar_formulario_editar_id({id_compra})")
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_proveedor, id_usuario, fecha_compra, total FROM compras WHERE id_compra = %s",
                (id_compra,)
            )
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        id_proveedor = ft.TextField(label="ID Proveedor", value=str(datos[0]))
        id_usuario = ft.TextField(label="ID Usuario", value=str(datos[1]))
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)", value=str(datos[2]))
        total = ft.TextField(label="Total", value=str(datos[3]))

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE compras SET id_proveedor=%s, id_usuario=%s, fecha_compra=%s, total=%s WHERE id_compra=%s",
                    (id_proveedor.value, id_usuario.value, fecha.value, total.value, id_compra)
                )
                conn2.commit()
                print(">> Compra actualizada correctamente")
                self._build_table_view()
                self.cargar_compras()
            except Exception as ex:
                print(f"❌ Error al editar compra: {ex}")
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
                            ft.Text(f"Editar Compra #{id_compra}", size=22, weight=ft.FontWeight.BOLD),
                            id_proveedor,
                            id_usuario,
                            fecha,
                            total,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_compras())
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

    def confirmar_eliminar_id(self, id_compra):
        print(f">> confirmar_eliminar_id({id_compra})")

        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM compras WHERE id_compra = %s",
                    (id_compra,)
                )
                conn.commit()
                print(">> Compra eliminada correctamente")
                self._build_table_view()
                self.cargar_compras()
            except Exception as ex:
                print(f"❌ Error al eliminar compra: {ex}")
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
                                f"¿Eliminar compra #{id_compra}?",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_compras())
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