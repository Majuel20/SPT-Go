# Guía de usuario

Descarga `SPT_Go-Portable.exe` de la [última Release](https://github.com/Majuel20/SPT-Go-Portable/releases/latest). Haz doble clic, sin instalar Python. Revisa [PORTABLE.md](PORTABLE.md) antes de usarlo desde una carpeta protegida.

1. Escribe el nombre del proyecto, zona UTM, hemisferio, origen y punto de dirección de corriente.
2. Indica la **distancia al pozo auxiliar**. El punto de dirección no fija esa distancia.
3. En potencial, usa ON para la dirección de corriente o OFF para una o varias direcciones `Este, Norte;`. Configura rayos laterales y separación si necesitas abanico.
4. Define porcentajes entre 0 y 100, incluido 100. Los menores a 100 generan puntos de potencial; 100 corresponde al pozo auxiliar C100% y a una circunferencia de referencia.
5. Elige carpeta de salida y, opcionalmente, un KML/KMZ base. Valida la vista y pulsa **Generar archivos**. Cada ejecución crea una carpeta propia.

Ejemplo: con distancia 100 m y porcentajes `0; 50; 61.8; 90; 100`, el pozo se ubica a 100 m, las rutas de potencial terminan a 90 m y se dibujan circunferencias de 0, 50, 61.8, 90 y 100 m.

Guarda un proyecto JSON para recuperar entradas. Revisa en campo todas las coordenadas, distancias, permisos y condiciones de seguridad. Esta herramienta planifica puntos; no sustituye la metodología de ensayo, las normas aplicables ni el juicio de personal competente.
