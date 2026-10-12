# SPT Go Portable

**By: Majuel20** · Planificación de rutas de medición de sistemas de puesta a tierra en subestaciones eléctricas.

**[Descargar la última Release](https://github.com/Majuel20/SPT-Go-Portable/releases/latest)** · Windows 10/11 x64 (destino de distribución; valida el EXE en tu equipo antes del trabajo de campo).

SPT Go Portable permite configurar un origen UTM común, la dirección de corriente y una o varias direcciones de potencial. Muestra una vista esquemática oscura/neón y genera Excel, KML, KMZ y un proyecto JSON recuperable. No requiere instalar Python ni acceder a internet para generar archivos desde el EXE.

## Empezar en tres pasos

1. Descarga `SPT_Go-Portable.exe` de la Release oficial. Si deseas guía y avisos legales, descarga el ZIP de distribución. Comprueba la suma con `SHA256SUMS`.
2. Abre el EXE con doble clic. Escribe zona UTM, hemisferio, origen, punto de dirección de corriente y distancia al pozo auxiliar.
3. Configura potencial y porcentajes, valida la vista y pulsa **Generar archivos**. Usa **Abrir resultados** para ver la carpeta nueva de esa ejecución.

El EXE no está firmado digitalmente; Windows SmartScreen puede mostrar una advertencia de editor desconocido. Verifica la procedencia y la suma SHA-256. No desactives el antivirus.

## Qué calcula

- **Corriente:** una ruta principal; el segundo punto define su dirección. La distancia indicada sitúa el único pozo auxiliar **C100%**.
- **Potencial:** en **ON**, usa la dirección de corriente; en **OFF**, cada par `Este, Norte;` define una ruta independiente desde el mismo origen. El abanico y la separación se aplican solo a potencial.
- **Porcentajes:** los valores menores al 100% crean puntos de potencial y la ruta acaba en el mayor de ellos. El 100% conserva la circunferencia de referencia y el pozo auxiliar de corriente.

Ejemplo: a 100 m con `0; 50; 61.8; 90; 100`, el pozo C100% está a 100 m y la ruta de potencial acaba a 90 m. La vista no muestra terreno ni obstáculos.

## Archivos y portabilidad

Cada generación crea una carpeta independiente con `*.xlsx`, `*.kml`, `*.kmz`, `Proyecto.json` y `Registro.txt`. El Excel incluye campos para mediciones y filtros de tabla sin filtros superpuestos. Se puede incorporar un KML/KMZ base sin modificar el original. Los proyectos JSON antiguos `spat-ssee` de versión 1 siguen siendo aceptados.

PyInstaller OneFile extrae recursos a una carpeta temporal al iniciar. Si la carpeta del EXE permite escritura, el perfil y los resultados predeterminados se guardan allí; de lo contrario, se usa `%LOCALAPPDATA%\SPT Go Portable`. El usuario puede elegir otra carpeta. Consulta la [guía portable](docs/PORTABLE.md).

## Guías

- [Uso paso a paso](docs/USUARIO.md) · [Coordenadas UTM](docs/COORDENADAS_UTM.md)
- [Formatos de salida](docs/FORMATOS.md) · [Preguntas frecuentes](docs/FAQ.md)
- [Compilación para desarrolladores](docs/COMPILACION.md) · [Arquitectura](docs/ARQUITECTURA.md) · [Publicar una versión](docs/RELEASES.md)

## Desarrollo

En Windows x64 con Python 3.11–3.13:

```powershell
py -3.12 -m venv .venv_spt_go
.\.venv_spt_go\Scripts\python.exe -m pip install -e . -r scripts\requirements-build.txt
.\.venv_spt_go\Scripts\python.exe -m unittest discover -s tests -v
.\.venv_spt_go\Scripts\python.exe -m spt_go
```

Para crear el EXE, usa `CREAR_EXE.bat` o `python scripts/build_windows.py` dentro del entorno. La compilación prueba el código y luego el EXE real. El workflow de GitHub permite compilar manualmente y descargar un artefacto. La publicación de una nueva Release requiere una ejecución manual explícita y una etiqueta nueva.

## Derechos, límites y seguridad

© 2026 Majuel20. **Código y recursos visuales con derechos reservados**; consulta [LICENSE](LICENSE) y [atribuciones](docs/LICENCIAS_Y_ATRIBUCIONES.md). Las bibliotecas incluidas mantienen sus licencias, cuyos avisos acompañan el ZIP. La aplicación no incorpora telemetría ni requiere red para operaciones locales; un KML/KMZ externo puede contener enlaces interpretados al abrirlo en otra aplicación.

La herramienta planifica coordenadas; no mide resistencia, certifica una puesta a tierra ni sustituye un procedimiento de ensayo, normas aplicables, verificación en campo o criterio profesional. Revisa zona, datum, rutas, obstáculos y seguridad antes de usar los resultados.
