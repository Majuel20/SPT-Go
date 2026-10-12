# Compilar en Windows

Usa Windows x64, Python 3.11–3.13 x64 con Tk y acceso a internet para instalar dependencias. Haz doble clic en `CREAR_EXE.bat` desde el código completo. El script crea `.venv_spt_go`, instala el proyecto y PyInstaller, ejecuta pruebas y deja resultados en `dist/`. El EXE final se llama directamente `SPT_Go-Portable.exe`; no hay renombrado posterior. `Compilacion.log` contiene la salida si falla.

Compilación manual equivalente:

```powershell
py -3.12 -m venv .venv_spt_go
.\.venv_spt_go\Scripts\python.exe -m pip install -e . -r scripts\requirements-build.txt
.\.venv_spt_go\Scripts\python.exe scripts\build_windows.py
```

El compilador verifica sintaxis y comportamiento mediante `unittest`, ejecuta el autotest con pyproj real y ventana Tk, construye OneFile con datos PROJ, logo e icono, comprueba que el archivo es PE x64 y repite el autotest desde el EXE. Solo entonces crea el ZIP y `SHA256SUMS`. No se necesita Python en el equipo que recibe el EXE.

El build local y GitHub Actions verifican Windows x64. La compatibilidad en todas las configuraciones de Windows 10/11, políticas corporativas y antivirus requiere comprobación manual adicional. Se recomienda probar en una máquina limpia con Windows 10 x64 y otra con Windows 11 x64, sin Python, ejecutando desde una carpeta común y una protegida.
