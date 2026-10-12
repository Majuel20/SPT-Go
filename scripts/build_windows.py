"""Compila y verifica el ejecutable Windows antes de crear entregables."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import shutil
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from spt_go._version import VERSION

ROOT = Path(__file__).resolve().parents[1]
NAME = "SPT_Go-Portable.exe"


def run(*command: object) -> None:
    subprocess.run([str(part) for part in command], cwd=ROOT, check=True)


def assert_report(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("passed"):
        raise RuntimeError(data.get("error") or f"Falló la verificación {path}")


def assert_windows_x64(path: Path) -> None:
    with path.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise RuntimeError("El archivo no es un ejecutable PE.")
        stream.seek(0x3c)
        stream.seek(struct.unpack("<I", stream.read(4))[0])
        if stream.read(4) != b"PE\0\0" or struct.unpack("<H", stream.read(2))[0] != 0x8664:
            raise RuntimeError("El ejecutable no es PE x64.")


def version_info() -> str:
    numbers = tuple(int(part) for part in VERSION.split(".")) + (0,)
    return f'''VSVersionInfo(
  ffi=FixedFileInfo(filevers={numbers}, prodvers={numbers}, mask=0x3f,
    flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('FileDescription', 'SPT Go Portable - By: Majuel20'),
    StringStruct('CompanyName', 'Majuel20'),
    StringStruct('FileVersion', '{VERSION}'),
    StringStruct('InternalName', 'SPT_Go-Portable'),
    StringStruct('OriginalFilename', '{NAME}'),
    StringStruct('ProductName', 'SPT Go Portable'),
    StringStruct('ProductVersion', '{VERSION}')
  ])]), VarFileInfo([VarStruct('Translation', [1033, 1200])])]
)'''


def collect_notices(destination: Path) -> None:
    """Incluye avisos presentes en las distribuciones instaladas, con versión."""
    sections = []
    for name in ("pandas", "numpy", "openpyxl", "et_xmlfile", "pyproj", "certifi"):
        dist = importlib.metadata.distribution(name)
        texts = []
        for file in dist.files or []:
            filename = str(file).replace("\\", "/")
            if file.name.upper().startswith(("LICENSE", "LICENCE", "COPYING", "NOTICE")) and (".dist-info/" in filename or name == "pyproj"):
                source = Path(dist.locate_file(file))
                if source.is_file():
                    texts.append(f"\n{filename}\n" + source.read_text(encoding="utf-8", errors="replace"))
        if not texts:
            raise RuntimeError(f"No se encontró aviso de licencia para {name} {dist.version}.")
        sections.append(f"\n{'=' * 70}\n{name} {dist.version}\n{'=' * 70}\n" + "\n".join(texts))
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise RuntimeError("No se encontró LICENSE.txt de Python para la distribución.")
    sections.append("\nPython\n" + python_license.read_text(encoding="utf-8", errors="replace"))
    tk_license = Path(sys.base_prefix) / "tcl" / "tk8.6" / "license.terms"
    if tk_license.is_file():
        sections.append("\nTk 8.6\n" + tk_license.read_text(encoding="utf-8", errors="replace"))
    destination.write_text("AVISOS DE COMPONENTES DE TERCEROS\n" + "\n".join(sections), encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if sys.platform != "win32" or sys.maxsize <= 2**32:
        raise RuntimeError("Compila en Windows x64 con Python x64.")
    if not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise RuntimeError("Usa Python 3.11–3.13 de 64 bits.")
    work = ROOT / "build"
    work.mkdir(exist_ok=True)
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    source_report = work / "Verificacion_codigo.json"
    run(sys.executable, "-m", "spt_go", "--self-test", "--report", source_report)
    assert_report(source_report)
    metadata = work / "version_info.txt"
    metadata.write_text(version_info(), encoding="utf-8")
    notices = work / "AVISOS_TERCEROS.txt"
    collect_notices(notices)
    assets = ROOT / "src" / "spt_go" / "assets"
    staging = work / "salida_exe"
    run(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile",
        "--windowed", "--noupx", "--name", "SPT_Go-Portable", "--icon", assets / "app.ico",
        "--version-file", metadata, "--collect-all", "pyproj",
        "--add-data", f"{assets};spt_go/assets", "--add-data", f"{notices};.",
        "--distpath", staging, "--workpath", work / "pyinstaller", "--specpath", work,
        ROOT / "scripts" / "entry.py")
    exe = staging / NAME
    assert_windows_x64(exe)
    exe_report = work / "Verificacion_exe.json"
    run(exe, "--self-test", "--report", exe_report)
    assert_report(exe_report)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    final_exe = dist / NAME
    shutil.copy2(exe, final_exe)
    shutil.copy2(ROOT / "docs" / "GUIA_USO.txt", dist / "GUIA_USO.txt")
    shutil.copy2(ROOT / "LICENSE", dist / "LICENSE.txt")
    shutil.copy2(notices, dist / notices.name)
    shutil.copy2(ROOT / "docs" / f"NOTAS_RELEASE_v{VERSION}.md", dist / "NOTAS_PUBLICACION.md")
    archive_path = dist / "SPT_Go_Portable_Windows_x64.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (final_exe, dist / "GUIA_USO.txt", dist / "LICENSE.txt", dist / notices.name):
            archive.write(path, path.name)
    (dist / "SHA256SUMS").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in (final_exe, archive_path)), encoding="ascii")
    print(f"EXE verificado: {final_exe}", flush=True)


if __name__ == "__main__":
    main()
