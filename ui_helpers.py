"""
ui_helpers.py  –  Funciones auxiliares de interfaz de usuario
-------------------------------------------------------------
Contiene widgets y componentes reutilizables que usan varios
tabs de MainApp.  Al estar aquí y no en vistas.py se evita
duplicar código y es más fácil hacer cambios de estilo globales.

Librerías usadas:
  - tkinter (stdlib): widgets base  tk.Frame, tk.Label
  - tkinter.ttk      : Treeview (tabla con scroll), Scrollbar
"""

import tkinter as tk
from tkinter import ttk
from config import C


# ─────────────────────────────────────────────────────────────
#  make_treeview
#  Crea un Treeview con scrollbar vertical dentro de un Frame.
# ─────────────────────────────────────────────────────────────
def make_treeview(parent, columns: tuple, col_widths: tuple,
                  col_anchors: tuple = None, height: int = 12):
    """
    Construye un ttk.Treeview estilizado con scrollbar.

    Parámetros:
      parent      : widget padre tkinter
      columns     : tupla de nombres de columnas, p.ej. ("Fecha","Monto")
      col_widths  : tupla de anchos en píxeles por columna
      col_anchors : alineación por columna ("w"=izquierda, "e"=derecha,
                    "center"=centrado).  Si es None, usa "w" para todas.
      height      : número de filas visibles sin hacer scroll

    Retorna:
      (frame_contenedor, tree)
      El frame debe empaquetarse en el padre con .pack() o .grid()
    """
    frame = tk.Frame(parent, bg=C["surface2"], bd=0)

    # Scrollbar vertical enlazada al Treeview
    vsb = ttk.Scrollbar(frame, orient="vertical")
    vsb.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",        # oculta la columna fantasma #0
        height=height,
        yscrollcommand=vsb.set,
    )
    vsb.config(command=tree.yview)

    # Configurar encabezados y columnas
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        anchor = col_anchors[i] if col_anchors else "w"
        tree.column(col, width=col_widths[i], anchor=anchor, stretch=False)

    tree.pack(fill=tk.BOTH, expand=True)
    return frame, tree


# ─────────────────────────────────────────────────────────────
#  separator
#  Línea horizontal decorativa de 1 px.
# ─────────────────────────────────────────────────────────────
def separator(parent, color: str = None):
    """
    Inserta una línea separadora de 1px en el widget padre.

    Parámetro:
      color : color hexadecimal opcional; usa C["border"] por defecto
    """
    tk.Frame(parent, bg=color or C["border"], height=1).pack(
        fill=tk.X, padx=10, pady=4
    )


# ─────────────────────────────────────────────────────────────
#  section_title
#  Etiqueta de sección con línea decorativa a la derecha.
# ─────────────────────────────────────────────────────────────
def section_title(parent, text: str):
    """
    Crea un encabezado de sección con texto en acento y una línea
    que se extiende hasta el borde derecho del contenedor.

    Ejemplo visual:
      ACTIVO CORRIENTE ─────────────────────────────────────────
    """
    f = tk.Frame(parent, bg=C["surface"])
    tk.Label(
        f, text=text.upper(),
        bg=C["surface"], fg=C["accent"],
        font=("Consolas", 9, "bold"),
    ).pack(side=tk.LEFT, padx=20, pady=(14, 4))
    # Línea que crece hasta llenar el espacio restante
    tk.Frame(f, bg=C["accent"], height=1).pack(
        side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20), pady=(14, 4)
    )
    f.pack(fill=tk.X)


# ─────────────────────────────────────────────────────────────
#  card_frame
#  Tarjeta con encabezado oscuro y cuerpo de contenido.
# ─────────────────────────────────────────────────────────────
def card_frame(parent, title: str, icon: str = "",
               pady: int = 0, expand: bool = True):
    """
    Crea un widget de tarjeta compuesto por:
      - outer : Frame exterior con borde sutil
      - hdr   : barra de encabezado de 38 px con el título
      - body  : área de contenido donde se agregan los widgets hijos

    Parámetros:
      title  : texto del encabezado
      icon   : emoji opcional que se antepone al título
      expand : si el body debe expandirse para llenar el espacio

    Retorna:
      (outer, body)  → empaquetar outer; agregar widgets a body
    """
    outer = tk.Frame(
        parent, bg=C["surface"], bd=0,
        highlightbackground=C["border"], highlightthickness=1,
    )
    # Encabezado de altura fija
    hdr = tk.Frame(outer, bg=C["surface2"], height=38)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)   # evita que los hijos alteren la altura
    tk.Label(
        hdr,
        text=f"{icon}  {title}" if icon else title,
        bg=C["surface2"], fg=C["text"],
        font=("Segoe UI", 10, "bold"), padx=14,
    ).pack(side=tk.LEFT, pady=6)

    # Cuerpo del contenido
    body = tk.Frame(outer, bg=C["surface"])
    body.pack(fill=tk.BOTH, expand=expand, padx=0, pady=0)

    return outer, body
