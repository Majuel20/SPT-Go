"""Ventana de SPT Go. Entrada principal para el EXE portable."""
from __future__ import annotations

import json
import math
import os
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from spt_config import APP_NAME, BYLINE, COLORS, VERSION, Settings, integer, load_settings, number, portable_dir, preview_geometry, save_settings
from spt_service import generate

BG = "#080d16"
PANEL = "#111b29"
FIELD = "#09121f"
INK = "#e9f3ff"
MUTED = "#8a9eb8"
BLUE = "#00d9f5"
TONES = {"cyan": "#00e5ff", "green": "#a0ff53", "purple": "#bb85ff", "amber": "#ffca59"}


class NeonButton(tk.Canvas):
    """Boton redondeado con borde neon, hover y acceso por teclado."""
    def __init__(self, parent, *, text, command, tone="cyan", style=None, state="normal", **kwargs):
        self._text, self._command = text, command
        self._tone = "green" if style == "Accent.TButton" else tone
        self._solid = style == "Accent.TButton"
        self._disabled = state == "disabled"
        self._hover = False
        self._focused = False
        font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        try:
            background = ttk.Style().lookup(parent.cget("style") or parent.winfo_class(), "background") or BG
        except tk.TclError:
            background = BG
        super().__init__(parent, width=max(100, font.measure(text) + 38), height=42, background=background, highlightthickness=0, bd=0, takefocus=True, cursor="hand2", **kwargs)
        self._font = font
        self.bind("<Configure>", lambda event: self._paint())
        self.bind("<Enter>", lambda event: self._set_hover(True))
        self.bind("<Leave>", lambda event: self._set_hover(False))
        self.bind("<FocusIn>", lambda event: self._set_focus(True))
        self.bind("<FocusOut>", lambda event: self._set_focus(False))
        self.bind("<Button-1>", lambda event: self._invoke())
        self.bind("<Return>", lambda event: self._invoke())
        self.bind("<space>", lambda event: self._invoke())
        self._paint()

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, dict):
            kwargs = {**cnf, **kwargs}
            cnf = None
        if "state" in kwargs:
            self._disabled = kwargs.pop("state") == "disabled"
        result = super().configure(cnf, **kwargs)
        if hasattr(self, "_font"):
            self._paint()
        return result

    config = configure

    def _set_hover(self, value):
        self._hover = value
        self._paint()

    def _set_focus(self, value):
        self._focused = value
        self._paint()

    def _invoke(self):
        if not self._disabled:
            self.focus_set()
            self._command()

    def _rounded(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius,y1,x2-radius,y1,x2,y1,x2,y1+radius,x2,y2-radius,x2,y2,x2-radius,y2,x1+radius,y2,x1,y2,x1,y2-radius,x1,y1+radius,x1,y1]
        self.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def _paint(self):
        self.delete("all")
        width = max(self.winfo_width(), int(self.cget("width")))
        height = max(self.winfo_height(), 42)
        color = TONES[self._tone]
        active = self._hover or self._focused
        fill = color if (self._solid or active) and not self._disabled else PANEL
        foreground = BG if fill == color else color
        outline = color
        if self._disabled:
            fill, outline, foreground = "#151e2b", "#2c3b4d", "#63758b"
        glow = "#25445a" if self._tone == "cyan" else ("#354c2c" if self._tone == "green" else "#3a2c51")
        self._rounded(2, 2, width-2, height-2, 10, fill="", outline=glow if not self._disabled else PANEL, width=3)
        self._rounded(4, 4, width-4, height-4, 9, fill=fill, outline=outline, width=1.5)
        self.create_text(width/2, height/2, text=self._text, fill=foreground, font=self._font)


