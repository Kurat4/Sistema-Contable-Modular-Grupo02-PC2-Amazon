"""
modelo.py  –  Modelo de datos del Sistema Contable (PCGE Perú)
--------------------------------------------------------------
Contiene la clase SistemaContable, que es el núcleo lógico
de la aplicación.  No importa tkinter ni ninguna librería de
interfaz; solo trabaja con datos puros.

Librerías usadas:
  - datetime  (stdlib): para obtener la fecha por defecto al registrar
"""

from datetime import datetime


class SistemaContable:
    """
    Modelo principal de la aplicación.

    Responsabilidades:
      1. Almacenar el Plan de Cuentas PCGE (self.planes)
      2. Mantener los saldos acumulados de cada cuenta (self.saldos)
      3. Guardar el historial de transacciones (self.transacciones)
      4. Calcular estados financieros: Balance, ER, ESF

    Patrón de diseño: Modelo en MVC (Model-View-Controller).
    La vista (vistas.py) solo llama métodos de esta clase; nunca
    modifica self.saldos directamente.
    """

    # ──────────────────────────────────────────────────────────
    #  CONSTRUCTOR
    # ──────────────────────────────────────────────────────────
    def __init__(self):
        # Plan de Cuentas PCGE organizado por categoría
        # Estructura: dict[str, dict[str, str]]
        #   categoría → { código_cuenta → nombre_cuenta }
        self.planes = {
            "Activo": {
                "10": "Efectivo y Equivalentes de Efectivo",
                "11": "Inversiones Financieras",
                "12": "Cuentas por Cobrar Comerciales - Terceros",
                "13": "Cuentas por Cobrar Comerciales - Relacionadas",
                "14": "Cuentas por Cobrar al Personal y Accionistas",
                "16": "Cuentas por Cobrar Diversas - Terceros",
                "17": "Cuentas por Cobrar Diversas - Relacionadas",
                "18": "Servicios Contratados por Anticipado",
                "20": "Mercaderías",
                "21": "Productos Terminados",
                "22": "Subproductos, Desechos y Desperdicio",
                "23": "Productos en Proceso",
                "24": "Materias Primas",
                "25": "Materiales Auxiliares, Suministros y Repuestos",
                "26": "Envases y Embalajes",
                "27": "Activos No Corrientes para la Venta",
                "28": "Existencias por Recibir",
                "29": "Desvalorización de Existencias",
                "30": "Inversiones Mobiliarias",
                "31": "Inversiones Inmobiliarias",
                "32": "Activos en Arrendamiento Financiero",
                "33": "Inmuebles, Maquinaria y Equipo",
                "34": "Intangibles",
                "35": "Activos Biológicos",
                "36": "Desvalorización de Activo Inmovilizado",
                "37": "Activo Diferido",
                "38": "Otros Activos",
                "39": "Depreciación, Amortización y Agotamiento Acumulado",
            },
            "Pasivos": {
                "40": "Tributos y Aportes por Pagar",
                "41": "Remuneraciones y Participaciones por Pagar",
                "42": "Cuentas por Pagar Comerciales - Terceros",
                "43": "Cuentas por Pagar Comerciales - Relacionadas",
                "44": "Cuentas por Pagar a Accionistas y Gerentes",
                "45": "Obligaciones Financieras",
                "46": "Cuentas por Pagar Diversas - Terceros",
                "47": "Cuentas por Pagar Diversas - Relacionadas",
                "48": "Provisiones",
                "49": "Pasivo Diferido",
            },
            "Patrimonio": {
                "50": "Capital",
                "51": "Acciones de Inversión",
                "52": "Capital Adicional",
                "56": "Resultados No Realizados",
                "57": "Excedente de Revaluación",
                "58": "Reservas",
            },
            "Gastos": {
                "60": "Compras",
                "61": "Variación de Existencias",
                "62": "Gastos de Personal",
                "63": "Gastos de Servicios por Terceros",
                "64": "Gastos por Tributos",
                "65": "Otros Gastos de Gestión",
                "66": "Pérdida por Activos No Financieros",
                "67": "Gastos Financieros",
                "68": "Valuacion y deterioro de activos y provisiones",
                "69": "Costo de Ventas",
            },
            "Ingresos": {
                "70": "Ventas",
                "71": "Variación de la Producción Almacenada",
                "72": "Producción de Activo Inmovilizado",
                "73": "Descuentos y Bonificaciones Obtenidos",
                "74": "Descuentos y Bonificaciones Concedidos",
                "75": "Otros Ingresos de Gestión",
                "76": "Ganancia por Activos No Financieros",
                "77": "Ingresos Financieros",
                "78": "Cargas Cubiertas por Provisiones",
                "79": "Cargas Imputables a Costos",
            },
            "Cuentas de Cierre": {
                "81": "Producción del Ejercicio",
                "82": "Valor Agregado",
                "83": "Excedente Bruto de Explotación",
                "84": "Resultado de Explotación",
                "85": "Resultado Antes de Impuestos",
                "87": "Participaciones de los Trabajadores",
                "88": "Impuesto a la Renta",
                "89": "Resultado del Ejercicio",
            },
            "Analíticas": {
                "91": "Costos por Distribuir",
                "92": "Costos de Producción",
                "93": "Centros de Costos",
                "94": "Gastos Administrativos",
                "95": "Gastos de Ventas",
                "96": "Gastos Financieros",
            },
        }

        # Saldos acumulados: dict[código, float]
        # Se inicializan en cero y se actualizan con cada registrar()
        self.saldos = {
            cod: 0.0
            for cat in self.planes.values()
            for cod in cat.keys()
        }

        # Lista de transacciones registradas
        # Cada elemento es un dict con: fecha, descripcion, movimientos
        self.transacciones = []

        # Construye los mapas de búsqueda rápida
        self._rebuild_maps()

    # ──────────────────────────────────────────────────────────
    #  MAPAS DE BÚSQUEDA  (código ↔ nombre)
    # ──────────────────────────────────────────────────────────
    def _rebuild_maps(self):
        """
        Crea tres estructuras auxiliares para búsqueda O(1):
          self.cod2nom : código  → nombre
          self.nom2cod : nombre  → código
          self.all_options : lista de strings "cod  –  nombre"
                             usada para poblar el Combobox
        """
        self.cod2nom = {}
        self.nom2cod = {}
        self.all_options = []
        for cat in self.planes.values():
            for cod, nom in cat.items():
                self.cod2nom[cod] = nom
                self.nom2cod[nom] = cod
                self.all_options.append(f"{cod}  –  {nom}")

    # ──────────────────────────────────────────────────────────
    #  HELPERS DE CONSULTA
    # ──────────────────────────────────────────────────────────
    def get_categoria(self, cod: str) -> str | None:
        """Devuelve la categoría ('Activo', 'Pasivos', etc.) de un código."""
        for cat, cuentas in self.planes.items():
            if cod in cuentas:
                return cat
        return None

    def nombre(self, cod: str) -> str:
        """Devuelve el nombre de una cuenta dado su código."""
        return self.cod2nom.get(cod, "Cuenta Desconocida")

    # ──────────────────────────────────────────────────────────
    #  REGLA DÉBITO / CRÉDITO  (Partida Doble)
    # ──────────────────────────────────────────────────────────
    def determinar_dh(self, cod: str, tipo: str) -> str:
        """
        Aplica la regla de Partida Doble para determinar si un
        movimiento va al DEBE o al HABER.

        Parámetros:
          cod  : código de la cuenta (p.ej. "10", "70")
          tipo : "aumento" o "disminucion"

        Reglas generales:
          Activo  → aumenta por el DEBE, disminuye por el HABER
          Pasivo / Patrimonio → aumenta por el HABER, disminuye por el DEBE
          Gastos  → aumenta por el DEBE (igual que Activo)
          Ingresos → aumenta por el HABER (igual que Pasivo)

        Casos especiales:
          39 (Depreciación acumulada) : cuenta de naturaleza acreedora
                                        aunque está en el grupo Activo
          74 (Desc. concedidos)       : cuenta de naturaleza deudora
                                        aunque está en el grupo Ingresos
        """
        cat = self.get_categoria(cod)
        if not cat:
            raise ValueError(f"Cuenta {cod} no encontrada en el plan.")

        # Casos especiales con naturaleza contraria a su categoría
        if cod == "74":
            return "debe" if tipo == "aumento" else "haber"
        if cod == "39":
            return "haber" if tipo == "aumento" else "debe"

        # Regla general por categoría
        if cat == "Activo":
            return "debe" if tipo == "aumento" else "haber"
        if cat in ("Pasivos", "Patrimonio"):
            return "haber" if tipo == "aumento" else "debe"
        if cat == "Gastos":
            return "debe" if tipo == "aumento" else "haber"
        if cat == "Ingresos":
            return "haber" if tipo == "aumento" else "debe"

        # Analíticas y Cuentas de Cierre: por defecto igual que Gastos
        return "debe" if tipo == "aumento" else "haber"

    # ──────────────────────────────────────────────────────────
    #  REGISTRAR TRANSACCIÓN
    # ──────────────────────────────────────────────────────────
    def registrar(self, movimientos: list, descripcion: str):
        """
        Valida y registra una transacción en el sistema.

        Validación: suma(DEBE) == suma(HABER)  →  Partida Doble
        Si no cuadra, lanza ValueError.

        Efecto en saldos:
          movimiento DEBE  → suma el monto al saldo de la cuenta
          movimiento HABER → resta el monto al saldo de la cuenta
        (Las cuentas acreedoras quedan con saldo negativo en este modelo,
         lo que se corrige con abs() al mostrar en los estados financieros)
        """
        # Obtener fecha principal del primer movimiento
        f_principal = (movimientos[0]["fecha"]
                       if movimientos
                       else datetime.now().strftime("%Y-%m-%d"))

        # Verificar cuadre de Partida Doble
        td = sum(m["monto"] for m in movimientos if m["tipo"] == "debe")
        th = sum(m["monto"] for m in movimientos if m["tipo"] == "haber")
        if round(td, 2) != round(th, 2):
            raise ValueError(f"No cuadra: Debe {td:,.2f} ≠ Haber {th:,.2f}")

        # Actualizar saldos acumulados
        for m in movimientos:
            if m["tipo"] == "debe":
                self.saldos[m["cuenta"]] += m["monto"]
            else:
                self.saldos[m["cuenta"]] -= m["monto"]

        # Guardar en historial
        self.transacciones.append({
            "fecha":       f_principal,
            "descripcion": descripcion,
            "movimientos": list(movimientos),
        })

    def eliminar_transaccion(self, idx: int) -> bool:
        """
        Elimina una transacción por índice y revierte sus efectos
        en los saldos.  Devuelve True si tuvo éxito.
        """
        if not (0 <= idx < len(self.transacciones)):
            return False
        for m in self.transacciones[idx]["movimientos"]:
            if m["tipo"] == "debe":
                self.saldos[m["cuenta"]] -= m["monto"]
            else:
                self.saldos[m["cuenta"]] += m["monto"]
        del self.transacciones[idx]
        return True

    # ──────────────────────────────────────────────────────────
    #  SALDOS PARCIALES  (para el selector de Tx)
    # ──────────────────────────────────────────────────────────
    def _saldos_de(self, txs: list) -> dict:
        """
        Calcula los saldos resultantes de una lista parcial de
        transacciones (no del total).  Útil para mostrar los
        estados financieros de una sola transacción.

        Parámetro:
          txs : subconjunto de self.transacciones
        Retorna:
          dict[código_cuenta, float]  con los saldos calculados
        """
        s = {cod: 0.0
             for cat in self.planes.values()
             for cod in cat.keys()}
        for t in txs:
            for m in t["movimientos"]:
                if m["tipo"] == "debe":
                    s[m["cuenta"]] += m["monto"]
                else:
                    s[m["cuenta"]] -= m["monto"]
        return s

    # ──────────────────────────────────────────────────────────
    #  LIBRO DIARIO
    # ──────────────────────────────────────────────────────────
    def diario(self) -> list[tuple]:
        """
        Devuelve todas las filas del Libro Diario como lista de tuplas
        (fecha, cuenta, debe, haber) listas para insertar en un Treeview.
        """
        rows = []
        for t in self.transacciones:
            for m in [x for x in t["movimientos"] if x["tipo"] == "debe"]:
                rows.append((m.get("fecha", t["fecha"]),
                             f"{m['cuenta']} {self.nombre(m['cuenta'])}",
                             f"{m['monto']:,.2f}", ""))
            for m in [x for x in t["movimientos"] if x["tipo"] == "haber"]:
                rows.append((m.get("fecha", t["fecha"]),
                             f"        {m['cuenta']} {self.nombre(m['cuenta'])}",
                             "", f"{m['monto']:,.2f}"))
            rows.append(("", f"  ↳ {t['descripcion']}", "", ""))
            rows.append(("─", "─", "─", "─"))
        return rows

    # ──────────────────────────────────────────────────────────
    #  BALANCE DE SALDOS
    # ──────────────────────────────────────────────────────────
    def balance(self, saldos: dict = None) -> list[tuple]:
        """
        Genera las filas del Balance de Saldos.

        Parámetro opcional 'saldos': permite pasar saldos parciales
        (de una sola transacción) en lugar de los acumulados.

        Retorna lista de tuplas: (categoría, código, nombre, debe, haber)
        Solo incluye cuentas con saldo ≠ 0, más una fila de TOTALES.
        """
        if saldos is None:
            saldos = self.saldos
        rows = []
        for cat, cuentas in self.planes.items():
            for cod, nom in cuentas.items():
                s = saldos.get(cod, 0.0)
                if s != 0:
                    rows.append((cat, cod, nom,
                                 f"{s:,.2f}"      if s > 0 else "",
                                 f"{abs(s):,.2f}" if s < 0 else ""))
        td = sum(v for v in saldos.values() if v > 0)
        th = sum(abs(v) for v in saldos.values() if v < 0)
        rows.append(("", "", "TOTALES", f"{td:,.2f}", f"{th:,.2f}"))
        return rows

    # ──────────────────────────────────────────────────────────
    #  LIBRO MAYOR
    # ──────────────────────────────────────────────────────────
    def mayor(self, cod: str) -> tuple[list, float]:
        """
        Devuelve los movimientos de una cuenta específica y su saldo final.

        Retorna:
          (lista_de_filas, saldo_final)
          cada fila: (fecha, descripción, debe, haber, saldo_acumulado)
        """
        movs, saldo = [], 0.0
        for t in self.transacciones:
            for m in t["movimientos"]:
                if m["cuenta"] == cod:
                    saldo += m["monto"] if m["tipo"] == "debe" else -m["monto"]
                    # Usar la fecha individual del movimiento (m["fecha"]),
                    # no la fecha general de la transacción (t["fecha"]).
                    # La descripción es la glosa del movimiento si existe,
                    # o la glosa general de la transacción como respaldo.
                    fecha_mov = m.get("fecha", t["fecha"])
                    glosa_mov = m.get("glosa", t["descripcion"])
                    movs.append((
                        fecha_mov,
                        glosa_mov,
                        f"{m['monto']:,.2f}" if m["tipo"] == "debe"  else "",
                        f"{m['monto']:,.2f}" if m["tipo"] == "haber" else "",
                        f"{saldo:,.2f}",
                    ))
        return movs, saldo

    # ──────────────────────────────────────────────────────────
    #  ESTADO DE RESULTADOS
    # ──────────────────────────────────────────────────────────
    def estado_resultados(self, saldos: dict = None) -> list[tuple]:
        """
        Calcula el Estado de Resultados.

        Estructura:
          Ventas Netas              = 70 - 74
          (-) Costo de Ventas       = 69
          Utilidad Bruta
          (-) Gastos Operativos     = 94 + 95 + 96 + 62 + 63 + 68
          Utilidad Operativa
          (+) Otros Ingresos        = 75 + 76 + 77
          (-) Otros Gastos          = 65 + 66 + 67
          Utilidad Antes de Imptos.

        Retorna lista de tuplas: (concepto, valor, es_subtotal)
          es_subtotal=True → se muestra en negrita y fondo diferente
        """
        if saldos is None:
            saldos = self.saldos
        s = saldos

        # ── Ventas ────────────────────────────────────────────
        ventas     = abs(s.get("70", 0))
        descuentos = abs(s.get("74", 0))   # 74 es deudora (resta ventas)
        v_netas    = ventas - descuentos

        # ── Costo de ventas ───────────────────────────────────
        costo_venta = abs(s.get("69", 0))
        u_bruta     = v_netas - costo_venta

        # ── Gastos Operativos ─────────────────────────────────
        # Cuentas analíticas (9x) más gastos directos sin pasar por analíticas
        g_adm       = abs(s.get("94", 0))   # Gastos Administrativos
        g_ventas_c  = abs(s.get("95", 0))   # Gastos de Ventas
        g_fin_anal  = abs(s.get("96", 0))   # Gastos Financieros (analítica)
        g_personal  = abs(s.get("62", 0))   # Gastos de Personal
        g_servicios = abs(s.get("63", 0))   # Servicios por Terceros
        g_deprec    = abs(s.get("68", 0))   # Depreciación / Valuación

        g_op = g_adm + g_ventas_c + g_fin_anal + g_personal + g_servicios + g_deprec
        u_op = u_bruta - g_op

        # ── Otros Ingresos y Gastos ───────────────────────────
        otros_ingresos = (abs(s.get("75", 0)) +
                          abs(s.get("76", 0)) +
                          abs(s.get("77", 0)))
        otros_gastos   = (abs(s.get("65", 0)) +
                          abs(s.get("66", 0)) +
                          abs(s.get("67", 0)))

        u_antes_imp = u_op + otros_ingresos - otros_gastos

        # Retorna lista de (concepto, valor_float, es_subtotal)
        return [
            ("Ventas Netas",                 v_netas,        False),
            ("(-) Costo de Ventas",          -costo_venta,   False),
            ("Utilidad Bruta",               u_bruta,        True),
            ("(-) Gastos Operativos",        -g_op,          False),
            ("Utilidad Operativa",           u_op,           True),
            ("(+) Otros Ingresos",           otros_ingresos, False),
            ("(-) Otros Gastos",             -otros_gastos,  False),
            ("Utilidad Antes de Impuestos",  u_antes_imp,    True),
        ]

    # ──────────────────────────────────────────────────────────
    #  ESTADO DE SITUACIÓN FINANCIERA
    # ──────────────────────────────────────────────────────────
    def situacion_financiera(self, saldos: dict = None) -> dict:
        """
        Calcula el Estado de Situación Financiera (Balance General).

        Nota sobre saldos negativos:
          Las cuentas de Pasivo y Patrimonio se incrementan con HABER,
          por lo que en self.saldos quedan con valor negativo.
          Se usa abs(min(s, 0)) para extraer su valor positivo.

          Para cuentas de Activo se usa el saldo tal cual (puede ser
          negativo si hay más salidas que entradas, como en la cuenta 10).

        Retorna un dict con todas las partidas listo para consumir
        por la vista (_refresh_situacion en vistas.py).
        """
        if saldos is None:
            saldos = self.saldos
        s = saldos

        # ── ACTIVO CORRIENTE ──────────────────────────────────
        # CORRECCIÓN: se usa s.get() directo (sin max(...,0)) para
        # que los saldos negativos se muestren correctamente.
        efectivo = s.get("10", 0)           # Efectivo y Equivalentes
        cxc      = s.get("12", 0)           # Cuentas por Cobrar Comerciales
        cxc_div  = s.get("16", 0)           # Cuentas por Cobrar Diversas
        mercs    = s.get("20", 0)           # Mercaderías
        tot_corr = efectivo + cxc + cxc_div + mercs

        # ── ACTIVO NO CORRIENTE ───────────────────────────────
        inmuebles    = max(s.get("33", 0), 0)
        # 39 es cuenta acreedora → saldo negativo en el modelo
        depreciacion = abs(min(s.get("39", 0), 0))
        intangibles  = max(s.get("34", 0), 0)
        tot_no_corr  = inmuebles - depreciacion + intangibles

        tot_activo = tot_corr + tot_no_corr

        # ── PASIVO CORRIENTE ──────────────────────────────────
        # min(..., 0) captura solo valores negativos (cuentas acreedoras)
        tributos = abs(min(s.get("40", 0), 0))   # Tributos por Pagar
        remun    = abs(min(s.get("41", 0), 0))   # Remuneraciones
        cxp_com  = abs(min(s.get("42", 0), 0))   # CxP Comerciales
        cxp_div  = abs(min(s.get("46", 0), 0))   # CxP Diversas
        tot_pas_corr = tributos + remun + cxp_com + cxp_div

        # ── PASIVO NO CORRIENTE ───────────────────────────────
        oblig_fin       = abs(min(s.get("45", 0), 0))   # Obligaciones Financieras
        tot_pas_no_corr = oblig_fin
        tot_pasivo      = tot_pas_corr + tot_pas_no_corr

        # ── PATRIMONIO ────────────────────────────────────────
        capital       = abs(min(s.get("50", 0), 0))
        cap_adicional = abs(min(s.get("52", 0), 0))
        reservas      = abs(min(s.get("58", 0), 0))

        # La utilidad proviene del Estado de Resultados
        er            = self.estado_resultados(saldos)
        utilidad_acum = er[-1][1]   # último ítem = Utilidad Antes de Impuestos

        tot_pat = capital + cap_adicional + reservas + utilidad_acum
        tot_pp  = tot_pasivo + tot_pat

        return dict(
            # Activo corriente
            efectivo=efectivo, cxc=cxc, cxc_div=cxc_div, mercs=mercs,
            tot_corr=tot_corr,
            # Activo no corriente
            inmuebles=inmuebles, depreciacion=depreciacion,
            intangibles=intangibles, tot_no_corr=tot_no_corr,
            tot_activo=tot_activo,
            # Pasivo corriente
            tributos=tributos, remun=remun,
            cxp_com=cxp_com, cxp_div=cxp_div,
            tot_pas_corr=tot_pas_corr,
            # Pasivo no corriente
            oblig_fin=oblig_fin, tot_pas_no_corr=tot_pas_no_corr,
            tot_pasivo=tot_pasivo,
            # Patrimonio
            capital=capital, cap_adicional=cap_adicional,
            reservas=reservas, utilidad=utilidad_acum,
            tot_pat=tot_pat,
            tot_pp=tot_pp,
        )