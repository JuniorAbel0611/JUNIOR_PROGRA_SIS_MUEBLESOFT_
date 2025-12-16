import flet as ft
from muebles.conexion import ConexionDB
import mysql.connector
import tema


class ProductosView(ft.Container):
    """
    MISMA LÓGICA
    NUEVO DISEÑO - TEMA OSCURO
    """

    def __init__(self, page, volver_atras):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)
        self.page = page
        self.volver_atras = volver_atras
        self.conexion = ConexionDB()

        self.tabla_db = "productos"
        self.title_text = "🛋️ Productos"

        self.columns = []
        self.pk_column = None

        # =========================
        # COMPONENTES BASE
        # =========================
        self.lista_productos = ft.Column(
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
                    tema.texto_titulo(self.title_text, 24),
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
        self._load_metadata()
        self.cargar_productos()

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
                            self.lista_productos
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
    # METADATA (LÓGICA ORIGINAL)
    # =====================================================

    def _load_metadata(self):
        conn = self.conexion.conectar()
        if conn is None:
            return
        try:
            cur = conn.cursor(dictionary=True)
            dbname = getattr(self.conexion, "database", None) or conn.database
            cur.execute(
                "SELECT COLUMN_NAME, DATA_TYPE, COLUMN_KEY, EXTRA "
                "FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s "
                "ORDER BY ORDINAL_POSITION",
                (dbname, self.tabla_db)
            )
            self.columns.clear()
            self.pk_column = None
            for c in cur.fetchall():
                item = {
                    "name": c["COLUMN_NAME"],
                    "type": c["DATA_TYPE"],
                    "is_pk": c["COLUMN_KEY"] == "PRI",
                    "extra": c["EXTRA"]
                }
                self.columns.append(item)
                if item["is_pk"] and self.pk_column is None:
                    self.pk_column = item["name"]
        finally:
            self.conexion.cerrar(conn)

    # =====================================================
    # LISTADO EN CARDS
    # =====================================================

    def cargar_productos(self):
        self.lista_productos.controls.clear()
        conn = self.conexion.conectar()
        try:
            if conn is None:
                return

            cur = conn.cursor()
            cols_sql = ", ".join([f"`{c['name']}`" for c in self.columns])
            cur.execute(f"SELECT {cols_sql} FROM `{self.tabla_db}`")
            filas = cur.fetchall()

            for row in filas:
                pk_val = row[0]

                detalles = []
                for i, c in enumerate(self.columns):
                    if c["is_pk"]:
                        continue
                    detalles.append(
                        tema.texto_cuerpo(f"{c['name'].replace('_',' ').capitalize()}: {row[i] or ''}", 14)
                    )

                card = ft.Container(
                    **tema.estilo_card(),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    tema.texto_titulo(f"ID: {pk_val}", 18),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_color=tema.COLOR_PRIMARY,
                                                on_click=lambda e, _id=pk_val: self.mostrar_formulario_editar_id(_id)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_color=tema.COLOR_ERROR,
                                                on_click=lambda e, _id=pk_val: self.confirmar_eliminar_id(_id)
                                            )
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            tema.crear_divider(),
                            *detalles
                        ],
                        spacing=8
                    )
                )

                self.lista_productos.controls.append(card)

        finally:
            self.conexion.cerrar(conn)

        try:
            self.page.update()
        except Exception:
            pass

    # =====================================================
    # FORMULARIOS (MISMA LÓGICA)
    # =====================================================

    def mostrar_formulario_agregar(self, e=None):
        id_field = None
        if self.pk_column:
            id_field = ft.TextField(label=f"{self.pk_column} (opcional)", **tema.estilo_textfield())

        fields = []
        for c in self.columns:
            if c["is_pk"]:
                continue
            tf = ft.TextField(label=c["name"].replace("_", " ").capitalize(), **tema.estilo_textfield())
            fields.append((c["name"], tf))

        def guardar(ev):
            id_val = (id_field.value or "").strip() if id_field else ""
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                if id_val:
                    cols = [self.pk_column] + [db for db, _ in fields]
                    sql = f"INSERT INTO `{self.tabla_db}` ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})"
                    params = (int(id_val),) + tuple(f.value for _, f in fields)
                else:
                    cols = [db for db, _ in fields]
                    sql = f"INSERT INTO `{self.tabla_db}` ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})"
                    params = tuple(f.value for _, f in fields)

                cur.execute(sql, params)
                conn.commit()
                self._build_table_view()
                self.cargar_productos()
            finally:
                self.conexion.cerrar(conn)

        self._mostrar_formulario(
            "Nuevo Producto",
            ([id_field] if id_field else []) + [f for _, f in fields],
            guardar
        )

    def mostrar_formulario_editar_id(self, pk_val):
        conn = self.conexion.conectar()
        try:
            cur = conn.cursor()
            cols = [c["name"] for c in self.columns]
            cur.execute(
                f"SELECT {','.join(cols)} FROM `{self.tabla_db}` WHERE `{self.pk_column}`=%s",
                (pk_val,)
            )
            fila = cur.fetchone()
        finally:
            self.conexion.cerrar(conn)

        fields = []
        for i, c in enumerate(self.columns):
            if c["is_pk"]:
                continue
            tf = ft.TextField(
                label=c["name"].replace("_", " ").capitalize(),
                value=str(fila[i] or ""),
                **tema.estilo_textfield()
            )
            fields.append((c["name"], tf))

        def guardar(ev):
            conn2 = self.conexion.conectar()
            try:
                cur2 = conn2.cursor()
                set_sql = ", ".join([f"`{db}`=%s" for db, _ in fields])
                sql = f"UPDATE `{self.tabla_db}` SET {set_sql} WHERE `{self.pk_column}`=%s"
                params = tuple(f.value for _, f in fields) + (pk_val,)
                cur2.execute(sql, params)
                conn2.commit()
                self._build_table_view()
                self.cargar_productos()
            finally:
                self.conexion.cerrar(conn2)

        self._mostrar_formulario(
            f"Editar Producto (ID {pk_val})",
            [f for _, f in fields],
            guardar
        )

    # =====================================================

    def confirmar_eliminar_id(self, pk_val):
        def eliminar(ev):
            conn = self.conexion.conectar()
            try:
                cur = conn.cursor()
                cur.execute(
                    f"DELETE FROM `{self.tabla_db}` WHERE `{self.pk_column}`=%s",
                    (pk_val,)
                )
                conn.commit()
                self._build_table_view()
                self.cargar_productos()
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
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=64, color=tema.COLOR_ERROR),
                        tema.texto_titulo("Confirmar eliminación", 22),
                        tema.texto_cuerpo(f"¿Eliminar producto ID {pk_val}?", 14),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Cancelar",
                                    on_click=lambda e: (self._build_table_view(), self.cargar_productos()),
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
                                    on_click=lambda e: (self._build_table_view(), self.cargar_productos()),
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