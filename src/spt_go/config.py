"""Configuracion y geometria UTM sin dependencias externas."""
from __future__ import annotations

import json
import math
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from ._version import VERSION

APP_NAME = "SPT Go Portable"
AUTHOR = "Majuel20"
BYLINE = f"By: {AUTHOR}"
COLORS = {
    "Rojo": (1, "#dc2626"), "Naranja": (2, "#ea580c"),
    "Amarillo": (3, "#ca8a04"), "Verde": (4, "#16a34a"),
    "Celeste": (5, "#0891b2"), "Azul": (6, "#2563eb"),
    "Magenta": (7, "#c026d3"), "Morado": (8, "#7c3aed"),
    "Blanco": (9, "#94a3b8"), "Gris": (10, "#64748b"),
}


def portable_dir() -> Path:
    """Archivos del usuario junto al EXE, nunca en la extraccion temporal."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def writable_dir(path: Path) -> bool:
    """Comprueba escritura real sin dejar archivos de prueba."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=path):
            pass
        return True
    except OSError:
        return False


def user_data_dir() -> Path:
    """Prefiere modo portable; usa datos locales si la carpeta del EXE es protegida."""
    base = portable_dir()
    if writable_dir(base):
        return base
    fallback = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "SPT Go Portable"
    if writable_dir(fallback):
        return fallback
    raise OSError(f"No se puede escribir en {base} ni en {fallback}. Elige una carpeta con permisos de escritura.")


def default_output_dir() -> Path:
    return user_data_dir() / "Resultados"


def number(value, label: str) -> float:
    try:
        result = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}: escribe un numero valido.") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label}: el numero debe ser finito.")
    return result


def integer(value, label: str) -> int:
    result = number(value, label)
    if not result.is_integer():
        raise ValueError(f"{label}: escribe un numero entero.")
    return int(result)


def parse_percentages(text: str) -> list[float]:
    tokens = [item for item in re.split(r"[;\s]+", text.strip()) if item]
    if not tokens:
        raise ValueError("Agrega los porcentajes separados por punto y coma (;).")
    return [number(item, "Porcentaje (separa los valores con ;)") for item in tokens]


