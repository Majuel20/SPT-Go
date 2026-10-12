# Archivos de salida

Cada generación crea una carpeta `Proyecto_AAAAMMDD_HHMMSS_microsegundos` con:

- `*_Coordenadas_*.xlsx`: resumen, hoja de corriente, hojas de potencial y todos los puntos. Las celdas MED1–MED3 permiten registrar mediciones; PROM calcula el promedio. Las tablas tienen su propio filtro y no se agrega un filtro de hoja superpuesto.
- `*_GoogleEarth.kml`: puntos, rutas y circunferencias de referencia.
- `*_GoogleEarth.kmz`: KML comprimido. Si se usa un KMZ base, conserva sus recursos y el original no se modifica.
- `Proyecto.json`: configuración recuperable; se siguen aceptando los esquemas `spt-go` y `spat-ssee` de versión 1.
- `Registro.txt`: resumen de generación.

La vista y las coordenadas de entrada usan UTM en metros. Las latitudes y longitudes exportadas usan WGS84. Los archivos no son mediciones ni certifican un sistema de puesta a tierra.
