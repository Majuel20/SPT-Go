# SPT Go Portable v1.0.3

**By: Majuel20**

Esta versión reorganiza el proyecto sin alterar la lógica técnica de rutas de corriente y potencial. El ejecutable se genera directamente como **`SPT_Go-Portable.exe`**.

## Cambios

- Código importable en `src/spt_go/`, documentación y pruebas automatizadas en el repositorio.
- Compilación Windows x64 con PyInstaller OneFile, inclusión de datos PROJ, logo e icono, y autotest del EXE real.
- Configuración JSON guardada de forma atómica. Si la carpeta del EXE no permite escritura, se usa `%LOCALAPPDATA%\SPT Go Portable` para el perfil y los resultados predeterminados.
- Compatibilidad de lectura con proyectos JSON antiguos; se conservan la interfaz oscura/neón, By: Majuel20, Excel, KML y KMZ.
- ZIP de distribución con guía, licencia y avisos de terceros; `SHA256SUMS` para verificar la descarga.

## Descargas

- `SPT_Go-Portable.exe`: aplicación para Windows x64, sin instalación de Python.
- `SPT_Go_Portable_Windows_x64.zip`: EXE, guía de uso, licencia y avisos de terceros.
- `SHA256SUMS`: sumas del EXE y del ZIP.
- `AVISOS_TERCEROS.txt`: licencias de componentes incluidos.

La generación local no necesita internet. OneFile extrae archivos temporalmente al iniciar y la aplicación escribe configuraciones y resultados en la carpeta elegida. El EXE no está firmado digitalmente; verifica su origen y SHA-256 si Windows muestra una advertencia de editor desconocido. No desactives mecanismos de seguridad.

**Alcance de verificación:** se probó la compilación y ejecución en Windows 11 x64 y en el runner Windows x64 de GitHub Actions. La ejecución manual en Windows 10 x64 y en equipos con políticas corporativas queda pendiente. La herramienta planifica puntos de ensayo; no sustituye mediciones, normas aplicables ni revisión profesional en campo.
