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

class DashboardView(ft.Container):
    """
    Dashboard renovado: topbar + sidebar + área principal de tarjetas.
    Solo UI: mantiene la lógica de navegación intacta.
    """
    def __init__(self, page, cambiar_vista, user=None):
        super().__init__(expand=True, bgcolor="#F6F7FB")
        print("[DEBUG] cargando muebles.dashboard_view.DashboardView")
        self.page = page
        self.cambiar_vista = cambiar_vista
        self.user = user or {}

        # Tabla metadata
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

        # Sidebar (simple)
        menu_items = []
        for name, _, icon in self.tables:
            btn = ft.TextButton(name, icon=icon, on_click=lambda e, n=name: self.mostrar_tabla(n), style=ft.ButtonStyle())
            menu_items.append(btn)

        sidebar = ft.Container(
            content=ft.Column(
                [
                    ft.Row([ft.Icon(ft.Icons.CHAIR, size=28, color="#6A1B9A"), ft.Text("Sistema de Venta de Muebles", weight=ft.FontWeight.BOLD)], spacing=10),
                    ft.Divider(),
                    *menu_items
                ],
                spacing=8
            ),
            width=240,
            padding=ft.padding.all(12),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#ECEFF1")
        )

        # Topbar
        self.search = ft.TextField(hint_text="Buscar tabla...", width=420, on_change=self._on_search_change)
        avatar = ft.CircleAvatar(content=ft.Text((self.user.get("usuario") or "U")[:1].upper()), radius=18)
        topbar = ft.Container(
            content=ft.Row([ft.Container(self.search), ft.Container(expand=True), avatar]),
            padding=ft.padding.symmetric(vertical=12, horizontal=18),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#ECEFF1")
        )

        # Main area with cards
        self.cards_column = ft.Column([], spacing=12, expand=True)
        header = ft.Container(ft.Text("Tablas disponibles", size=14, weight=ft.FontWeight.BOLD), padding=ft.padding.only(left=8, top=8))
        main_cards = ft.Container(ft.Column([header, self.cards_column]), padding=ft.padding.all(12), expand=True)

        # Layout: sidebar + content (content: topbar + main_cards)
        content_area = ft.Column([topbar, main_cards], spacing=12, expand=True)
        body = ft.Row([sidebar, ft.Container(content_area, expand=True, padding=ft.padding.all(12))], spacing=12, expand=True)

        self.content = body
        self._rebuild_cards("")

    def _rebuild_cards(self, q):
        q = (q or "").strip().lower()
        filtered = [t for t in self.tables if q == "" or q in t[0].lower() or q in t[1].lower()]

        rows = []
        i = 0
        while i < len(filtered):
            pair = filtered[i:i+2]
            row_cells = []
            for name, desc, icon in pair:
                icon_box = ft.Container(ft.Icon(icon, size=28, color="#37474F"), width=56, height=56, padding=ft.padding.all(10), bgcolor="#FFFFFF", border=ft.border.all(1, "#ECEFF1"), border_radius=8)
                mid = ft.Column([ft.Text(desc, size=12, color="#616161")], alignment=ft.MainAxisAlignment.START)
                right = ft.Column([ft.Text(name, weight=ft.FontWeight.BOLD, size=14), ft.Container(ft.ElevatedButton("Abrir", on_click=lambda e, n=name: self.mostrar_tabla(n), bgcolor="#FFFFFF", color="#6A1B9A"), alignment=ft.alignment.center_right)], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.END)
                inner = ft.Row([icon_box, ft.Container(width=12), mid, ft.Container(expand=True), right], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                card = ft.Container(content=inner, padding=ft.padding.symmetric(vertical=18, horizontal=18), bgcolor="#FFFFFF", border=ft.border.all(1, "#F0F2F5"), border_radius=10)
                row_cells.append(ft.Container(card, expand=True))
            if len(row_cells) == 1:
                row_cells.append(ft.Container(expand=True))
            rows.append(ft.Row(row_cells, spacing=12))
            i += 2

        self.cards_column.controls = rows
        try:
            self.page.update()
        except Exception:
            pass

    def _on_search_change(self, e):
        q = (self.search.value or "").strip().lower()
        self._rebuild_cards(q)

    def mostrar_tabla(self, nombre_tabla):
        """
        Mantiene el mapeo a las vistas existentes sin tocar la lógica CRUD.
        """
        if nombre_tabla == "Clientes":
            self.cambiar_vista(ClientesView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Productos":
            self.cambiar_vista(ProductosView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Proveedores":
            self.cambiar_vista(ProveedoresView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Usuarios":
            self.cambiar_vista(UsuariosView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Ventas":
            self.cambiar_vista(VentasView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Detalle Venta":
            self.cambiar_vista(DetalleVentaView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Categorías":
            self.cambiar_vista(CategoriasView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Compras":
            self.cambiar_vista(ComprasView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        elif nombre_tabla == "Detalle Compra":
            self.cambiar_vista(DetalleCompraView(self.page, volver_atras=lambda: self.cambiar_vista(DashboardView(self.page, self.cambiar_vista))))
        else:
            try:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Vista '{nombre_tabla}' no implementada"), open=True)
                self.page.update()
            except Exception:
                pass