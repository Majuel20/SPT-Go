# Arquitectura técnica

`config.py` define la configuración, valida entradas y calcula la geometría de la vista. `gui.py` mantiene la ventana Tk oscura/neón y delega la generación a `service.py` en un hilo. `service.py` conecta la configuración con `motor.py`, que conserva la lógica de corriente, potencial, Excel y KML/KMZ de v1.0.2. `selftest.py` ejecuta una prueba de extremo a extremo tanto desde Python como desde el EXE. `_version.py` es la única fuente de versión: `pyproject.toml` y los metadatos PE la leen.

El motor heredado usa parámetros de módulo configurados por el servicio. La interfaz impide generaciones simultáneas; el servicio no es seguro para llamadas concurrentes externas. Refactorizar este estado requeriría pruebas de equivalencia geométrica y se deja fuera de este cambio.

Los recursos visuales residen en `src/spt_go/assets/` y PyInstaller los incluye en el paquete OneFile. Durante la ejecución OneFile los extrae a una carpeta temporal; se accede a ellos mediante `__file__` del módulo empaquetado. Los datos personales se guardan junto al EXE si es posible o en `%LOCALAPPDATA%\SPT Go Portable`. La ruta temporal de extracción nunca se usa como carpeta de resultados.
