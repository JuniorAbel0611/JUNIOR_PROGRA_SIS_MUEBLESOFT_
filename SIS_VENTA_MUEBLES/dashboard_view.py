import flet as ft
from muebles.clientes_view import ClientesView
from muebles.productos_view import ProductosView
from muebles.proveedores_view import ProveedoresView
from muebles.usuarios_view import UsuariosView
from muebles.ventas_view import VentasView
from muebles.detalle_venta_view import DetalleVentaView
from muebles.categorias_view import CategoriasView
from muebles.compras_view import ComprasView
from muebles.detalle_compra_view import DetalleCompraView
import tema

class DashboardView(ft.Container):
    """
    Dashboard renovado: topbar + sidebar + área principal de tarjetas.
    Solo UI: mantiene la lógica de navegación intacta.

    Ahora respeta el rol del usuario para decidir qué tablas mostrar.
    Tema oscuro y diseño responsivo.
    """
    def __init__(self, page, cambiar_vista, user=None, on_logout=None):
        super().__init__(expand=True, bgcolor=tema.COLOR_FONDO)
        print("[DEBUG] cargando muebles.dashboard_view.DashboardView")
        self.page = page
        self.cambiar_vista = cambiar_vista
        self.user = user or {}
        self.rol = (self.user.get("rol") or "").lower()
        self.on_logout = on_logout

        # Tabla metadata (todas las tablas posibles)
        self.tables = [
            ("Clientes", "Gestionar clientes", ft.Icons.PERSON),
            ("Productos", "Gestionar productos", ft.Icons.INVENTORY_2),
            ("Proveedores", "Gestionar proveedores", ft.Icons.LOCAL_SHIPPING),
            ("Usuarios", "Gestionar usuarios", ft.Icons.SUPERVISOR_ACCOUNT),
            ("Ventas", "Gestionar ventas", ft.Icons.PAYMENT),
            ("Detalle Venta", "Detalle de ventas", ft.Icons.RECEIPT_LONG),
            ("Categorías", "Gestionar categorías", ft.Icons.LABEL),
            ("Compras", "Gestionar compras", ft.Icons.SHOPPING_CART),
            ("Detalle Compra", "Detalle de compras", ft.Icons.INVENTORY),
        ]

        # Regla centralizada de visibilidad por rol (fácil de mantener)
        self.allowed_tables_by_role = {
            # Admin ve todo
            "admin": {t[0] for t in self.tables},
            # Vendedor solo ve lo necesario para su trabajo
            "vendedor": {
                "Clientes",
                "Productos",
                "Ventas",
                "Detalle Venta",
            },
        }
        # Si el rol no está configurado, se comporta como admin (compatibilidad)
        self.allowed_tables = self._get_allowed_tables_for_role()

        # Logo en sidebar
        try:
            logo_img = ft.Image(
                src="assets/logo.png",
                width=50,
                height=50,
                fit=ft.ImageFit.CONTAIN,
                error_content=ft.Icon(ft.Icons.CHAIR, size=40, color=tema.COLOR_PRIMARY)
            )
        except:
            logo_img = ft.Icon(ft.Icons.CHAIR, size=40, color=tema.COLOR_PRIMARY)

        # Sidebar (simple)
        menu_items = []
        for name, _, icon in self.allowed_tables:
            btn = ft.TextButton(
                name,
                icon=icon,
                on_click=lambda e, n=name: self.mostrar_tabla(n),
                style=ft.ButtonStyle(
                    color=tema.COLOR_ON_SURFACE,
                    overlay_color={"": tema.COLOR_SURFACE_VARIANT}
                ),
            )
            menu_items.append(btn)

        # Botón cerrar sesión
        btn_logout = ft.ElevatedButton(
            "Cerrar Sesión",
            icon=ft.Icons.LOGOUT,
            on_click=self._cerrar_sesion,
            **tema.estilo_boton_secundario(),
            width=200
        )

        sidebar = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [logo_img, tema.texto_titulo("Sistema", 16)],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    tema.crear_divider(),
                    ft.Container(
                        content=ft.Column(menu_items, spacing=4, scroll=ft.ScrollMode.AUTO),
                        expand=True
                    ),
                    tema.crear_divider(),
                    ft.Container(
                        content=btn_logout,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=10)
                    )
                ],
                spacing=8,
                expand=True
            ),
            width=240,
            padding=ft.padding.all(12),
            bgcolor=tema.COLOR_SURFACE,
            border=ft.border.all(1, tema.COLOR_BORDER)
        )

        # Topbar
        self.search = ft.TextField(
            hint_text="Buscar tabla...",
            width=420,
            on_change=self._on_search_change,
            **tema.estilo_textfield()
        )
        avatar = ft.CircleAvatar(
            content=ft.Text(
                (self.user.get("usuario") or "U")[:1].upper(),
                color=tema.COLOR_ON_PRIMARY
            ),
            radius=18,
            bgcolor=tema.COLOR_PRIMARY
        )
        topbar = ft.Container(
            content=ft.Row(
                [
                    ft.Container(self.search, expand=True),
                    ft.Container(
                        content=tema.texto_cuerpo(
                            f"Usuario: {self.user.get('usuario', 'N/A')}",
                            12
                        ),
                        padding=ft.padding.symmetric(horizontal=10)
                    ),
                    avatar
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=18),
            bgcolor=tema.COLOR_SURFACE,
            border=ft.border.all(1, tema.COLOR_BORDER)
        )

        # Main area with cards
        self.cards_column = ft.Column([], spacing=12, expand=True, scroll=ft.ScrollMode.AUTO)
        header = ft.Container(
            tema.texto_titulo("Tablas disponibles", 18),
            padding=ft.padding.only(left=8, top=8),
        )
        main_cards = ft.Container(
            ft.Column([header, self.cards_column], spacing=12, expand=True),
            padding=ft.padding.all(12),
            expand=True,
        )

        # Layout: sidebar + content (content: topbar + main_cards) - RESPONSIVO
        content_area = ft.Column([topbar, main_cards], spacing=12, expand=True)
        
        # Layout responsivo: en pantallas pequeñas el sidebar se coloca arriba
        body = ft.ResponsiveRow(
            [
                ft.Container(
                    content=sidebar,
                    col={"xs": 12, "sm": 12, "md": 3, "lg": 3, "xl": 2},
                    padding=ft.padding.only(right=12)
                ),
                ft.Container(
                    content=content_area,
                    col={"xs": 12, "sm": 12, "md": 9, "lg": 9, "xl": 10},
                    expand=True,
                    padding=ft.padding.all(12)
                )
            ],
            spacing=12,
            expand=True
        )

        self.content = body
        self._rebuild_cards("")

    def _get_allowed_tables_for_role(self):
        """
        Devuelve la lista de tablas visibles según el rol.
        """
        if self.rol in self.allowed_tables_by_role:
            allowed_names = self.allowed_tables_by_role[self.rol]
        else:
            # Rol desconocido o vacío -> se comporta como admin
            allowed_names = self.allowed_tables_by_role["admin"]

        return [t for t in self.tables if t[0] in allowed_names]

    def _rebuild_cards(self, q):
        q = (q or "").strip().lower()
        filtered = [
            t
            for t in self.allowed_tables
            if q == "" or q in t[0].lower() or q in t[1].lower()
        ]

        # Usar ResponsiveRow para mejor adaptación
        cards_list = []
        for name, desc, icon in filtered:
            icon_box = ft.Container(
                ft.Icon(icon, size=28, color=tema.COLOR_PRIMARY),
                width=56,
                height=56,
                padding=ft.padding.all(10),
                bgcolor=tema.COLOR_SURFACE_VARIANT,
                border=ft.border.all(1, tema.COLOR_BORDER),
                border_radius=8
            )
            mid = ft.Column(
                [tema.texto_cuerpo(desc, 12)],
                alignment=ft.MainAxisAlignment.START
            )
            btn_abrir = ft.ElevatedButton(
                "Abrir",
                on_click=lambda e, n=name: self.mostrar_tabla(n),
                **tema.estilo_boton_primario()
            )
            right = ft.Column(
                [
                    tema.texto_titulo(name, 16),
                    ft.Container(btn_abrir, alignment=ft.alignment.center_right)
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.END
            )
            inner = ft.Row(
                [
                    icon_box,
                    ft.Container(width=12),
                    mid,
                    ft.Container(expand=True),
                    right
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            card = ft.Container(
                content=inner,
                padding=ft.padding.symmetric(vertical=18, horizontal=18),
                **tema.estilo_card()
            )
            cards_list.append(
                ft.Container(
                    content=card,
                    col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6},
                    padding=ft.padding.all(6)
                )
            )

        self.cards_column.controls = [
            ft.ResponsiveRow(cards_list, spacing=12, expand=True)
        ]
        try:
            self.page.update()
        except Exception:
            pass

    def _on_search_change(self, e):
        q = (self.search.value or "").strip().lower()
        self._rebuild_cards(q)

    def _cerrar_sesion(self, e):
        """Cierra la sesión y vuelve al login"""
        if self.on_logout:
            self.on_logout()
        else:
            print("[WARNING] on_logout callback no definido")

    def _usuario_puede_ver_tabla(self, nombre_tabla: str) -> bool:
        """
        Verificación centralizada de permiso visual a nivel de dashboard.
        No toca la lógica CRUD, solo controla el acceso a las vistas.
        """
        return any(t[0] == nombre_tabla for t in self.allowed_tables)

    def mostrar_tabla(self, nombre_tabla):
        """
        Mantiene el mapeo a las vistas existentes sin tocar la lógica CRUD.
        Respeta el rol del usuario para decidir qué vistas puede abrir.
        """
        if not self._usuario_puede_ver_tabla(nombre_tabla):
            # Protección mínima por si alguien intenta abrir una vista oculta
            try:
                self.page.snack_bar = ft.SnackBar(
                    content=tema.texto_cuerpo("No tienes permisos para acceder a esta sección."),
                    bgcolor=tema.COLOR_ERROR,
                    open=True,
                )
                self.page.update()
            except Exception:
                pass
            return

        def volver_dashboard():
            # Siempre regresamos al dashboard con el mismo usuario (rol persistente)
            self.cambiar_vista(DashboardView(self.page, self.cambiar_vista, user=self.user, on_logout=self.on_logout))

        if nombre_tabla == "Clientes":
            self.cambiar_vista(
                ClientesView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Productos":
            self.cambiar_vista(
                ProductosView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Proveedores":
            self.cambiar_vista(
                ProveedoresView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Usuarios":
            self.cambiar_vista(
                UsuariosView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Ventas":
            self.cambiar_vista(
                VentasView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Detalle Venta":
            self.cambiar_vista(
                DetalleVentaView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Categorías":
            self.cambiar_vista(
                CategoriasView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Compras":
            self.cambiar_vista(
                ComprasView(self.page, volver_atras=volver_dashboard)
            )
        elif nombre_tabla == "Detalle Compra":
            self.cambiar_vista(
                DetalleCompraView(self.page, volver_atras=volver_dashboard)
            )
        else:
            try:
                self.page.snack_bar = ft.SnackBar(
                    content=tema.texto_cuerpo(f"Vista '{nombre_tabla}' no implementada"),
                    bgcolor=tema.COLOR_ERROR,
                    open=True,
                )
                self.page.update()
            except Exception:
                pass