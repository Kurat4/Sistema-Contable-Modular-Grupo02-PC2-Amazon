"""
config.py  –  Constantes globales del Sistema Contable
-------------------------------------------------------
Contiene la paleta de colores C que usan todos los
demás módulos.  Es el único lugar donde se definen
los valores de diseño; cambiar aquí afecta a toda
la aplicación.

Librería usada: ninguna (solo tipos nativos de Python)
"""

# ─────────────────────────────────────────────────────
#  PALETA DE COLORES  (tema oscuro profesional)
#  Tipo de dato: dict[str, str]  →  nombre : hex color
# ─────────────────────────────────────────────────────
C = {
    # Fondos principales
    "bg":          "#0D1117",   # fondo raíz de la ventana
    "surface":     "#1E2530",   # superficie de tarjetas
    "surface2":    "#29303D",   # superficie secundaria
    "surface3":    "#3A424F",   # superficie terciaria / hover
    "border":      "#3A424F",   # color de bordes

    # Color de acento (verde-azulado)
    "accent":      "#22D3A4",
    "accent_dark": "#16A88A",   # versión oscura para hover

    # Colores semánticos
    "blue":        "#58A6FF",   # débitos / debe
    "amber":       "#F0B429",   # créditos / haber
    "red":         "#F85149",   # errores / valores negativos
    "green":       "#22D3A4",   # confirmaciones

    # Texto
    "text":        "#E6EDF3",   # texto principal
    "text_dim":    "#A8B3BE",   # texto secundario
    "text_muted":  "#5C6572",   # texto desactivado / hints

    # Colores específicos para filas DEBE / HABER en tablas
    "debe_bg":     "#1A2332",
    "debe_fg":     "#58A6FF",
    "haber_bg":    "#2A1F0A",
    "haber_fg":    "#F0B429",

    # Fondos especiales de componentes
    "header_bg":   "#151C26",   # barra superior
    "main_bg":     "#1A2030",   # fondo del área de trabajo
}