class Application(tk.Tk):
    def __init__(self, *, load_previous=True):
        super().__init__()
        self.title(f"{APP_NAME} · {VERSION} · {BYLINE}")
        width = min(1160, self.winfo_screenwidth() - 40)
        height = min(810, self.winfo_screenheight() - 80)
        self.geometry(f"{max(960, width)}x{max(650, height)}")
        self.minsize(960, 650)
        self.configure(background=BG)
        assets = Path(__file__).resolve().parent
        try:
            self.logo_image = tk.PhotoImage(file=str(assets / "logo.png"))
            self.iconphoto(True, self.logo_image)
            if sys.platform == "win32":
                self.iconbitmap(str(assets / "app.ico"))
        except tk.TclError:
            self.logo_image = None
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.busy = False
        self.events = queue.Queue()
        self.result_folder = None
        self.last_config = None
        self.preview_job = None
        self.profile_path = portable_dir() / "SPT_Go_config.json"
        self.vars = {}
        for key, value in Settings().to_dict().items():
            self.vars[key] = tk.BooleanVar(self, value=value) if isinstance(value, bool) else tk.StringVar(self, value=str(value))
        self.status = tk.StringVar(self, "Configura el proyecto y revisa las rutas antes de generar.")
        self.stats = tk.StringVar(self, "")
        self.switch_label = tk.StringVar(self, "OFF · Direcciones independientes")
        self._style()
        self._build()
        self._apply(Settings())
        previous_profile = self.profile_path
        legacy_profile = portable_dir() / "SPAT_SSEE_config.json"
        if not previous_profile.is_file() and legacy_profile.is_file():
            previous_profile = legacy_profile
        if load_previous and previous_profile.is_file():
            try:
                self._apply(load_settings(previous_profile))
                self.status.set("Se recupero la ultima configuracion guardada.")
            except Exception:
                self.status.set("La configuracion anterior no pudo cargarse. Se muestra el ejemplo inicial.")
        self.after(100, self._poll)

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("White.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 10))
        style.configure("White.TLabel", background=PANEL, foreground=INK)
        style.configure("Hint.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TLabelframe", background=PANEL, bordercolor="#283b50", relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=PANEL, foreground=BLUE, font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=6, fieldbackground=FIELD, foreground=INK, insertcolor=INK, bordercolor="#354c65")
        style.map("TEntry", bordercolor=[("focus", BLUE)], fieldbackground=[("disabled", "#172332")], foreground=[("disabled", MUTED)])
        style.configure("TSpinbox", padding=6, fieldbackground=FIELD, foreground=INK, arrowcolor=BLUE, background=PANEL)
        style.configure("TCombobox", padding=5, fieldbackground=FIELD, foreground=INK, arrowcolor=BLUE, background=PANEL)
        style.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", INK)], selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", INK)])
        self.option_add("*TCombobox*Listbox.background", FIELD)
        self.option_add("*TCombobox*Listbox.foreground", INK)
        self.option_add("*TCombobox*Listbox.selectBackground", "#26405c")
        style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10), background="#e3ebf5", foreground=INK)
        style.map("TButton", background=[("active", "#d5e2f3")])
        style.configure("Accent.TButton", background=BLUE, foreground="white", font=("Segoe UI", 11, "bold"), padding=(18, 9))
        style.map("Accent.TButton", background=[("disabled", "#a5b8d1"), ("active", "#1454b5")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(10, 10), font=("Segoe UI", 10))
        style.configure("TNotebook.Tab", background="#162336", foreground=MUTED)
        style.map("TNotebook.Tab", background=[("selected", PANEL)], foreground=[("selected", BLUE)])
        style.configure("TCheckbutton", background=PANEL, foreground=INK, font=("Segoe UI", 10), indicatorbackground=FIELD, indicatorforeground=TONES["green"])
        style.map("TCheckbutton", background=[("active", PANEL)], foreground=[("selected", TONES["green"])])
        style.configure("Vertical.TScrollbar", background="#26384d", troughcolor=FIELD, arrowcolor=MUTED, borderwidth=0)
        style.configure("Horizontal.TProgressbar", background=TONES["green"], troughcolor=BG, borderwidth=0)

    def _build(self):
        header = tk.Frame(self, bg=BG, padx=22, pady=15)
        header.pack(fill="x")
        if self.logo_image is not None:
            tk.Label(header, image=self.logo_image, bg=TONES["cyan"], padx=6, pady=6).pack(side="left", padx=(0, 16))
        heading = tk.Frame(header, bg=BG)
        heading.pack(side="left", fill="x", expand=True)
        tk.Label(heading, text=APP_NAME, bg=BG, fg=TONES["cyan"], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(heading, text=BYLINE, bg=BG, fg=TONES["purple"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(heading, text="Planificador de rutas de puesta a tierra · Excel + Google Earth", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))
        tk.Label(header, text="PORTABLE\n" + VERSION, bg=BG, fg=TONES["green"], font=("Segoe UI", 10, "bold")).pack(side="right")

        toolbar = ttk.Frame(self, padding=(18, 9))
        toolbar.pack(fill="x")
        NeonButton(toolbar, text="Cargar proyecto", command=self._load).pack(side="left")
        NeonButton(toolbar, text="Guardar proyecto", command=self._save, tone="purple").pack(side="left", padx=6)
        NeonButton(toolbar, text="Cargar ejemplo", command=lambda: self._apply(Settings()), tone="amber").pack(side="left")
        NeonButton(toolbar, text="Ayuda", command=self._help).pack(side="right")

        content = ttk.Frame(self, padding=(18, 0, 18, 8))
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=5)
        content.columnconfigure(1, weight=4)
        content.rowconfigure(0, weight=1)
        self.tabs = ttk.Notebook(content)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        data_tab, data = self._scroll_tab()
        potential_tab, potential = self._scroll_tab()
        output_tab, output = self._scroll_tab()
        self.tabs.add(data_tab, text="1. Proyecto y corriente")
        self.tabs.add(potential_tab, text="2. Potencial")
        self.tabs.add(output_tab, text="3. Salida")

        card = ttk.LabelFrame(data, text="Proyecto y sistema de coordenadas", padding=12)
        card.pack(fill="x", pady=(0, 12))
        card.columnconfigure(1, weight=1)
        self._field(card, "Nombre del proyecto", "project", 0)
        ttk.Label(card, text="Zona UTM", style="White.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Spinbox(card, from_=1, to=60, width=8, textvariable=self.vars["zone"]).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(card, text="Hemisferio", style="White.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.hemisphere = tk.StringVar(self, "Sur")
        ttk.Combobox(card, textvariable=self.hemisphere, values=("Sur", "Norte"), state="readonly", width=12).grid(row=2, column=1, sticky="w", pady=4)

        card = ttk.LabelFrame(data, text="Origen comun", padding=12)
        card.pack(fill="x", pady=(0, 12))
        card.columnconfigure(1, weight=1)
        self._field(card, "Este UTM", "origin_e", 0)
        self._field(card, "Norte UTM", "origin_n", 1)
        ttk.Label(card, text="Inicio de corriente, potencial y circunferencias.", style="Hint.TLabel").grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        card = ttk.LabelFrame(data, text="Corriente: direccion y pozo auxiliar", padding=12)
        card.pack(fill="x")
        card.columnconfigure(1, weight=1)
        self._field(card, "Este de direccion", "current_e", 0)
        self._field(card, "Norte de direccion", "current_n", 1)
        self._field(card, "Distancia al pozo (m)", "distance", 2)
        ttk.Label(card, text="El segundo punto orienta la recta. La distancia ubica el pozo.\nSolo se genera el punto Pozo auxiliar (C100%).", style="Hint.TLabel", wraplength=440).grid(row=3, column=0, columnspan=2, sticky="w", pady=(7, 0))

        card = ttk.LabelFrame(potential, text="Direccion de potencial", padding=12)
        card.pack(fill="x", pady=(0, 12))
        ttk.Checkbutton(card, text="Usar la misma direccion de corriente", variable=self.vars["same_direction"], command=self._toggle_direction).pack(anchor="w")
        ttk.Label(card, textvariable=self.switch_label, style="Hint.TLabel").pack(anchor="w", pady=(5, 10))
        self.direction_text = tk.Text(card, height=5, font=("Consolas", 10), wrap="none", relief="solid", bd=1, highlightthickness=1, highlightbackground="#354c65", highlightcolor=BLUE, padx=8, pady=8, foreground=INK, background=FIELD, insertbackground=INK, selectbackground="#26405c")
        self.direction_text.pack(fill="x")
        ttk.Label(card, text="En OFF: un par Este, Norte; por ruta. Usa punto decimal.\nTodas las rutas toman automaticamente el origen de corriente.", style="Hint.TLabel", wraplength=450).pack(anchor="w", pady=(7, 0))

        card = ttk.LabelFrame(potential, text="Abanico: solo para potencial", padding=12)
        card.pack(fill="x", pady=(0, 12))
        card.columnconfigure(1, weight=1)
        ttk.Label(card, text="Rayos a cada lado", style="White.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Spinbox(card, from_=0, to=100, width=10, textvariable=self.vars["potential_rays"]).grid(row=0, column=1, sticky="w", pady=4)
        self._field(card, "Separacion (m)", "ray_separation", 1)
        ttk.Label(card, text="0 rayos = una recta por direccion. Separacion definida al 100%.", style="Hint.TLabel", wraplength=440).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        card = ttk.LabelFrame(potential, text="Porcentajes y circunferencias", padding=12)
        card.pack(fill="x")
        ttk.Entry(card, textvariable=self.vars["percentages"]).pack(fill="x")
        ttk.Label(card, text="Separa con ;. Ejemplo: 0; 10; 50; 61.8; 90; 100\nMenores a 100: potencial. 100: pozo y circunferencia.", style="Hint.TLabel", wraplength=450).pack(anchor="w", pady=(7, 0))

        card = ttk.LabelFrame(output, text="Carpeta de resultados", padding=12)
        card.pack(fill="x", pady=(0, 12))
        ttk.Entry(card, textvariable=self.vars["output_dir"]).pack(fill="x")
        NeonButton(card, text="Elegir carpeta", command=self._choose_output, tone="purple").pack(anchor="w", pady=(8, 0))
        ttk.Label(card, text="Cada generacion crea una carpeta nueva con fecha y hora.\nIncluye Excel, KML, KMZ y la configuracion del proyecto.", style="Hint.TLabel", wraplength=450).pack(anchor="w", pady=(8, 0))

        card = ttk.LabelFrame(output, text="Google Earth", padding=12)
        card.pack(fill="x", pady=(0, 12))
        ttk.Checkbutton(card, text="Integrar con un KML/KMZ existente", variable=self.vars["use_base"], command=self._toggle_base).pack(anchor="w")
        self.base_entry = ttk.Entry(card, textvariable=self.vars["base_file"])
        self.base_entry.pack(fill="x", pady=(8, 0))
        self.base_button = NeonButton(card, text="Seleccionar archivo base", command=self._choose_base)
        self.base_button.pack(anchor="w", pady=(8, 0))
        ttk.Label(card, text="Opcional. Se conservan el archivo original y sus recursos.\nDesactivado: se crea un KML/KMZ nuevo.", style="Hint.TLabel", wraplength=450).pack(anchor="w", pady=(8, 0))
        ttk.Label(card, text="Color de circunferencias", style="White.TLabel").pack(anchor="w", pady=(12, 4))
        ttk.Combobox(card, textvariable=self.vars["color"], values=tuple(COLORS), state="readonly", width=16).pack(anchor="w")

        card = ttk.LabelFrame(output, text="Uso portable", padding=12)
        card.pack(fill="x")
        ttk.Label(card, text="El EXE compilado se abre con doble clic.\nLos usuarios no necesitan Python ni conexion a internet.\nPuedes guardar y cargar proyectos para repetir una configuracion.", style="Hint.TLabel", wraplength=450).pack(anchor="w")

        preview = ttk.Frame(content, style="White.TFrame", padding=15)
        preview.grid(row=0, column=1, sticky="nsew")
        ttk.Label(preview, text="Vista de las rutas", style="White.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(preview, text="Esquema UTM · Norte hacia arriba", style="Hint.TLabel").pack(anchor="w", pady=(3, 12))
        self.canvas = tk.Canvas(preview, background=FIELD, bd=0, highlightthickness=1, highlightbackground="#28425d", width=420, height=330)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda event: self._schedule_draw())
        legend = ttk.Frame(preview, style="White.TFrame", padding=(0, 10))
        legend.pack(fill="x")
        ttk.Label(legend, text="● Corriente / pozo", foreground=TONES["cyan"], style="White.TLabel").pack(side="left")
        ttk.Label(legend, text="● Potencial", foreground=TONES["green"], style="White.TLabel").pack(side="right")
        ttk.Label(preview, textvariable=self.stats, style="White.TLabel", justify="left", font=("Segoe UI", 10), wraplength=410).pack(anchor="w", pady=(0, 10))
        NeonButton(preview, text="Validar y actualizar vista", command=self._validate).pack(fill="x")

        bottom = ttk.Frame(self, padding=(18, 6, 18, 12))
        bottom.pack(fill="x")
        self.generate_button = NeonButton(bottom, text="Generar archivos", style="Accent.TButton", command=self._generate)
        self.generate_button.pack(side="right")
        self.open_button = NeonButton(bottom, text="Abrir resultados", command=self._open_results, state="disabled", tone="purple")
        self.open_button.pack(side="right", padx=8)
        ttk.Label(bottom, textvariable=self.status, wraplength=590, foreground=MUTED).pack(side="left", fill="x", expand=True)
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", side="bottom")

    def _field(self, parent, label, key, row):
        ttk.Label(parent, text=label, style="White.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
        entry = ttk.Entry(parent, textvariable=self.vars[key])
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        return entry

    def _scroll_tab(self):
        panel = ttk.Frame(self.tabs, style="White.TFrame")
        canvas = tk.Canvas(panel, background=PANEL, width=470, highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        form = ttk.Frame(canvas, style="White.TFrame", padding=15)
        window = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        return panel, form

    def _apply(self, cfg):
        for key, value in cfg.to_dict().items():
            self.vars[key].set(value)
        self.vars["output_dir"].set(cfg.output_dir or str(portable_dir() / "Resultados"))
        self.hemisphere.set("Sur" if cfg.hemisphere == "south" else "Norte")
        self.direction_text.configure(state="normal")
        self.direction_text.delete("1.0", "end")
        self.direction_text.insert("1.0", cfg.potential_points)
        self._toggle_direction()
        self._toggle_base()
        self.last_config = cfg
        self._draw()

    def _collect(self, *, check_files=False):
        values = {key: var.get() for key, var in self.vars.items()}
        values["potential_points"] = self.direction_text.get("1.0", "end").strip()
        values["hemisphere"] = "south" if self.hemisphere.get() == "Sur" else "north"
        if values["output_dir"].strip() == str(portable_dir() / "Resultados"):
            values["output_dir"] = ""
        cfg = Settings.from_dict(values)
        cfg.validate(check_files=check_files)
        return cfg

    def _toggle_direction(self):
        enabled = self.vars["same_direction"].get()
        self.switch_label.set("ON · Usa corriente; la lista de potencial se ignora" if enabled else "OFF · Cada par de la lista define una ruta")
        self.direction_text.configure(state="disabled" if enabled else "normal", background="#162334" if enabled else FIELD)

    def _toggle_base(self):
        state = "normal" if self.vars["use_base"].get() else "disabled"
        self.base_entry.configure(state=state)
        self.base_button.configure(state=state)

    def _choose_output(self):
        path = filedialog.askdirectory(title="Carpeta para guardar resultados", parent=self)
        if path:
            self.vars["output_dir"].set(path)

    def _choose_base(self):
        path = filedialog.askopenfilename(title="Seleccionar base de Google Earth", filetypes=[("Google Earth", "*.kml *.kmz"), ("Todos los archivos", "*.*")], parent=self)
        if path:
            self.vars["base_file"].set(path)

    def _validate(self):
        try:
            cfg = self._collect()
            self.last_config = cfg
            self._draw()
            self.status.set(f"Configuracion valida: {cfg.point_count} puntos y {len(cfg.directions())} direcciones de potencial.")
            return cfg
        except Exception as exc:
            messagebox.showerror("Revisa la configuracion", str(exc), parent=self)
            return None

    def _schedule_draw(self):
        if self.preview_job is not None:
            self.after_cancel(self.preview_job)
        self.preview_job = self.after(100, self._draw)

    def _draw(self):
        self.preview_job = None
        if self.last_config is None:
            return
        cfg = self.last_config
        geometry = preview_geometry(cfg)
        canvas = self.canvas
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 100), max(canvas.winfo_height(), 100)
        cx, cy = width / 2, height / 2
        radius = min(width, height) * .37
        scale = radius / cfg.distance
        def xy(point):
            return cx + point[0] * scale, cy - point[1] * scale
        for p in cfg.percentages_list:
            if p == 0:
                continue
            r = radius * p / 100
            color = COLORS[cfg.color][1]
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=2 if p == 100 or p == 61.8 else 1, dash=() if p == 100 else (2, 4))
        canvas.create_text(width - 19, 17, text="N ↑", fill=MUTED, font=("Segoe UI", 10, "bold"))
        canvas.create_text(cx + radius + 2, cy + 13, text="100%", fill=MUTED, font=("Segoe UI", 8))
        for route in geometry["routes"]:
            end = xy(route["end"])
            canvas.create_line(cx, cy, *end, fill=TONES["green"], width=2)
            for e, n, p in route["points"]:
                x, y = xy((e, n))
                size = 3 if p == 61.8 else 2
                canvas.create_oval(x-size, y-size, x+size, y+size, fill=TONES["green"], outline=FIELD)
            if route["ray"] == 0:
                canvas.create_text(end[0], end[1] - 11, text=f'{route["name"]} · {cfg.final_percent:g}%', fill=TONES["green"], font=("Segoe UI", 8, "bold"))
        current = xy(geometry["current"])
        canvas.create_line(cx, cy, *current, fill=TONES["cyan"], width=3)
        canvas.create_oval(current[0]-5, current[1]-5, current[0]+5, current[1]+5, fill=TONES["cyan"], outline=FIELD, width=2)
        canvas.create_text(current[0], current[1]+15, text="Pozo auxiliar", fill=TONES["cyan"], font=("Segoe UI", 8, "bold"))
        canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=INK, outline=FIELD)
        canvas.create_text(cx, cy+13, text="Origen", fill=INK, font=("Segoe UI", 8))
        self.stats.set(f"Pozo auxiliar: 100% · {cfg.distance:g} m\nFin de potencial: {cfg.final_percent:g}% · {cfg.distance * cfg.final_percent / 100:g} m\n{len(cfg.directions())} direcciones · {2 * cfg.potential_rays + 1} rectas por direccion\n{cfg.point_count} puntos de salida · UTM {cfg.zone} {'Sur' if cfg.hemisphere == 'south' else 'Norte'}")

    def _save(self):
        cfg = self._validate()
        if cfg is None:
            return
        path = filedialog.asksaveasfilename(title="Guardar proyecto", defaultextension=".json", initialfile=f"{cfg.project}.json", filetypes=[("Proyecto SPT Go", "*.json")], parent=self)
        if path:
            try:
                save_settings(Path(path), cfg)
                self.status.set(f"Proyecto guardado: {Path(path).name}")
            except Exception as exc:
                messagebox.showerror("No se pudo guardar", str(exc), parent=self)

    def _load(self):
        path = filedialog.askopenfilename(title="Cargar proyecto", filetypes=[("Proyecto SPT Go", "*.json")], parent=self)
        if path:
            try:
                self._apply(load_settings(Path(path)))
                self.status.set(f"Proyecto cargado: {Path(path).name}")
            except Exception as exc:
                messagebox.showerror("No se pudo cargar", str(exc), parent=self)

    def _generate(self):
        if self.busy:
            return
        try:
            cfg = self._collect(check_files=True)
        except Exception as exc:
            messagebox.showerror("Revisa la configuracion", str(exc), parent=self)
            return
        self.last_config = cfg
        self._draw()
        self.busy = True
        self.generate_button.configure(state="disabled")
        self.progress.start(12)
        self.status.set("Generando Excel, KML y KMZ...")
        try:
            save_settings(self.profile_path, cfg)
        except OSError:
            pass  # La generacion puede continuar en otra carpeta elegida por el usuario.
        def work():
            try:
                self.events.put(("success", generate(cfg)))
            except Exception as exc:
                self.events.put(("error", str(exc), traceback.format_exc()))
        threading.Thread(target=work, daemon=True).start()

    def _poll(self):
        try:
            event = self.events.get_nowait()
        except queue.Empty:
            event = None
        if event:
            self.busy = False
            self.progress.stop()
            self.generate_button.configure(state="normal")
            if event[0] == "success":
                result = event[1]
                self.result_folder = result["folder"]
                self.open_button.configure(state="normal")
                self.status.set(f"Listo: {result['points']} puntos. Usa Abrir resultados para ver los archivos.")
                messagebox.showinfo("Archivos generados", "Se generaron Excel, KML y KMZ.\n\n" + result["folder"], parent=self)
            else:
                self.status.set("No se completo la generacion. Revisa el mensaje y vuelve a intentar.")
                messagebox.showerror("No se pudo generar", event[1], parent=self)
        self.after(100, self._poll)

    def _open_results(self):
        if not self.result_folder:
            return
        try:
            if sys.platform == "win32":
                os.startfile(self.result_folder)
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", self.result_folder])
        except Exception as exc:
            messagebox.showerror("No se pudo abrir la carpeta", str(exc), parent=self)

    def _help(self):
        messagebox.showinfo("SPT Go · Guia rapida", "1. Define proyecto, zona UTM y origen comun.\n2. Define un punto de direccion de corriente y la distancia al pozo.\n3. En Potencial activa ON para usar corriente, o deja OFF y agrega direcciones.\n4. Configura porcentajes y, opcionalmente, rayos laterales.\n5. Elige carpeta y genera los archivos.\n\nCorriente: solo Pozo auxiliar (C100%).\nPotencial: solo porcentajes menores al 100%, hasta el ultimo seleccionado.\nCircunferencias: incluye 100%.\n\nTodos los porcentajes usan la distancia al pozo auxiliar como base. La vista es esquematica; no incluye terreno ni obstaculos.\n\nVersion " + VERSION, parent=self)

    def _close(self):
        if self.busy:
            messagebox.showinfo("Generacion en curso", "Espera a que termine la generacion para cerrar la ventana.", parent=self)
            return
        try:
            save_settings(self.profile_path, self._collect())
        except Exception:
            pass
        self.destroy()


def main():
    if "--self-test" in sys.argv:
        from spt_selftest import run_self_test
        report = None
        if "--report" in sys.argv:
            position = sys.argv.index("--report") + 1
            if position < len(sys.argv):
                report = Path(sys.argv[position])
        return run_self_test(report, check_gui=(sys.platform == "win32"))
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    app = Application()
    app.mainloop()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        try:
            messagebox.showerror("SPT Go", f"No se pudo iniciar la aplicacion.\n\n{exc}")
        except Exception:
            if sys.stderr is not None:
                traceback.print_exc()
        raise SystemExit(1)
