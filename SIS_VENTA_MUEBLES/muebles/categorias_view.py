import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector


class CategoriasView(ft.Container):
    """
    MISMA LÓGICA ORIGINAL
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
        self.lista_categorias = ft.Column(
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
                        "🏷️ Categorías",
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
        self.cargar_categorias()

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
                            self.lista_categorias
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

    def cargar_categorias(self):
        print(">> cargar_categorias() llamado")
        self.lista_categorias.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                print("❌ No hay conexión")
                return

            cur = conn.cursor()
            cur.execute(
                "SELECT id_categoria, nombre_categoria, descripcion FROM categorias"
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
                                                r[1] or "",
                                                size=18,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Text(
                                                f"ID: {r[0]}",
                                                size=11,
                                                color=ft.Colors.GREY_500
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
                            ft.Text(
                                r[2] or "",
                                color=ft.Colors.GREY_700
                            ),
                        ],
                        spacing=8
                    )
                )

                self.lista_categorias.controls.append(card)

            print(f">> {len(filas)} categorias añadidas")

        except Exception as ex:
            print(f"❌ Error al cargar categorias: {ex}")
        finally:
            self.conexion.cerrar(conn)

        try:
            self.page.update()
        except Exception:
            pass

    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        print(">> mostrar_formulario_agregar() categorias")
        id_field = ft.TextField(label="ID (opcional)")
        nombre = ft.TextField(label="Nombre")
        descripcion = ft.TextField(label="Descripción", multiline=True)

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
                        "INSERT INTO categorias (id_categoria, nombre_categoria, descripcion) VALUES (%s, %s, %s)",
                        (int(id_val), nombre.value, descripcion.value)
                    )
                else:
                    cur.execute(
                        "INSERT INTO categorias (nombre_categoria, descripcion) VALUES (%s, %s)",
                        (nombre.value, descripcion.value)
                    )
                conn.commit()
                print(">> Categoría insertada correctamente")
                self._build_table_view()
                self.cargar_categorias()
            except mysql.connector.IntegrityError as ie:
                print(f"❌ Integridad DB: {ie}")
            except Exception as ex:
                print(f"❌ Error al agregar categoría: {ex}")
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
                            ft.Text(
                                "Nueva Categoría",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            ),
                            id_field,
                            nombre,
                            descripcion,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_categorias())
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

    def mostrar_formulario_editar_id(self, id_categoria):
        print(f">> mostrar_formulario_editar_id({id_categoria})")
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT nombre_categoria, descripcion FROM categorias WHERE id_categoria = %s",
                (id_categoria,)
            )
            datos = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        nombre = ft.TextField(label="Nombre", value=datos[0])
        descripcion = ft.TextField(label="Descripción", value=datos[1], multiline=True)

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE categorias SET nombre_categoria=%s, descripcion=%s WHERE id_categoria=%s",
                    (nombre.value, descripcion.value, id_categoria)
                )
                conn2.commit()
                print(">> Categoría actualizada correctamente")
                self._build_table_view()
                self.cargar_categorias()
            except Exception as ex:
                print(f"❌ Error al editar categoría: {ex}")
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
                                f"Editar Categoría (ID {id_categoria})",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            ),
                            nombre,
                            descripcion,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_categorias())
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

    def confirmar_eliminar_id(self, id_categoria):
        print(f">> confirmar_eliminar_id({id_categoria})")

        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM categorias WHERE id_categoria = %s",
                    (id_categoria,)
                )
                conn.commit()
                print(">> Categoría eliminada correctamente")
                self._build_table_view()
                self.cargar_categorias()
            except Exception as ex:
                print(f"❌ Error al eliminar categoría: {ex}")
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
                                f"¿Eliminar categoría ID {id_categoria}?",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Cancelar",
                                        on_click=lambda e: (self._build_table_view(), self.cargar_categorias())
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