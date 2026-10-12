"""Compila, prueba y prepara el paquete para distribuir desde Windows."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command):
    print("Ejecutando:", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def assert_report(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("passed"):
        raise RuntimeError(data.get("error") or "La verificacion no fue satisfactoria.")


def collect_licenses(destination):
    texts = []
    for name in ("pandas", "numpy", "openpyxl", "et_xmlfile", "pyproj", "certifi", "pyinstaller", "pyinstaller-hooks-contrib"):
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            continue
        texts.append(f"\n{'=' * 70}\n{name} {distribution.version}\n{'=' * 70}\n")
        for file in distribution.files or []:
            filename = str(file).replace("\\", "/")
            if file.name.upper().startswith(("LICENSE", "COPYING", "NOTICE")) and (".dist-info/" in filename or name == "pyproj"):
                source = Path(distribution.locate_file(file))
                if source.is_file():
                    texts.append(f"\n{file}\n" + source.read_text(encoding="utf-8", errors="replace"))
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.is_file():
        texts.append("\nPython y componentes incluidos\n" + python_license.read_text(encoding="utf-8", errors="replace"))
    destination.write_text("\n".join(texts), encoding="utf-8")


def main():
    if sys.platform != "win32":
        raise RuntimeError("Este compilador se ejecuta en Windows para producir un EXE de Windows.")
    if sys.maxsize <= 2**32 or not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise RuntimeError("Usa Python de 64 bits, preferentemente version 3.12 (compatible: 3.11 a 3.13).")
    work = ROOT / "build"
    work.mkdir(exist_ok=True)
    source_report = work / "Verificacion_codigo.json"
    run([sys.executable, ROOT / "SPT_Go.py", "--self-test", "--report", source_report])
    assert_report(source_report)
    licenses = work / "Licencias_terceros.txt"
    collect_licenses(licenses)
    staging_dist = work / "salida_exe"
    run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed", "--noupx",
        "--name", "SPT_Go", "--icon", ROOT / "app.ico", "--version-file", ROOT / "version_info.txt",
        "--collect-all", "pyproj", "--add-data", f"{licenses}:.",
        "--add-data", f"{ROOT / 'logo.png'}:.", "--add-data", f"{ROOT / 'app.ico'}:.",
        "--distpath", staging_dist, "--workpath", work / "pyinstaller", "--specpath", work,
        ROOT / "SPT_Go.py",
    ])
    exe = staging_dist / "SPT_Go.exe"
    if not exe.is_file() or exe.read_bytes()[:2] != b"MZ":
        raise RuntimeError("PyInstaller no genero un ejecutable de Windows valido.")
    exe_report = work / "Verificacion_exe.json"
    run([exe, "--self-test", "--report", exe_report])
    assert_report(exe_report)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    final_exe = dist / exe.name
    shutil.copy2(exe, final_exe)
    shutil.copy2(ROOT / "GUIA_USO.txt", dist / "GUIA_USO.txt")
    shutil.copy2(ROOT / "NOTAS_RELEASE.md", dist / "NOTAS_RELEASE.md")
    shutil.copy2(licenses, dist / licenses.name)
    shutil.copy2(exe_report, dist / exe_report.name)
    frozen = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (dist / "Versiones_compilacion.txt").write_text(frozen, encoding="utf-8")
    checksum = hashlib.sha256(final_exe.read_bytes()).hexdigest()
    (dist / "SHA256.txt").write_text(f"{checksum}  {final_exe.name}\n", encoding="utf-8")
    gift = dist / "SPT_Go_Para_Regalar.zip"
    with zipfile.ZipFile(gift, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in (final_exe, dist / "GUIA_USO.txt", dist / licenses.name, dist / "SHA256.txt"):
            archive.write(file, file.name)
    print("LISTO: EXE probado y paquete para regalar en", dist, flush=True)


if __name__ == "__main__":
    main()
