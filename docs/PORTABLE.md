# Ejecución portable

Descarga el EXE oficial o el ZIP de la [Release](https://github.com/Majuel20/SPT-Go-Portable/releases/latest). Para comprobar integridad en PowerShell ejecuta `Get-FileHash .\SPT_Go-Portable.exe -Algorithm SHA256` y compara el valor con `SHA256SUMS` de la misma Release.

No se necesita instalar Python, usar comandos ni conectarse a internet para el trabajo local. PyInstaller OneFile extrae bibliotecas y recursos en una carpeta temporal durante cada inicio. La aplicación también escribe configuraciones y resultados. Si la carpeta del EXE permite escritura, allí se crean `SPT_Go_config.json` y `Resultados`. Si no, se usa `%LOCALAPPDATA%\SPT Go Portable` (incluida la carpeta `Resultados`). Puedes elegir otra carpeta de salida en la interfaz. Los proyectos antiguos en la carpeta del EXE se siguen leyendo.

No se requieren permisos de administrador para el uso normal. En carpetas administradas pueden existir políticas que bloqueen la ejecución. El EXE no está firmado; SmartScreen puede advertir que el editor es desconocido. Verifica origen y suma. No desactives protecciones del sistema.
