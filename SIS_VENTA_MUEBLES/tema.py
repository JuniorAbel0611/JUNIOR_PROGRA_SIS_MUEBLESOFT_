"""
Módulo centralizado de tema oscuro para el sistema.
Define colores, estilos y componentes reutilizables.
"""
import flet as ft

# ==================== COLORES TEMA OSCURO ====================
COLOR_FONDO = "#121212"
COLOR_SURFACE = "#1E1E1E"
COLOR_SURFACE_VARIANT = "#2C2C2C"
COLOR_PRIMARY = "#BB86FC"
COLOR_PRIMARY_VARIANT = "#9D6DE8"
COLOR_SECONDARY = "#03DAC6"
COLOR_ERROR = "#CF6679"
COLOR_ON_PRIMARY = "#000000"
COLOR_ON_SURFACE = "#FFFFFF"
COLOR_ON_BACKGROUND = "#E0E0E0"
COLOR_DISABLED = "#424242"
COLOR_DIVIDER = "#3A3A3A"
COLOR_BORDER = "#2C2C2C"

# ==================== ESTILOS DE COMPONENTES ====================

def estilo_textfield():
    """Estilo para TextField en tema oscuro"""
    return {
        "bgcolor": COLOR_SURFACE_VARIANT,
        "color": COLOR_ON_SURFACE,
        "border_color": COLOR_BORDER,
        "focused_border_color": COLOR_PRIMARY,
        "cursor_color": COLOR_PRIMARY,
    }

def estilo_boton_primario():
    """Estilo para botones primarios"""
    return {
        "bgcolor": COLOR_PRIMARY,
        "color": COLOR_ON_PRIMARY,
        "elevation": 2,
    }

def estilo_boton_secundario():
    """Estilo para botones secundarios"""
    return {
        "bgcolor": COLOR_SURFACE_VARIANT,
        "color": COLOR_ON_SURFACE,
        "elevation": 1,
    }

def estilo_card():
    """Estilo base para cards (SIN padding)"""
    return {
        "bgcolor": COLOR_SURFACE,
        "border_radius": 12,
        "border": ft.border.all(1, COLOR_BORDER),
    }

def estilo_container_header():
    """Estilo base para headers (SIN padding)"""
    return {
        "bgcolor": COLOR_SURFACE,
        "border_radius": 12,
        "border": ft.border.all(1, COLOR_BORDER),
    }

# ==================== FUNCIONES AUXILIARES ====================

def texto_titulo(texto: str, size: int = 24):
    return ft.Text(
        texto,
        size=size,
        weight=ft.FontWeight.BOLD,
        color=COLOR_ON_SURFACE,
    )

def texto_subtitulo(texto: str, size: int = 16):
    return ft.Text(
        texto,
        size=size,
        color=COLOR_ON_BACKGROUND,
    )

def texto_cuerpo(texto: str, size: int = 14):
    return ft.Text(
        texto,
        size=size,
        color=COLOR_ON_BACKGROUND,
    )

def crear_divider():
    return ft.Divider(color=COLOR_DIVIDER, height=1)
