"""
main.py  –  Punto de entrada del Sistema Contable
--------------------------------------------------
Contiene:
  - WelcomeScreen : pantalla animada de bienvenida (tk.Frame)
  - App           : controlador principal que gestiona la ventana raíz
                    y la transición Welcome → MainApp

Para ejecutar la aplicación:
  python main.py

Librerías usadas:
  - tkinter (stdlib): ventana raíz tk.Tk, tk.Frame, tk.Canvas, tk.Button
  - random  (stdlib): posición y velocidad aleatoria de las partículas
  - datetime(stdlib): fecha actual en la barra superior
"""

import tkinter as tk
from datetime import datetime
import random

from config import C
from modelo import SistemaContable
from vistas import MainApp


# ─────────────────────────────────────────────────────────────
#  PANTALLA DE BIENVENIDA
# ─────────────────────────────────────────────────────────────
class WelcomeScreen(tk.Frame):
    """
    Pantalla animada que se muestra al iniciar la aplicación.

    Técnica de animación:
      - Se crea un tk.Canvas que cubre todo el frame.
      - Se dibujan 22 textos contables (DEBE, HABER, S/., etc.)
        en posiciones aleatorias con random.seed(42) para que
        sean reproducibles.
      - El método _animate() se llama cada 30 ms con self.after(),
        moviendo cada partícula hacia arriba.  Cuando sale por
        la parte superior reaparece por abajo (efecto de loop).
    """

    def __init__(self, parent, on_enter):
        super().__init__(parent, bg=C["bg"])
        self.on_enter = on_enter   # callback para ingresar a MainApp
        self._dots   = []          # lista de partículas animadas
        self._build()
        self._animate()

    def _build(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Canvas de partículas (fondo)
        self.canvas = tk.Canvas(self, bg=C["bg"], bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._create_particles()

        # Frame central (contenido principal)
        center = tk.Frame(self, bg=C["bg"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Badge PCGE
        badge_f = tk.Frame(center, bg="#0D2B1F",
                           highlightbackground=C["accent"], highlightthickness=1)
        badge_f.pack(pady=(0, 20))
        tk.Label(badge_f,
                 text="●  SISTEMA CONTABLE PROFESIONAL  ·  PCGE PERÚ",
                 bg="#0D2B1F", fg=C["accent"],
                 font=("Consolas", 9, "bold"),
                 padx=14, pady=6).pack()

        # Título principal
        tk.Label(center, text="Bienvenido",
                 bg=C["bg"], fg=C["text"],
                 font=("Georgia", 52, "bold")).pack()
        tk.Label(center, text="Usuario",
                 bg=C["bg"], fg=C["accent"],
                 font=("Georgia", 52, "bold")).pack()

        tk.Label(center,
                 text="Gestión financiera inteligente  ·  "
                      "Libro Diario, Mayor, Balance y más",
                 bg=C["bg"], fg=C["text_dim"],
                 font=("Segoe UI", 11)).pack(pady=(8, 40))

        # Estadísticas rápidas
        stats_f = tk.Frame(center, bg=C["bg"])
        stats_f.pack(pady=(0, 40))
        for label, val in [("Cuentas PCGE", "120+"),
                           ("Módulos",      "7"),
                           ("Plan",         "PCGE")]:
            sf = tk.Frame(stats_f, bg=C["bg"])
            sf.pack(side=tk.LEFT, padx=24)
            tk.Label(sf, text=val, bg=C["bg"], fg=C["accent"],
                     font=("Consolas", 22, "bold")).pack()
            tk.Label(sf, text=label.upper(), bg=C["bg"], fg=C["text_muted"],
                     font=("Consolas", 8)).pack()

        # Botón principal de ingreso
        btn_f = tk.Frame(center, bg=C["accent_dark"])
        btn_f.pack(ipadx=2, ipady=2)
        self.btn = tk.Button(
            btn_f,
            text="  →   INGRESAR AL SISTEMA   ",
            bg=C["accent"], fg=C["bg"],
            font=("Segoe UI", 13, "bold"),
            bd=0, padx=28, pady=14,
            activebackground=C["accent_dark"],
            activeforeground=C["bg"],
            cursor="hand2",
            command=self.on_enter,
        )
        self.btn.pack()
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=C["accent_dark"]))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=C["accent"]))

        # Pie de página
        tk.Label(self,
                 text="© 2025 Sistema Contable Profesional  ·  "
                      "Gestión y Sistemas Financieros",
                 bg=C["bg"], fg=C["text_muted"],
                 font=("Consolas", 8)).place(
                     relx=0.5, rely=0.97, anchor="center")

    def _create_particles(self):
        """
        Crea 22 textos flotantes en posiciones aleatorias.
        random.seed(42) garantiza que el resultado sea siempre igual.
        """
        random.seed(42)
        texts = ["S/.", "DEBE", "HABER", "42,500", "Dr.", "Cr.",
                 "IGV", "PCGE", "1,200", "18%", "RUC", "Cts."]
        for _ in range(22):
            x = random.randint(50, 950)
            y = random.randint(50, 650)
            t = random.choice(texts)
            # Color semi-aleatorio de tono verde-azulado apagado
            fill = (f"#{random.randint(2,6):01x}{random.randint(5,9):01x}"
                    f"{random.randint(2,6):01x}{random.randint(2,6):01x}"
                    f"{random.randint(5,9):01x}{random.randint(2,6):01x}")
            item = self.canvas.create_text(
                x, y, text=t, fill=fill,
                font=("Consolas", random.randint(9, 13)),
            )
            self._dots.append({
                "id":    item,
                "x":     x,
                "y":     y,
                "speed": random.uniform(0.3, 0.8),
            })

    def _animate(self):
        """
        Bucle de animación: mueve cada partícula hacia arriba
        y la teletransporta abajo cuando sale del canvas.
        Se reprograma a sí misma cada 30 ms con self.after().
        """
        if not self.winfo_exists():
            return
        h = self.winfo_height() or 700
        for d in self._dots:
            d["y"] -= d["speed"]
            if d["y"] < -20:
                d["y"] = h + 20
            try:
                self.canvas.coords(d["id"], d["x"], d["y"])
            except Exception:
                pass
        self.after(30, self._animate)


# ─────────────────────────────────────────────────────────────
#  CONTROLADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────
class App:
    """
    Clase raíz de la aplicación.

    Responsabilidades:
      1. Crear la ventana principal (tk.Tk)
      2. Instanciar el modelo (SistemaContable)
      3. Mostrar WelcomeScreen al arrancar
      4. Reemplazar WelcomeScreen por MainApp al hacer clic en "Ingresar"

    Patrón: esta clase actúa como Controlador en MVC.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Contable Profesional")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg"])

        # Icono genérico (evita error si no hay archivo .ico)
        try:
            ico = tk.PhotoImage(width=32, height=32)
            self.root.iconphoto(True, ico)
        except Exception:
            pass

        # Modelo de datos (independiente de la interfaz)
        self.sistema = SistemaContable()
        self._show_welcome()

    def _show_welcome(self):
        """Muestra la pantalla de bienvenida."""
        self._welcome = WelcomeScreen(self.root, self._enter_app)

    def _enter_app(self):
        """
        Destruye WelcomeScreen y crea MainApp.
        Se pasa como callback a WelcomeScreen para que el botón
        "Ingresar" lo llame sin conocer la implementación.
        """
        self._welcome.destroy()
        MainApp(self.root, self.sistema)

    def run(self):
        """Inicia el bucle principal de eventos de tkinter."""
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().run()
