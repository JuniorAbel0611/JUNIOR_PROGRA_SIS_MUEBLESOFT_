import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector
import tema


class VentasView(ft.Container):
    def __init__(self, page, volver_atras):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)
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
            bgcolor=tema.COLOR_PRIMARY,
            on_click=self.mostrar_formulario_agregar
        )

        self.header = ft.Container(
            **tema.estilo_container_header(),
            content=ft.Row(
                [
                    tema.texto_titulo("💳 Gestión de Ventas", 24),
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
                    bgcolor=tema.COLOR_FONDO,
                    content=ft.Column(
                        [
                            self.header,
                            self.lista_ventas
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
                    **tema.estilo_card(),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    tema.texto_titulo(f"Venta #{id_v}", 18),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=tema.COLOR_PRIMARY,
                                                tooltip="Editar",
                                                on_click=lambda e, _id=id_v: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=tema.COLOR_ERROR,
                                                tooltip="Eliminar",
                                                on_click=lambda e, _id=id_v: self.confirmar_eliminar_id(_id)
                                            ),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            tema.crear_divider(),
                            tema.texto_cuerpo(f"Cliente ID: {f[1] if f[1] is not None else ''}", 14),
                            tema.texto_cuerpo(f"Usuario ID: {f[2] if f[2] is not None else ''}", 14),
                            tema.texto_cuerpo(f"Fecha: {f[3] if f[3] is not None else ''}", 14),
                            tema.texto_titulo(f"Total: S/ {f[4] if f[4] is not None else ''}", 16),
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

        id_field = ft.TextField(label="ID (opcional)", **tema.estilo_textfield())
        id_cliente = ft.TextField(label="ID Cliente", **tema.estilo_textfield())
        id_usuario = ft.TextField(label="ID Usuario", **tema.estilo_textfield())
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)", **tema.estilo_textfield())
        total = ft.TextField(label="Total", **tema.estilo_textfield())

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

        id_cliente = ft.TextField(label="ID Cliente", value=str(datos[0]) if datos[0] else "", **tema.estilo_textfield())
        id_usuario = ft.TextField(label="ID Usuario", value=str(datos[1]) if datos[1] else "", **tema.estilo_textfield())
        fecha = ft.TextField(label="Fecha (YYYY-MM-DD HH:MM:SS)", value=str(datos[2]) if datos[2] else "", **tema.estilo_textfield())
        total = ft.TextField(label="Total", value=str(datos[3]) if datos[3] else "", **tema.estilo_textfield())

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
                        tema.texto_cuerpo(f"¿Eliminar venta ID {id_venta}?", 14),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_ventas()),
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
    # FORMULARIO BASE (REUTILIZABLE)
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
                                    on_click=lambda e: (self._build_table_view(), self.cargar_ventas()),
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