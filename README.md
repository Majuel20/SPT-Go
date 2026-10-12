# SPT Go

**By: Majuel20**

Aplicación de escritorio para preparar rutas y puntos de corriente y potencial de sistemas de puesta a tierra. Interfaz oscura, botones redondeados con acentos neón y el logo MK proporcionado como referencia.

Este repositorio contiene el **código fuente y la compilación automática**. Un `.py` o un ZIP del repositorio no es todavía el EXE. El EXE se genera en Windows, localmente o con GitHub Actions.

## Versión 1.0.2

El nombre de la aplicación es **SPT Go**, el repositorio recomendado es **SPT-Go** y el ejecutable es **SPT_Go.exe**. Conserva **By: Majuel20**, el diseño neón, el logo MK y la corrección de filtros duplicados de Excel. Los proyectos JSON de las versiones anteriores siguen siendo compatibles.

## Funciones

- Coordenadas UTM, zona, hemisferio, proyecto y distancia editables.
- Origen común para corriente, potencial y circunferencias.
- Corriente: una sola recta y un único **Pozo auxiliar (C100%)**.
- Potencial: puntos y trazos hasta el último porcentaje configurado menor al 100%.
- Se conserva la circunferencia del 100%.
- ON: usa la dirección de corriente e ignora la lista de potencial.
- OFF: cada par `Este, Norte;` define una dirección de potencial distinta.
- Abanico y separación solo para potencial.
- Vista esquemática UTM, carga y guardado de proyectos JSON.
- Excel con tablas, campos de medición y promedio automático; KML y KMZ.
- Integración opcional con una plantilla KML/KMZ, conservando sus recursos y su archivo original.
- Carpetas de resultados independientes por ejecución.

El segundo punto de corriente **define una dirección**; `Distancia al pozo (m)` determina la ubicación del pozo auxiliar. Los porcentajes se calculan sobre esa distancia.

## Crear el EXE en tu PC

1. Descomprime el paquete completo en una carpeta de Windows.
2. Si no tienes Python compatible, instala **Python 3.12 de 64 bits** desde [python.org](https://www.python.org/downloads/windows/). Incluye Tcl/Tk y activa `Add python.exe to PATH`. El compilador también admite Python 3.11 y 3.13 de 64 bits.
3. Haz doble clic en `CREAR_EXE.bat`. La primera compilación necesita internet para descargar las dependencias.
4. Espera a que finalicen las pruebas y la compilación.
5. Abre la carpeta `dist`:
   - `SPT_Go.exe`: ejecutable portable.
   - `SPT_Go_Para_Regalar.zip`: paquete listo para distribuir.

Los destinatarios del EXE no necesitan Python ni instalar las bibliotecas. La conversión WGS84/UTM usa los datos PROJ incluidos; no necesita internet durante el uso.

Si falla la compilación, revisa `Compilacion.log` y los archivos `build/Verificacion_*.json`. El proceso no anuncia un EXE listo si sus verificaciones fallan.

## Crear el EXE desde GitHub

El flujo `.github/workflows/crear-exe-windows.yml` compila y prueba en un equipo Windows de GitHub. No necesitas compilar en tu PC si utilizas esta opción.

1. Crea o abre el repositorio de destino.
2. Sube **el contenido de esta carpeta a la raíz del repositorio**, incluida la carpeta `.github`. No coloques todo dentro de una carpeta adicional: el flujo espera los archivos en la raíz.
3. Usa la rama `main` o `master`. La compilación se inicia al subir los cambios. También puedes iniciarla en **Actions → Crear EXE Windows → Run workflow**.
4. Espera a que el flujo termine correctamente.
5. Abre la ejecución y descarga el artefacto **SPT-Go-Windows-x64**.
6. Dentro encontrarás el EXE y `SPT_Go_Para_Regalar.zip`.

Los artefactos del flujo se conservan durante 30 días. Para ofrecer una descarga en **Releases**, sube una etiqueta de versión nueva como `v1.0.2`. El flujo compilará, verificará y publicará los archivos de esa etiqueta. También puedes descargar el artefacto y crear la Release manualmente desde GitHub, adjuntando el EXE y el ZIP para regalar. Si la Release ya existe, el flujo la conserva y termina correctamente. Usa una etiqueta nueva para cada versión.

```bash
git tag v1.0.2
git push origin v1.0.2
```

Sube el código, los recursos y el flujo; no subas `.venv_spt_go`, `build`, `dist` ni configuraciones personales. El `.gitignore` ya contempla esas carpetas.

## Probar desde el código

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python SPT_Go.py
```

La prueba completa de generación y proyección real es:

```bash
python SPT_Go.py --self-test --report Verificacion_SPT_Go.json
```

En Windows también verifica la creación de la ventana, el logo y los controles. `build_windows.py` ejecuta la prueba antes y después de compilar, con la aplicación ya empaquetada.

## Verificación de esta entrega

La preparación del proyecto se realizó en Linux, sin un compilador Windows ni una pantalla Tk disponible. No se incluye un `.exe` ya compilado. Las pruebas locales comprueban la configuración, la geometría UTM, la persistencia y los exportadores con una proyección simulada. La conversión geográfica real y la ventana del EXE se comprobarán en Windows mediante las pruebas automáticas incluidas.

## Estructura

| Archivo | Función |
|---|---|
| `SPT_Go.py` | Ventana y botones neón |
| `spt_config.py` | Configuración, validación y geometría de la vista |
| `spt_service.py` | Conexión entre la ventana y el motor |
| `spt_motor.py` | Generación de puntos, Excel, KML y KMZ |
| `spt_selftest.py` | Prueba integral con pyproj real |
| `build_windows.py` | Compilación, verificación y paquete para regalar |
| `CREAR_EXE.bat` | Compilación con doble clic en Windows |
| `app.ico`, `logo.png` | Logo MK del material de referencia |
| `.github/workflows/crear-exe-windows.yml` | Compilación y publicación por etiqueta |

El material `MVideoDk.zip` se utilizó como referencia visual. No se copian su servidor, componentes de descargas, túneles, tokens ni otros módulos funcionales. El ejecutable de esta aplicación no incorpora esos componentes.

## Documentación de las herramientas

- [PyInstaller: ejecutables de un archivo y requisitos de plataforma](https://pyinstaller.org/en/stable/operating-mode.html).
- [PyInstaller: rutas durante la ejecución empaquetada](https://pyinstaller.org/en/stable/runtime-information.html).
- [pyproj: instalación y datos de PROJ](https://pyproj4.github.io/pyproj/stable/installation.html).
- [GitHub: artefactos de los flujos](https://docs.github.com/en/actions/tutorials/store-and-share-data).

Los avisos de las dependencias se recopilan al compilar y acompañan el paquete de distribución.
