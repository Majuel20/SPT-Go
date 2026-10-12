**SPT Go Portable 1.0.2 — By: Majuel20**

SPT Go Portable permite preparar rutas y puntos de corriente y potencial desde una ventana, con diseño oscuro, botones neón y logo MK.

La Release pública v1.0.2 contiene **SPT_Go-Portable.exe**. Destino: Windows 10/11 de 64 bits. Los usuarios del EXE no necesitan instalar Python.

Funciones principales:

- Coordenadas, zona UTM, hemisferio y distancia editables.
- ON/OFF para usar la dirección de corriente o varias direcciones de potencial.
- Corriente con un único **Pozo auxiliar (C100%)**.
- Potencial hasta el último porcentaje menor al 100%, conservando la circunferencia del 100%.
- Abanico exclusivamente de potencial.
- Vista esquemática, guardado de proyectos y generación de Excel, KML y KMZ.
- Integración opcional con un KML/KMZ base.

Cada generación se guarda en una carpeta independiente para conservar los resultados anteriores. El punto de dirección orienta la recta; la distancia determina la ubicación del pozo.

La compilación ejecuta pruebas de generación, conversión UTM y creación de la ventana antes de preparar los archivos de esta Release.

Corrección de esta versión: se elimina el filtro de hoja superpuesto al filtro de las tablas de corriente y potencial. La exportación valida los filtros y los encabezados antes de guardar los resultados.
