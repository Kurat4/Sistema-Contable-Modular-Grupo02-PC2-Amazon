"""
vistas.py  –  Interfaz de usuario principal (MainApp)
------------------------------------------------------
Contiene la clase MainApp (tk.Frame), que construye y gestiona
todos los tabs (pestañas) de la aplicación:

  Tab 0 – Registro          : formulario + calendario popup
  Tab 1 – Libro Diario      : Treeview con movimientos cronológicos
  Tab 2 – Libro Mayor       : movimientos filtrados por cuenta
  Tab 3 – Balance de Saldos : Treeview con saldos de todas las cuentas
  Tab 4 – Estado de Result. : cálculo de utilidad operativa
  Tab 5 – Situación Fin.    : balance general (activo = pasivo + patrimonio)
  Tab 6 – Plan de Cuentas   : catálogo PCGE con saldos actuales

Librerías usadas:
  - tkinter (stdlib) : ventanas, widgets, layout (pack/grid)
  - tkinter.ttk      : Notebook (pestañas), Combobox, Scrollbar, Style
  - datetime (stdlib): fecha actual para el entry y los reportes
  - re (stdlib)      : expresión regular para extraer el código de cuenta
  - calendar (stdlib): generar la grilla del calendario popup
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re
import calendar

from config import C
from modelo import SistemaContable
from ui_helpers import make_treeview, separator, section_title, card_frame


class MainApp(tk.Frame):
    """
    Vista principal de la aplicación.

    Hereda de tk.Frame para poder empaquetarse directamente
    dentro de la ventana raíz (tk.Tk) que gestiona App en main.py.

    Atributos de estado:
      self.sistema           : instancia de SistemaContable (el modelo)
      self.movimientos_actuales : lista de movimientos del asiento en curso
      self._selected_cod     : código de cuenta seleccionado en el combobox
      self._cal_year / _month: año/mes mostrado en el calendario popup
    """

    def __init__(self, parent, sistema: SistemaContable):
        super().__init__(parent, bg=C["main_bg"])
        self.sistema = sistema
        self.movimientos_actuales = []   # asiento pendiente de registrar
        self._selected_cod = None        # cuenta elegida en el combobox
        self._cal_year  = datetime.now().year
        self._cal_month = datetime.now().month
        self._build()

    # ──────────────────────────────────────────────────────────
    #  CONSTRUCCIÓN INICIAL
    # ──────────────────────────────────────────────────────────
    def _build(self):
        self.pack(fill=tk.BOTH, expand=True)
        self._apply_styles()    # estilos ttk globales
        self._build_topbar()    # barra superior con logo y estado
        self._build_notebook()  # pestañas

    # ──────────────────────────────────────────────────────────
    #  ESTILOS ttk
    #  ttk.Style permite personalizar widgets ttk (Treeview,
    #  Notebook, Combobox, Scrollbar) con colores del tema oscuro.
    # ──────────────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")   # base neutral para sobreescribir

        # ── Treeview (tablas) ──────────────────────────────
        style.configure("Treeview",
            background=C["surface2"], fieldbackground=C["surface2"],
            foreground=C["text_dim"], rowheight=26,
            font=("Consolas", 10), borderwidth=0, relief="flat",
        )
        style.configure("Treeview.Heading",
            background=C["surface3"], foreground=C["text"],
            font=("Consolas", 9, "bold"), relief="flat",
        )
        style.map("Treeview",
            background=[("selected", C["surface3"])],
            foreground=[("selected", C["accent"])],
        )

        # ── Notebook (pestañas) ────────────────────────────
        style.configure("Dark.TNotebook",
            background=C["main_bg"], borderwidth=0, tabmargins=0)
        style.configure("Dark.TNotebook.Tab",
            background=C["surface2"], foreground=C["text_dim"],
            font=("Segoe UI", 10), padding=(16, 8), borderwidth=0,
        )
        style.map("Dark.TNotebook.Tab",
            background=[("selected", C["surface"]), ("active", C["surface3"])],
            foreground=[("selected", C["accent"]), ("active", C["text"])],
        )

        # ── Scrollbar ─────────────────────────────────────
        style.configure("Vertical.TScrollbar",
            background=C["surface3"], troughcolor=C["surface2"],
            arrowcolor=C["text_muted"], borderwidth=0, relief="flat",
        )

        # ── Combobox de cuenta (con borde acento) ──────────
        style.configure("Cuenta.TCombobox",
            fieldbackground=C["surface2"], background=C["surface3"],
            foreground=C["text"], arrowcolor=C["accent"],
            selectbackground=C["surface3"], selectforeground=C["accent"],
            bordercolor=C["accent"], lightcolor=C["surface2"],
            darkcolor=C["surface2"], insertcolor=C["accent"], padding=(8, 6),
        )
        style.map("Cuenta.TCombobox",
            fieldbackground=[("readonly", C["surface2"]), ("focus", C["surface3"])],
            foreground=[("readonly", C["text"]), ("focus", C["accent"])],
            bordercolor=[("focus", C["accent"]), ("!focus", C["border"])],
        )

        # ── Combobox genérico (selector de transacción, etc.) ──
        style.configure("Dark.TCombobox",
            fieldbackground=C["surface2"], background=C["surface2"],
            foreground=C["text"], arrowcolor=C["text_dim"],
            selectbackground=C["surface3"], selectforeground=C["accent"],
            bordercolor=C["border"],
        )

    # ──────────────────────────────────────────────────────────
    #  BARRA SUPERIOR
    # ──────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["header_bg"],
                       highlightbackground=C["border"], highlightthickness=1)
        bar.pack(fill=tk.X)

        logo_f = tk.Frame(bar, bg=C["header_bg"])
        logo_f.pack(side=tk.LEFT, padx=16, pady=8)
        tk.Label(logo_f, text=" SC ", bg=C["accent"], fg=C["bg"],
                 font=("Georgia", 13, "bold"), padx=4, pady=2).pack(side=tk.LEFT)
        tk.Label(logo_f, text="  Sistema", bg=C["header_bg"],
                 fg=C["text"], font=("Georgia", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(logo_f, text="Contable", bg=C["header_bg"],
                 fg=C["accent"], font=("Georgia", 13, "bold")).pack(side=tk.LEFT)

        tk.Label(bar, text=datetime.now().strftime("%d/%m/%Y"),
                 bg=C["header_bg"], fg=C["text_muted"],
                 font=("Consolas", 9)).pack(side=tk.RIGHT)
        self.lbl_status = tk.Label(bar, text="● 0 transacciones",
                                   bg=C["header_bg"], fg=C["accent"],
                                   font=("Consolas", 9), padx=12)
        self.lbl_status.pack(side=tk.RIGHT, padx=10)

    # ──────────────────────────────────────────────────────────
    #  NOTEBOOK  (pestañas)
    # ──────────────────────────────────────────────────────────
    def _build_notebook(self):
        nb = ttk.Notebook(self, style="Dark.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        tabs = [
            ("  📝  Registro",             self._tab_registro),
            ("  📖  Libro Diario",          self._tab_diario),
            ("  📚  Libro Mayor",           self._tab_mayor),
            ("  📊  Balance",               self._tab_balance),
            ("  📈  Resultados",            self._tab_resultados),
            ("  🏦  Situación Financiera",  self._tab_situacion),
            ("  📋  Plan de Cuentas",       self._tab_plan),
        ]
        for title, builder in tabs:
            frame = tk.Frame(nb, bg=C["surface"])
            nb.add(frame, text=title)
            builder(frame)   # cada método construye el contenido del tab

        nb.bind("<<NotebookTabChanged>>", self._on_tab_change)
        self._nb = nb

    def _on_tab_change(self, event):
        """Refresca el tab activo cada vez que el usuario cambia de pestaña."""
        idx = self._nb.index("current")
        refreshers = {
            1: self._refresh_diario,
            2: self._refresh_mayor_combos,
            3: self._refresh_balance,
            4: self._refresh_resultados,
            5: self._refresh_situacion,
            6: self._refresh_plan,
        }
        if idx in refreshers:
            refreshers[idx]()

    # ──────────────────────────────────────────────────────────
    #  SELECTOR DE TRANSACCIÓN
    #  Barra común a Balance, ER, ESF, Diario, Mayor y Plan.
    #  Permite ver los datos de una transacción individual o el
    #  acumulado de todas.
    # ──────────────────────────────────────────────────────────
    def _build_tx_selector(self, parent, on_change):
        """
        Construye una barra con un Combobox que lista:
          - "Acumulado (todas las transacciones)"
          - "Tx 1: fecha  —  descripción"
          - "Tx 2: ..."  etc.

        Cuando el usuario elige una opción, llama on_change(idx)
        donde idx es None (acumulado) o el índice 0-based de la Tx.

        Retorna:
          (bar_frame, refresh_opts_fn, on_select_fn)
          refresh_opts_fn() : actualiza las opciones del combo
          on_select_fn()    : fuerza la re-lectura del combo actual
        """
        bar = tk.Frame(parent, bg=C["surface2"],
                       highlightbackground=C["border"], highlightthickness=1)
        bar.pack(fill=tk.X, padx=12, pady=(8, 0))

        tk.Label(bar, text="Ver datos de:",
                 bg=C["surface2"], fg=C["text_dim"],
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 6), pady=6)

        var = tk.StringVar(value="Acumulado (todas las transacciones)")
        combo = ttk.Combobox(bar, textvariable=var,
                             style="Dark.TCombobox",
                             font=("Consolas", 9), width=52,
                             state="readonly")
        combo.pack(side=tk.LEFT, padx=4, pady=6)

        lbl_info = tk.Label(bar, text="",
                            bg=C["surface2"], fg=C["text_muted"],
                            font=("Consolas", 8))
        lbl_info.pack(side=tk.LEFT, padx=10)

        def refresh_opts():
            opts = ["Acumulado (todas las transacciones)"]
            for i, t in enumerate(self.sistema.transacciones, 1):
                opts.append(f"Tx {i}: {t['fecha']}  —  {t['descripcion'][:50]}")
            combo["values"] = opts
            if var.get() not in opts:
                var.set(opts[0])
                on_change(None)

        def on_select(event=None):
            sel = var.get()
            if sel.startswith("Acumulado"):
                on_change(None)
                lbl_info.config(
                    text=f"  {len(self.sistema.transacciones)} transacciones")
            else:
                try:
                    idx = int(sel.split(":")[0].replace("Tx", "").strip()) - 1
                    on_change(idx)
                    t = self.sistema.transacciones[idx]
                    lbl_info.config(text=f"  {len(t['movimientos'])} movimientos")
                except Exception:
                    on_change(None)

        combo.bind("<<ComboboxSelected>>", on_select)
        return bar, refresh_opts, on_select

    def _saldos_activos(self, tx_idx):
        """
        Devuelve el dict de saldos según la selección del usuario:
          tx_idx = None  → saldos acumulados (self.sistema.saldos)
          tx_idx = 0,1,2 → saldos de esa sola transacción
        """
        if tx_idx is None:
            return self.sistema.saldos
        if 0 <= tx_idx < len(self.sistema.transacciones):
            return self.sistema._saldos_de(
                [self.sistema.transacciones[tx_idx]]
            )
        return self.sistema.saldos

    # ══════════════════════════════════════════════════════════
    #  TAB 0 – REGISTRO
    # ══════════════════════════════════════════════════════════
    def _tab_registro(self, parent):
        """
        Formulario de ingreso de transacciones.
        Usa PanedWindow (divisor arrastrable) para separar:
          - Panel izquierdo : selección de cuenta y monto
          - Panel derecho   : lista de movimientos del asiento en curso
        """
        pw = tk.PanedWindow(parent, orient=tk.HORIZONTAL,
                            bg=C["main_bg"], sashwidth=4, sashpad=0)
        pw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── Panel izquierdo ───────────────────────────────
        left = tk.Frame(pw, bg=C["main_bg"])
        pw.add(left, minsize=400)

        # Tarjeta: fecha
        c1, b1 = card_frame(left, "Datos de la Transacción", icon="📋")
        c1.pack(fill=tk.X, pady=(0, 10))

        row1 = tk.Frame(b1, bg=C["surface"])
        row1.pack(fill=tk.X, padx=14, pady=(12, 12))
        self._lbl(row1, "Fecha (YYYY-MM-DD)").pack(side=tk.LEFT)
        self.entry_fecha = self._entry(row1, width=13)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side=tk.LEFT, padx=(8, 4))

        # Botón calendario 📅
        cal_btn = tk.Button(
            row1, text="📅",
            bg=C["surface3"], fg=C["accent"],
            font=("Segoe UI", 11), relief="flat", bd=0,
            padx=7, pady=3, cursor="hand2",
            activebackground=C["surface2"],
            activeforeground=C["accent"],
            command=self._open_calendar,
        )
        cal_btn.pack(side=tk.LEFT)
        cal_btn.bind("<Enter>", lambda e: cal_btn.config(bg=C["accent"], fg=C["bg"]))
        cal_btn.bind("<Leave>", lambda e: cal_btn.config(bg=C["surface3"], fg=C["accent"]))

        # Tarjeta: agregar movimiento
        c2, b2 = card_frame(left, "Agregar Movimiento", icon="➕")
        c2.pack(fill=tk.X, pady=(0, 10))

        # Etiqueta del combobox
        cuenta_lbl_row = tk.Frame(b2, bg=C["surface"])
        cuenta_lbl_row.pack(fill=tk.X, padx=14, pady=(12, 2))
        tk.Label(cuenta_lbl_row, text="Cuenta Contable",
                 bg=C["surface"], fg=C["text_dim"],
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(cuenta_lbl_row, text="  (código o nombre)",
                 bg=C["surface"], fg=C["text_muted"],
                 font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Combobox de cuentas con borde acento
        combo_row = tk.Frame(b2, bg=C["surface"])
        combo_row.pack(fill=tk.X, padx=14, pady=(0, 10))
        combo_border = tk.Frame(combo_row, bg=C["accent"], padx=1, pady=1)
        combo_border.pack(side=tk.LEFT, fill=tk.X, expand=True)

        all_opts = [f"{cod}  –  {nom}"
                    for cat in self.sistema.planes.values()
                    for cod, nom in cat.items()]
        self.combo_cuenta = ttk.Combobox(
            combo_border, values=all_opts,
            style="Cuenta.TCombobox", font=("Consolas", 10), state="normal",
        )
        self.combo_cuenta.pack(fill=tk.X, expand=True)
        self.combo_cuenta.set("Seleccionar cuenta…")
        # Eventos del combobox: búsqueda por tecleo y selección
        self.combo_cuenta.bind("<KeyRelease>",         self._on_combo_key)
        self.combo_cuenta.bind("<<ComboboxSelected>>", self._on_combo_select)
        self.combo_cuenta.bind("<FocusIn>",
            lambda e: self.combo_cuenta.set("")
            if self.combo_cuenta.get() == "Seleccionar cuenta…" else None)
        self.combo_cuenta.bind("<FocusOut>", self._on_combo_focusout)

        # Etiqueta de confirmación de cuenta seleccionada
        self.lbl_cuenta_sel = tk.Label(
            b2, text="", bg=C["surface"], fg=C["accent"],
            font=("Consolas", 9), anchor="w")
        self.lbl_cuenta_sel.pack(fill=tk.X, padx=16, pady=(0, 6))

        # Fila: monto + tipo (aumento / disminución)
        mr2 = tk.Frame(b2, bg=C["surface"])
        mr2.pack(fill=tk.X, padx=14, pady=4)
        self._lbl(mr2, "Monto S/.").pack(side=tk.LEFT)
        self.entry_monto = self._entry(mr2, width=13)
        self.entry_monto.pack(side=tk.LEFT, padx=(8, 20))
        self._lbl(mr2, "Tipo:").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value="aumento")
        for val, txt in [("aumento", " Aumento "), ("disminucion", " Disminución ")]:
            tk.Radiobutton(
                mr2, text=txt, variable=self.tipo_var, value=val,
                bg=C["surface"], fg=C["text_dim"],
                selectcolor=C["surface3"], activebackground=C["surface"],
                font=("Segoe UI", 10),
            ).pack(side=tk.LEFT, padx=2)

        tk.Frame(b2, bg=C["surface"]).pack(pady=4)
        self._dark_btn(b2, "＋  Agregar Movimiento", self._agregar_mov,
                       bg=C["surface3"], fg=C["text"],
                       width=36).pack(padx=14, pady=(0, 12))

        # ── Panel derecho ─────────────────────────────────
        right = tk.Frame(pw, bg=C["main_bg"])
        pw.add(right, minsize=420)

        c3, b3 = card_frame(right, "Movimientos de la Transacción", icon="⚖️")
        c3.pack(fill=tk.BOTH, expand=True)

        # Barra de totales DEBE / HABER / DIFERENCIA
        tot_bar = tk.Frame(b3, bg=C["surface2"])
        tot_bar.pack(fill=tk.X)
        for tag, col in [("debe", C["debe_fg"]), ("haber", C["haber_fg"]),
                         ("dif",  C["accent"])]:
            tf2 = tk.Frame(tot_bar, bg=C["surface2"], padx=14, pady=8)
            tf2.pack(side=tk.LEFT, expand=True)
            name = {"debe": "DEBE", "haber": "HABER", "dif": "DIFERENCIA"}[tag]
            tk.Label(tf2, text=name, bg=C["surface2"], fg=C["text_muted"],
                     font=("Consolas", 8, "bold")).pack()
            lbl = tk.Label(tf2, text="S/. 0.00", bg=C["surface2"], fg=col,
                           font=("Consolas", 14, "bold"))
            lbl.pack()
            setattr(self, f"lbl_{tag}", lbl)

        # Treeview de movimientos del asiento
        cols = ("Código", "Cuenta", "Tipo", "Monto")
        tf3, self.tree_movs = make_treeview(b3, cols, (60, 200, 70, 90),
                                            ("center", "w", "center", "e"), height=8)
        tf3.pack(fill=tk.BOTH, expand=True)
        self.tree_movs.tag_configure("debe",  foreground=C["debe_fg"])
        self.tree_movs.tag_configure("haber", foreground=C["haber_fg"])

        # Botones eliminar / limpiar
        btn_row = tk.Frame(b3, bg=C["surface"])
        btn_row.pack(fill=tk.X, padx=14, pady=6)
        self._dark_btn(btn_row, "✕  Eliminar seleccionado", self._eliminar_mov,
                       bg=C["surface2"], fg=C["red"]).pack(side=tk.LEFT, padx=(0, 6))
        self._dark_btn(btn_row, "⌫  Limpiar todo", self._limpiar_movs,
                       bg=C["surface2"], fg=C["text_muted"]).pack(side=tk.LEFT)

        separator(b3)
        self._dark_btn(b3, "✔   REGISTRAR TRANSACCIÓN", self._registrar,
                       bg=C["accent"], fg=C["bg"],
                       font=("Segoe UI", 11, "bold"),
                       width=40).pack(padx=14, pady=(4, 14))

    # ──────────────────────────────────────────────────────────
    #  CALENDARIO POPUP
    #  Toplevel sin bordes (overrideredirect) que aparece debajo
    #  del entry de fecha.  Usa el módulo calendar de la stdlib
    #  para generar la grilla de días.
    # ──────────────────────────────────────────────────────────
    def _open_calendar(self):
        try:
            current = datetime.strptime(
                self.entry_fecha.get().strip(), "%Y-%m-%d")
            self._cal_year  = current.year
            self._cal_month = current.month
        except Exception:
            now = datetime.now()
            self._cal_year  = now.year
            self._cal_month = now.month

        top = tk.Toplevel(self)
        top.title("")
        top.resizable(False, False)
        top.configure(bg=C["surface"])
        top.attributes("-topmost", True)
        top.overrideredirect(True)   # sin barra de título del SO

        self.update_idletasks()
        x = self.entry_fecha.winfo_rootx()
        y = self.entry_fecha.winfo_rooty() + self.entry_fecha.winfo_height() + 4
        top.geometry(f"262x240+{x}+{y}")
        tk.Frame(top, bg=C["accent"], height=2).pack(fill=tk.X)
        container = tk.Frame(top, bg=C["surface"])
        container.pack(fill=tk.BOTH, expand=True)

        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        def render():
            for w in container.winfo_children():
                w.destroy()

            hdr = tk.Frame(container, bg=C["surface2"])
            hdr.pack(fill=tk.X)

            def prev_month():
                if self._cal_month == 1:
                    self._cal_month = 12; self._cal_year -= 1
                else:
                    self._cal_month -= 1
                render()

            def next_month():
                if self._cal_month == 12:
                    self._cal_month = 1; self._cal_year += 1
                else:
                    self._cal_month += 1
                render()

            tk.Button(hdr, text="◀", bg=C["surface2"], fg=C["accent"],
                      font=("Consolas", 10, "bold"), relief="flat", bd=0,
                      padx=10, pady=5, cursor="hand2",
                      activebackground=C["surface3"],
                      command=prev_month).pack(side=tk.LEFT)
            tk.Label(hdr,
                     text=f"{meses[self._cal_month]}  {self._cal_year}",
                     bg=C["surface2"], fg=C["text"],
                     font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True)
            tk.Button(hdr, text="▶", bg=C["surface2"], fg=C["accent"],
                      font=("Consolas", 10, "bold"), relief="flat", bd=0,
                      padx=10, pady=5, cursor="hand2",
                      activebackground=C["surface3"],
                      command=next_month).pack(side=tk.RIGHT)

            days_f = tk.Frame(container, bg=C["surface3"])
            days_f.pack(fill=tk.X)
            for d in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]:
                tk.Label(days_f, text=d, bg=C["surface3"], fg=C["text_muted"],
                         font=("Consolas", 8, "bold"), width=3,
                         anchor="center", pady=4).pack(side=tk.LEFT, expand=True)

            grid_f = tk.Frame(container, bg=C["surface"])
            grid_f.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

            # calendar.monthcalendar devuelve lista de semanas (listas de 7 días)
            # Los días fuera del mes se representan con 0
            cal_data = calendar.monthcalendar(self._cal_year, self._cal_month)

            try:
                cur   = datetime.strptime(self.entry_fecha.get().strip(), "%Y-%m-%d")
                sel_d = cur.day if (cur.year == self._cal_year and
                                    cur.month == self._cal_month) else -1
            except Exception:
                sel_d = -1
            today   = datetime.now()
            today_d = today.day if (today.year == self._cal_year and
                                    today.month == self._cal_month) else -1

            for week in cal_data:
                wf = tk.Frame(grid_f, bg=C["surface"])
                wf.pack(fill=tk.X)
                for day in week:
                    if day == 0:
                        tk.Label(wf, text="", bg=C["surface"],
                                 width=3, pady=2).pack(side=tk.LEFT, expand=True)
                    else:
                        if day == sel_d:
                            bg_d, fg_d = C["accent"], C["bg"]
                        elif day == today_d:
                            bg_d, fg_d = C["surface3"], C["accent"]
                        else:
                            bg_d, fg_d = C["surface"], C["text_dim"]

                        def make_cmd(d=day):
                            def cmd():
                                self.entry_fecha.delete(0, tk.END)
                                self.entry_fecha.insert(
                                    0, f"{self._cal_year:04d}-"
                                       f"{self._cal_month:02d}-{d:02d}")
                                top.destroy()
                            return cmd

                        tk.Button(wf, text=str(day), width=3,
                                  bg=bg_d, fg=fg_d,
                                  font=("Consolas", 9), relief="flat", bd=0,
                                  pady=3, cursor="hand2",
                                  activebackground=C["accent_dark"],
                                  activeforeground=C["bg"],
                                  command=make_cmd(day)).pack(
                                      side=tk.LEFT, expand=True)

            tk.Frame(container, bg=C["border"], height=1).pack(
                fill=tk.X, pady=(2, 0))
            foot = tk.Frame(container, bg=C["surface2"])
            foot.pack(fill=tk.X)
            tk.Button(foot, text="  Hoy  ",
                      bg=C["surface2"], fg=C["accent"],
                      font=("Consolas", 9, "bold"), relief="flat", bd=0,
                      pady=5, cursor="hand2",
                      command=lambda: [
                          self.entry_fecha.delete(0, tk.END),
                          self.entry_fecha.insert(
                              0, datetime.now().strftime("%Y-%m-%d")),
                          top.destroy()
                      ]).pack(side=tk.LEFT, padx=8)
            tk.Button(foot, text="Cerrar",
                      bg=C["surface2"], fg=C["text_muted"],
                      font=("Consolas", 9), relief="flat", bd=0,
                      pady=5, cursor="hand2",
                      command=top.destroy).pack(side=tk.RIGHT, padx=8)

        render()
        top.bind("<FocusOut>",
                 lambda e: top.destroy() if top.winfo_exists() else None)

    # ──────────────────────────────────────────────────────────
    #  EVENTOS DEL COMBOBOX DE CUENTA
    # ──────────────────────────────────────────────────────────
    def _on_combo_key(self, event):
        """
        Filtra las opciones del Combobox en tiempo real mientras
        el usuario escribe.  Usa comprensión de lista sobre
        self.sistema.planes para encontrar coincidencias en código o nombre.
        """
        if event.keysym in ("Return", "Escape", "Down", "Up"):
            return
        query = self.combo_cuenta.get().strip().lower()
        if not query:
            all_opts = [f"{cod}  –  {nom}"
                        for cat in self.sistema.planes.values()
                        for cod, nom in cat.items()]
            self.combo_cuenta["values"] = all_opts
            return
        filtered = [f"{cod}  –  {nom}"
                    for cat in self.sistema.planes.values()
                    for cod, nom in cat.items()
                    if query in cod or query in nom.lower()]
        self.combo_cuenta["values"] = filtered
        if filtered:
            self.combo_cuenta.after(
                10, lambda: self.combo_cuenta.event_generate("<Button-1>"))

    def _on_combo_select(self, event=None):
        """Extrae el código de la opción seleccionada y actualiza la etiqueta."""
        sel = self.combo_cuenta.get().strip()
        if "–" in sel:
            parts = sel.split("–", 1)
            cod = parts[0].strip()
            nom = parts[1].strip() if len(parts) > 1 else ""
            if cod in self.sistema.saldos:
                self._selected_cod = cod
                cat = self.sistema.get_categoria(cod)
                self.lbl_cuenta_sel.config(
                    text=f"✔  {cod} · {nom[:40]}  [{cat}]")
                self.entry_monto.focus_set()
                return
        self._selected_cod = None
        self.lbl_cuenta_sel.config(text="")

    def _on_combo_focusout(self, event=None):
        if not self.combo_cuenta.get():
            self.combo_cuenta.set("Seleccionar cuenta…")
        self._on_combo_select()

    # ══════════════════════════════════════════════════════════
    #  TAB 1 – LIBRO DIARIO
    # ══════════════════════════════════════════════════════════
    def _tab_diario(self, parent):
        tk.Label(parent, text="LIBRO DIARIO", bg=C["surface"], fg=C["accent"],
                 font=("Georgia", 13, "bold"), pady=10).pack()

        self._diario_tx_idx = None
        def on_diario_change(idx):
            self._diario_tx_idx = idx
            self._refresh_diario()

        _, self._diario_refresh_opts, _ = self._build_tx_selector(
            parent, on_diario_change)

        separator(parent, C["accent"])
        cols = ("Fecha", "Cuenta", "Debe (S/.)", "Haber (S/.)")
        tf, self.tree_diario = make_treeview(
            parent, cols, (100, 420, 130, 130),
            ("center", "w", "e", "e"), height=22)
        tf.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.tree_diario.tag_configure("sep",      foreground=C["text_muted"])
        self.tree_diario.tag_configure("ref",      foreground=C["text_muted"])
        self.tree_diario.tag_configure("debe_row", foreground=C["debe_fg"])
        self.tree_diario.tag_configure("haber_row",foreground=C["haber_fg"])

    def _refresh_diario(self):
        if hasattr(self, "_diario_refresh_opts"):
            self._diario_refresh_opts()
        for i in self.tree_diario.get_children():
            self.tree_diario.delete(i)

        txs = self.sistema.transacciones
        if self._diario_tx_idx is not None:
            txs = [self.sistema.transacciones[self._diario_tx_idx]]

        for t in txs:
            for m in [x for x in t["movimientos"] if x["tipo"] == "debe"]:
                self.tree_diario.insert("", tk.END,
                    values=(m.get("fecha", t["fecha"]),
                            f"{m['cuenta']}  {self.sistema.nombre(m['cuenta'])}",
                            f"{m['monto']:,.2f}", ""),
                    tags=("debe_row",))
            for m in [x for x in t["movimientos"] if x["tipo"] == "haber"]:
                self.tree_diario.insert("", tk.END,
                    values=(m.get("fecha", t["fecha"]),
                            f"        {m['cuenta']}  "
                            f"{self.sistema.nombre(m['cuenta'])}",
                            "", f"{m['monto']:,.2f}"),
                    tags=("haber_row",))
            self.tree_diario.insert("", tk.END,
                values=("", f"  ↳ {t['descripcion']}", "", ""),
                tags=("ref",))
            self.tree_diario.insert("", tk.END,
                values=("─"*10, "─"*50, "─"*12, "─"*12),
                tags=("sep",))

    # ══════════════════════════════════════════════════════════
    #  TAB 2 – LIBRO MAYOR
    # ══════════════════════════════════════════════════════════
    def _tab_mayor(self, parent):
        top = tk.Frame(parent, bg=C["surface"])
        top.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(top, text="Cuenta:", bg=C["surface"], fg=C["text_dim"],
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.combo_mayor = ttk.Combobox(top, style="Dark.TCombobox",
                                        font=("Consolas", 10), width=48)
        self.combo_mayor.pack(side=tk.LEFT, padx=8)
        self._dark_btn(top, "Ver Mayor", self._refresh_mayor,
                       bg=C["accent"], fg=C["bg"]).pack(side=tk.LEFT, padx=4)

        self._mayor_tx_idx = None
        _, self._mayor_refresh_opts, _ = self._build_tx_selector(
            parent,
            lambda idx: [setattr(self, "_mayor_tx_idx", idx),
                         self._refresh_mayor()])

        separator(parent)
        self.lbl_mayor_header = tk.Label(
            parent, text="", bg=C["surface"],
            fg=C["text"], font=("Consolas", 10, "bold"))
        self.lbl_mayor_header.pack(padx=12, pady=4, anchor="w")

        cols = ("Fecha", "Descripción", "Debe (S/.)", "Haber (S/.)", "Saldo (S/.)")
        tf, self.tree_mayor = make_treeview(
            parent, cols, (100, 280, 120, 120, 120),
            ("center", "w", "e", "e", "e"), height=20)
        tf.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        self.tree_mayor.tag_configure("debe_row",  foreground=C["debe_fg"])
        self.tree_mayor.tag_configure("haber_row", foreground=C["haber_fg"])

    def _refresh_mayor_combos(self):
        opts = [f"{cod} - {nom}"
                for cat in self.sistema.planes.values()
                for cod, nom in cat.items()]
        self.combo_mayor["values"] = opts

    def _refresh_mayor(self):
        if hasattr(self, "_mayor_refresh_opts"):
            self._mayor_refresh_opts()
        sel = self.combo_mayor.get().strip()
        if not sel:
            return
        m = re.match(r"^(\d+)", sel)   # extrae el código numérico
        if not m:
            return
        cod = m.group(1)

        # Filtrar según selector de Tx
        txs_a_ver = self.sistema.transacciones
        if self._mayor_tx_idx is not None:
            txs_a_ver = [self.sistema.transacciones[self._mayor_tx_idx]]

        movs, saldo = [], 0.0
        for t in txs_a_ver:
            for mov in t["movimientos"]:
                if mov["cuenta"] == cod:
                    val = mov["monto"] if mov["tipo"] == "debe" else -mov["monto"]
                    saldo += val
                    # Usar fecha individual del movimiento, no de la transacción
                    fecha_mov = mov.get("fecha", t["fecha"])
                    # Usar glosa del movimiento si existe, si no la de la transacción
                    glosa_mov = mov.get("glosa", t["descripcion"])
                    movs.append((
                        fecha_mov,
                        glosa_mov,
                        f"{mov['monto']:,.2f}" if mov["tipo"] == "debe"  else "",
                        f"{mov['monto']:,.2f}" if mov["tipo"] == "haber" else "",
                        f"{saldo:,.2f}",
                    ))

        self.lbl_mayor_header.config(
            text=f"  {cod} — {self.sistema.nombre(cod)}"
                 f"    Saldo en vista: S/. {saldo:,.2f}")
        for i in self.tree_mayor.get_children():
            self.tree_mayor.delete(i)
        for row in movs:
            tag = "debe_row" if row[2] else "haber_row"
            self.tree_mayor.insert("", tk.END, values=row, tags=(tag,))

    # ══════════════════════════════════════════════════════════
    #  TAB 3 – BALANCE DE SALDOS
    # ══════════════════════════════════════════════════════════
    def _tab_balance(self, parent):
        tk.Label(parent, text="BALANCE DE SALDOS", bg=C["surface"], fg=C["accent"],
                 font=("Georgia", 13, "bold"), pady=10).pack()

        self._bal_tx_idx = None
        def on_bal_change(idx):
            self._bal_tx_idx = idx
            self._refresh_balance()

        _, self._bal_refresh_opts, _ = self._build_tx_selector(
            parent, on_bal_change)

        separator(parent, C["accent"])
        cols = ("Categoría", "Código", "Cuenta", "Debe (S/.)", "Haber (S/.)")
        tf, self.tree_balance = make_treeview(
            parent, cols, (110, 65, 280, 120, 120),
            ("w", "center", "w", "e", "e"), height=20)
        tf.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.tree_balance.tag_configure(
            "total", foreground=C["accent"],
            font=("Consolas", 10, "bold"))
        self.tree_balance.tag_configure("debe_row",  foreground=C["debe_fg"])
        self.tree_balance.tag_configure("haber_row", foreground=C["haber_fg"])

    def _refresh_balance(self):
        self._bal_refresh_opts()
        saldos = self._saldos_activos(self._bal_tx_idx)
        for i in self.tree_balance.get_children():
            self.tree_balance.delete(i)
        for row in self.sistema.balance(saldos):
            tag = "total" if row[2] == "TOTALES" else (
                "debe_row" if row[3] else "haber_row")
            self.tree_balance.insert("", tk.END, values=row, tags=(tag,))

    # ══════════════════════════════════════════════════════════
    #  TAB 4 – ESTADO DE RESULTADOS
    # ══════════════════════════════════════════════════════════
    def _tab_resultados(self, parent):
        hdr = tk.Frame(parent, bg=C["surface2"], height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="ESTADO DE RESULTADOS",
                 bg=C["surface2"], fg=C["accent"],
                 font=("Georgia", 14, "bold")).pack(expand=True)

        self._er_tx_idx = None
        def on_er_change(idx):
            self._er_tx_idx = idx
            self._refresh_resultados()

        _, self._er_refresh_opts, _ = self._build_tx_selector(parent, on_er_change)
        self.frame_er = tk.Frame(parent, bg=C["surface"])
        self.frame_er.pack(fill=tk.BOTH, expand=True, padx=60, pady=20)

    def _refresh_resultados(self):
        if hasattr(self, "_er_refresh_opts") and self._er_refresh_opts:
            self._er_refresh_opts()
        for w in self.frame_er.winfo_children():
            w.destroy()
        saldos = self._saldos_activos(self._er_tx_idx)
        data   = self.sistema.estado_resultados(saldos)

        tk.Label(self.frame_er,
                 text=f"Al {datetime.now().strftime('%d/%m/%Y')}",
                 bg=C["surface"], fg=C["text_muted"],
                 font=("Consolas", 9)).pack(anchor="e", pady=(0, 10))

        for concepto, valor, is_total in data:
            f = tk.Frame(self.frame_er,
                         bg=C["surface2"] if is_total else C["surface"],
                         pady=4 if is_total else 2)
            f.pack(fill=tk.X, pady=(4 if is_total else 0))
            color    = (C["accent"] if is_total and valor >= 0
                        else C["red"] if valor < 0 else C["text"])
            font_lbl = ("Segoe UI", 10, "bold") if is_total else ("Segoe UI", 10)
            font_val = ("Consolas", 11, "bold") if is_total else ("Consolas", 10)
            tk.Label(f, text=f"  {concepto}",
                     bg=f.cget("bg"),
                     fg=C["text"] if is_total else C["text_dim"],
                     font=font_lbl).pack(side=tk.LEFT, padx=8)
            prefix = "" if valor >= 0 else "-"
            tk.Label(f, text=f"S/. {prefix}{abs(valor):,.2f}  ",
                     bg=f.cget("bg"), fg=color,
                     font=font_val).pack(side=tk.RIGHT, padx=8)
            if is_total:
                tk.Frame(self.frame_er, bg=C["border"],
                         height=1).pack(fill=tk.X)

    # ══════════════════════════════════════════════════════════
    #  TAB 5 – ESTADO DE SITUACIÓN FINANCIERA
    # ══════════════════════════════════════════════════════════
    def _tab_situacion(self, parent):
        hdr = tk.Frame(parent, bg=C["surface2"], height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="ESTADO DE SITUACIÓN FINANCIERA",
                 bg=C["surface2"], fg=C["accent"],
                 font=("Georgia", 14, "bold")).pack(expand=True)

        self._sf_tx_idx = None
        def on_sf_change(idx):
            self._sf_tx_idx = idx
            self._refresh_situacion()

        _, self._sf_refresh_opts, _ = self._build_tx_selector(parent, on_sf_change)
        self.frame_sf = tk.Frame(parent, bg=C["surface"])
        self.frame_sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

    def _refresh_situacion(self):
        if hasattr(self, "_sf_refresh_opts") and self._sf_refresh_opts:
            self._sf_refresh_opts()
        for w in self.frame_sf.winfo_children():
            w.destroy()
        saldos = self._saldos_activos(self._sf_tx_idx)
        d      = self.sistema.situacion_financiera(saldos)

        tk.Label(self.frame_sf,
                 text=f"Al {datetime.now().strftime('%d/%m/%Y')}",
                 bg=C["surface"], fg=C["text_muted"],
                 font=("Consolas", 9)).pack(anchor="e", pady=(0, 8))

        cols_f = tk.Frame(self.frame_sf, bg=C["surface"])
        cols_f.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(cols_f, bg=C["surface"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        def row(f, lbl, val, bold=False):
            r = tk.Frame(f, bg=C["surface"])
            r.pack(fill=tk.X, padx=20, pady=1)
            tk.Label(r, text=lbl, bg=C["surface"],
                     fg=C["text"] if bold else C["text_dim"],
                     font=("Segoe UI", 10, "bold" if bold else "normal")
                     ).pack(side=tk.LEFT)
            tk.Label(r, text=f"S/. {val:,.2f}", bg=C["surface"],
                     fg=C["accent"] if bold else C["text_dim"],
                     font=("Consolas", 10, "bold" if bold else "normal")
                     ).pack(side=tk.RIGHT)

        # ── Activo ────────────────────────────────────────
        section_title(left, "Activo Corriente")
        row(left, "Efectivo y Equiv.",     d["efectivo"])
        if d["cxc"]     != 0: row(left, "Cuentas por Cobrar",         d["cxc"])
        if d["cxc_div"] != 0: row(left, "Cuentas por Cobrar Diversas",d["cxc_div"])
        row(left, "Mercaderías",           d["mercs"])
        row(left, "Total Activo Corriente",d["tot_corr"], True)
        separator(left)
        section_title(left, "Activo No Corriente")
        if d["inmuebles"]    != 0: row(left, "Inmuebles, Maq. y Equipo", d["inmuebles"])
        if d["depreciacion"] != 0: row(left, "(-) Depreciación Acum.",  -d["depreciacion"])
        if d["intangibles"]  != 0: row(left, "Intangibles",              d["intangibles"])
        row(left, "Total Activo No Corriente", d["tot_no_corr"], True)
        separator(left)
        row(left, "ACTIVO TOTAL", d["tot_activo"], True)

        # ── Pasivo + Patrimonio ───────────────────────────
        right = tk.Frame(cols_f, bg=C["surface"],
                         highlightbackground=C["border"], highlightthickness=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        section_title(right, "Pasivo Corriente")
        if d["tributos"] != 0: row(right, "Tributos por Pagar",         d["tributos"])
        if d["remun"]    != 0: row(right, "Remuneraciones x Pagar",     d["remun"])
        if d["cxp_com"]  != 0: row(right, "Ctas. por Pagar Comerciales",d["cxp_com"])
        if d["cxp_div"]  != 0: row(right, "Ctas. por Pagar Diversas",   d["cxp_div"])
        row(right, "Total Pasivo Corriente", d["tot_pas_corr"], True)
        separator(right)

        section_title(right, "Pasivo No Corriente")
        if d["oblig_fin"] != 0:
            row(right, "Obligaciones Financieras", d["oblig_fin"])
        row(right, "Total Pasivo No Corriente", d["tot_pas_no_corr"], True)
        separator(right)

        section_title(right, "Patrimonio")
        row(right, "Capital",            d["capital"])
        if d["cap_adicional"] != 0: row(right, "Capital Adicional", d["cap_adicional"])
        if d["reservas"]      != 0: row(right, "Reservas",          d["reservas"])
        row(right, "Utilidad Acumulada", d["utilidad"])
        row(right, "Total Patrimonio",   d["tot_pat"], True)
        separator(right)
        row(right, "TOTAL PASIVO + PATRIMONIO", d["tot_pp"], True)

        # Indicador de cuadre de la ecuación contable
        diff       = abs(d["tot_activo"] - d["tot_pp"])
        color_chk  = C["accent"] if diff < 0.01 else C["red"]
        msg        = ("✔  Ecuación contable cuadra"
                      if diff < 0.01
                      else f"✗  Diferencia: S/. {diff:,.2f}")
        tk.Label(self.frame_sf, text=msg,
                 bg=C["surface"], fg=color_chk,
                 font=("Consolas", 9, "bold")).pack(
                     anchor="e", padx=20, pady=(6, 0))

    # ══════════════════════════════════════════════════════════
    #  TAB 6 – PLAN DE CUENTAS
    # ══════════════════════════════════════════════════════════
    def _tab_plan(self, parent):
        top = tk.Frame(parent, bg=C["surface"])
        top.pack(fill=tk.X, pady=8)
        self.plan_cat_var = tk.StringVar(value="Activo")
        for cat in self.sistema.planes.keys():
            tk.Radiobutton(
                top, text=cat, variable=self.plan_cat_var, value=cat,
                command=self._refresh_plan,
                bg=C["surface"], fg=C["text_dim"],
                selectcolor=C["surface3"], activebackground=C["surface"],
                font=("Segoe UI", 9),
            ).pack(side=tk.LEFT, padx=6)

        self._plan_tx_idx = None
        _, self._plan_refresh_opts, _ = self._build_tx_selector(
            parent,
            lambda idx: [setattr(self, "_plan_tx_idx", idx),
                         self._refresh_plan()])

        cols = ("Código", "Nombre de Cuenta", "Saldo (S/.)")
        tf, self.tree_plan = make_treeview(
            parent, cols, (70, 460, 130),
            ("center", "w", "e"), height=22)
        tf.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.tree_plan.tag_configure("pos",  foreground=C["debe_fg"])
        self.tree_plan.tag_configure("neg",  foreground=C["haber_fg"])
        self.tree_plan.tag_configure("zero", foreground=C["text_muted"])

    def _refresh_plan(self):
        if hasattr(self, "_plan_refresh_opts"):
            self._plan_refresh_opts()
        for i in self.tree_plan.get_children():
            self.tree_plan.delete(i)
        cat    = self.plan_cat_var.get()
        saldos = self._saldos_activos(self._plan_tx_idx)
        for cod, nom in self.sistema.planes[cat].items():
            s   = saldos.get(cod, 0.0)
            tag = "pos" if s > 0 else ("neg" if s < 0 else "zero")
            self.tree_plan.insert("", tk.END,
                values=(cod, nom, f"{s:,.2f}"), tags=(tag,))

    # ══════════════════════════════════════════════════════════
    #  LÓGICA DE MOVIMIENTOS (asiento en curso)
    # ══════════════════════════════════════════════════════════
    def _agregar_mov(self):
        """Valida y agrega un movimiento al asiento en curso."""
        if not self._selected_cod:
            self._on_combo_select()
        cod = self._selected_cod
        if not cod or cod not in self.sistema.saldos:
            messagebox.showerror("Error", "Selecciona una cuenta válida.")
            return
        try:
            monto = float(self.entry_monto.get().replace(",", "."))
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
            return

        fecha_linea = self.entry_fecha.get().strip()
        dh  = self.sistema.determinar_dh(cod, self.tipo_var.get())
        nom = self.sistema.nombre(cod)
        cat = self.sistema.get_categoria(cod)
        # Glosa = descripción legible del movimiento para el Libro Mayor
        # Formato: "NombreCuenta (Categoría) – fecha"
        glosa = f"{nom} ({cat})"
        self.movimientos_actuales.append({
            "cuenta": cod,
            "nombre": nom,
            "monto":  monto,
            "tipo":   dh,
            "fecha":  fecha_linea,
            "glosa":  glosa,
        })
        self._render_movimientos()
        self.entry_monto.delete(0, tk.END)
        self.combo_cuenta.set("")
        self._selected_cod = None
        self.combo_cuenta.focus_set()

    def _eliminar_mov(self):
        sel = self.tree_movs.selection()
        if not sel:
            return
        idx = self.tree_movs.index(sel[0])
        if 0 <= idx < len(self.movimientos_actuales):
            del self.movimientos_actuales[idx]
            self._render_movimientos()

    def _limpiar_movs(self):
        if self.movimientos_actuales and not messagebox.askyesno(
                "Confirmar", "¿Eliminar todos los movimientos?"):
            return
        self.movimientos_actuales.clear()
        self._render_movimientos()

    def _render_movimientos(self):
        """Actualiza el Treeview y los contadores DEBE / HABER / DIFERENCIA."""
        for i in self.tree_movs.get_children():
            self.tree_movs.delete(i)
        td = th = 0.0
        for m in self.movimientos_actuales:
            nom = m["nombre"]
            self.tree_movs.insert("", tk.END,
                values=(m["cuenta"],
                        nom[:28] + "…" if len(nom) > 28 else nom,
                        m["tipo"].upper(),
                        f"{m['monto']:,.2f}"),
                tags=(m["tipo"],))
            if m["tipo"] == "debe":
                td += m["monto"]
            else:
                th += m["monto"]
        self.lbl_debe.config(text=f"S/. {td:,.2f}")
        self.lbl_haber.config(text=f"S/. {th:,.2f}")
        dif   = abs(td - th)
        color = (C["accent"] if round(dif, 2) == 0 and self.movimientos_actuales
                 else C["red"] if dif > 0 else C["text_muted"])
        self.lbl_dif.config(text=f"S/. {dif:,.2f}", fg=color)

    def _registrar(self):
        """Valida el asiento completo y lo envía al modelo."""
        fecha = self.entry_fecha.get().strip()
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error",
                "Formato de fecha inválido. Usa YYYY-MM-DD.")
            return
        if not self.movimientos_actuales:
            messagebox.showwarning("Aviso", "Agrega al menos un movimiento.")
            return
        if not any(m["tipo"] == "debe"  for m in self.movimientos_actuales) or \
           not any(m["tipo"] == "haber" for m in self.movimientos_actuales):
            messagebox.showwarning("Aviso",
                "Debe haber al menos un débito y un crédito.")
            return

        # Descripción legible: fecha + nombre de las cuentas principales
        # Se toma la primera cuenta DEBE y la primera cuenta HABER
        ctas_debe  = [m for m in self.movimientos_actuales if m["tipo"] == "debe"]
        ctas_haber = [m for m in self.movimientos_actuales if m["tipo"] == "haber"]
        nom_debe   = ctas_debe[0]["nombre"]  if ctas_debe  else ""
        nom_haber  = ctas_haber[0]["nombre"] if ctas_haber else ""
        # Si hay muchas cuentas, mostrar cuántas hay en total
        extra = len(self.movimientos_actuales) - 2
        sufijo = f" (+{extra} más)" if extra > 0 else ""
        desc = f"{fecha}  |  {nom_debe[:22]}  →  {nom_haber[:22]}{sufijo}"
        try:
            self.sistema.registrar(self.movimientos_actuales[:], desc)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        n = len(self.sistema.transacciones)
        self.lbl_status.config(
            text=f"● {n} transacción{'es' if n != 1 else ''}")
        self.movimientos_actuales.clear()
        self._render_movimientos()
        self._show_toast(f"✔  Transacción #{n} registrada — {fecha}")

    # ──────────────────────────────────────────────────────────
    #  TOAST  (notificación flotante temporal)
    # ──────────────────────────────────────────────────────────
    def _show_toast(self, msg: str):
        """
        Muestra una notificación flotante en la esquina inferior
        derecha que desaparece automáticamente tras 2.8 segundos.
        Usa tk.Toplevel con overrideredirect para eliminar el marco del SO.
        """
        toast = tk.Toplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg=C["surface2"])
        x = self.winfo_rootx() + self.winfo_width()  - 440
        y = self.winfo_rooty() + self.winfo_height() - 70
        toast.geometry(f"420x42+{x}+{y}")
        tk.Frame(toast, bg=C["accent"], width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(toast, text=msg, bg=C["surface2"], fg=C["text"],
                 font=("Consolas", 10), padx=14).pack(side=tk.LEFT, expand=True)
        toast.after(2800, toast.destroy)

    # ──────────────────────────────────────────────────────────
    #  HELPERS DE WIDGETS  (reutilizados dentro de MainApp)
    # ──────────────────────────────────────────────────────────
    def _lbl(self, parent, text: str) -> tk.Label:
        """Etiqueta estándar con fuente y color del tema."""
        return tk.Label(parent, text=text,
                        bg=C["surface"], fg=C["text_dim"],
                        font=("Segoe UI", 10))

    def _entry(self, parent, width: int = 20) -> tk.Entry:
        """Entry de texto con estilo oscuro y cursor de acento."""
        return tk.Entry(parent, width=width,
                        bg=C["surface2"], fg=C["text"],
                        insertbackground=C["accent"],
                        relief="flat", font=("Consolas", 10),
                        highlightbackground=C["border"],
                        highlightthickness=1,
                        highlightcolor=C["accent"])

    def _dark_btn(self, parent, text: str, cmd,
                  bg=None, fg=None, font=None, width=None) -> tk.Button:
        """
        Botón plano (relief=flat) con estilo oscuro.
        Parámetros opcionales permiten personalizar color y fuente
        sin repetir el bloque de configuración en cada lugar.
        """
        kw = dict(
            text=text, command=cmd,
            bg=bg or C["surface3"], fg=fg or C["text"],
            font=font or ("Segoe UI", 10),
            activebackground=C["surface2"],
            activeforeground=fg or C["text"],
            relief="flat", bd=0, padx=10, pady=6,
            cursor="hand2",
        )
        if width:
            kw["width"] = width
        return tk.Button(parent, **kw)