@dataclass
class Settings:
    project: str = "SPT_EJEMPLO"
    zone: int = 17
    hemisphere: str = "south"
    origin_e: float = 550364.26
    origin_n: float = 9422280.20
    current_e: float = 552873.71
    current_n: float = 9421133.69
    distance: float = 2300.0
    same_direction: bool = False
    potential_points: str = "552878.84, 9423290.72;"
    potential_rays: int = 0
    ray_separation: float = 5.0
    percentages: str = "0; 10; 20; 30; 40; 50; 52; 60; 61.8; 70; 72; 80; 90; 100"
    color: str = "Celeste"
    use_base: bool = False
    base_file: str = ""
    output_dir: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        if not isinstance(data, dict):
            raise ValueError("La configuracion debe ser un objeto JSON.")
        known = {f.name for f in fields(cls)}
        cfg = cls(**{k: v for k, v in data.items() if k in known})
        for key, label in (("zone", "Zona UTM"), ("potential_rays", "Rayos laterales")):
            setattr(cfg, key, integer(getattr(cfg, key), label))
        for key in ("origin_e", "origin_n", "current_e", "current_n", "distance", "ray_separation"):
            setattr(cfg, key, number(getattr(cfg, key), key))
        for key in ("same_direction", "use_base"):
            if not isinstance(getattr(cfg, key), bool):
                raise ValueError(f"{key}: el valor debe ser verdadero o falso.")
        for key in ("project", "hemisphere", "potential_points", "percentages", "color", "base_file", "output_dir"):
            if not isinstance(getattr(cfg, key), str):
                raise ValueError(f"{key}: el valor debe ser texto.")
        cfg.project = cfg.project.strip()
        cfg.validate()
        return cfg

    def to_dict(self) -> dict:
        return asdict(self)

    def validate(self, *, check_files: bool = False) -> None:
        if not self.project.strip() or len(self.project) > 80:
            raise ValueError("El nombre del proyecto debe tener entre 1 y 80 caracteres.")
        if not all(c.isalnum() or c in " _-" for c in self.project):
            raise ValueError("En el proyecto usa letras, numeros, espacios, guion o guion bajo.")
        if self.project.strip().upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
            raise ValueError("El nombre del proyecto esta reservado por Windows. Usa otro nombre.")
        if not 1 <= self.zone <= 60:
            raise ValueError("La zona UTM debe estar entre 1 y 60.")
        if self.hemisphere not in {"south", "north"}:
            raise ValueError("Selecciona hemisferio Sur o Norte.")
        if not all(math.isfinite(v) for v in (self.origin_e, self.origin_n, self.current_e, self.current_n, self.distance, self.ray_separation)):
            raise ValueError("Las coordenadas y distancias deben ser numeros finitos.")
        if self.distance <= 0:
            raise ValueError("La distancia al pozo auxiliar debe ser mayor que cero.")
        if (self.current_e, self.current_n) == (self.origin_e, self.origin_n):
            raise ValueError("El punto de direccion de corriente debe ser distinto del origen.")
        if not isinstance(self.potential_rays, int) or self.potential_rays < 0:
            raise ValueError("Los rayos laterales deben ser un entero mayor o igual a cero.")
        if self.ray_separation < 0 or (self.potential_rays > 0 and self.ray_separation == 0):
            raise ValueError("Si activas rayos laterales, la separacion debe ser mayor que cero.")
        values = parse_percentages(self.percentages)
        if any(not 0 <= p <= 100 for p in values):
            raise ValueError("Los porcentajes deben estar entre 0 y 100.")
        if len(set(values)) != len(values):
            raise ValueError("La lista de porcentajes tiene valores repetidos.")
        if 100 not in values:
            raise ValueError("Incluye 100 para el pozo auxiliar y su circunferencia.")
        if not any(p < 100 for p in values):
            raise ValueError("Incluye al menos un porcentaje menor al 100 para potencial.")
        if self.color not in COLORS:
            raise ValueError("Selecciona un color de circunferencias.")
        self.directions()
        if check_files and self.use_base:
            path = Path(self.base_file).expanduser()
            if not self.base_file.strip() or not path.is_file():
                raise ValueError("Selecciona un archivo base KML/KMZ existente, o desactiva esa opcion.")
            if path.suffix.lower() not in {".kml", ".kmz"}:
                raise ValueError("El archivo base debe ser KML o KMZ.")

    def directions(self) -> list[tuple[float, float]]:
        if self.same_direction:
            return [(self.current_e, self.current_n)]
        points = []
        for item in self.potential_points.strip().split(";"):
            item = item.strip()
            if not item:
                continue
            parts = [part.strip() for part in item.split(",")]
            if len(parts) != 2:
                raise ValueError("Cada direccion de potencial debe ser Este, Norte; usa punto decimal.")
            e, n = (number(parts[0], "Este de potencial"), number(parts[1], "Norte de potencial"))
            if (e, n) == (self.origin_e, self.origin_n):
                raise ValueError("No repitas el origen en potencial. Escribe solo los puntos de direccion.")
            points.append((e, n))
        if not points:
            raise ValueError("En OFF debes agregar al menos una direccion de potencial.")
        return points

    @property
    def percentages_list(self) -> list[float]:
        return sorted(parse_percentages(self.percentages))

    @property
    def potential_percentages(self) -> list[float]:
        return [p for p in self.percentages_list if p < 100]

    @property
    def final_percent(self) -> float:
        return max(self.potential_percentages)

    @property
    def root_output(self) -> Path:
        return Path(self.output_dir).expanduser().resolve() if self.output_dir.strip() else default_output_dir()

    @property
    def point_count(self) -> int:
        return 1 + len(self.directions()) * (2 * self.potential_rays + 1) * len(self.potential_percentages)


def unit_direction(origin, end):
    dx, dy = end[0] - origin[0], end[1] - origin[1]
    distance = math.hypot(dx, dy)
    if not distance:
        raise ValueError("La direccion coincide con el origen.")
    return dx / distance, dy / distance


def preview_geometry(cfg: Settings) -> dict:
    """Distancias locales desde el origen, iguales a las del generador."""
    origin = (cfg.origin_e, cfg.origin_n)
    ux, uy = unit_direction(origin, (cfg.current_e, cfg.current_n))
    current = (ux * cfg.distance, uy * cfg.distance)
    routes = []
    for index, end in enumerate(cfg.directions(), 1):
        ux, uy = unit_direction(origin, end)
        for ray in range(-cfg.potential_rays, cfg.potential_rays + 1):
            offset = ray * cfg.ray_separation
            dx, dy = ux * cfg.distance - uy * offset, uy * cfg.distance + ux * offset
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            points = [(dx * cfg.distance * p / 100, dy * cfg.distance * p / 100, p) for p in cfg.potential_percentages]
            routes.append({"name": f"L{index}", "ray": ray, "points": points, "end": (dx * cfg.distance * cfg.final_percent / 100, dy * cfg.distance * cfg.final_percent / 100)})
    return {"current": current, "routes": routes}


def save_settings(path: Path, cfg: Settings) -> None:
    """Guarda el proyecto de forma atómica en la misma carpeta de destino."""
    payload = json.dumps({"schema": "spt-go", "version": 1, "settings": cfg.to_dict()}, ensure_ascii=False, indent=2)
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".spt_config_", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_settings(path: Path) -> Settings:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    # Se conservan los proyectos JSON de las versiones anteriores.
    if not isinstance(payload, dict) or payload.get("schema") not in {"spt-go", "spat-ssee"} or payload.get("version") != 1:
        raise ValueError("Este archivo no es una configuracion compatible de SPT Go.")
    return Settings.from_dict(payload.get("settings"))
