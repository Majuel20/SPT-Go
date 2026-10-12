# Publicar una versión nueva

La Release `v1.0.2` y su ejecutable son históricos y no se alteran. La versión actual del código sigue siendo `1.0.2`; **no etiquetes `v1.0.3` hasta aprobar y preparar esa versión**.

1. Revisa el Pull Request, resultados de CI y derechos de los recursos. Obtén aprobación explícita para publicar.
2. Actualiza únicamente `src/spt_go/_version.py` a la versión aprobada, el historial y las notas de publicación. Ejecuta pruebas y build Windows x64.
3. Fusiona el PR según el proceso del mantenedor. Crea una etiqueta **nueva** `vX.Y.Z` en el commit aprobado. No muevas etiquetas existentes.
4. En **Actions → Compilar SPT Go Portable → Run workflow**, selecciona el commit etiquetado, marca `publish_release=true` e indica la etiqueta exacta. El flujo comprueba que versión, etiqueta y commit coinciden y que la Release no existe. Si falla, no publica.
5. Descarga el artefacto y verifica `SHA256SUMS`. Comprueba en Windows 10/11 x64, especialmente GUI, recursos y escritura en carpetas protegidas. La publicación manual solo debe iniciarse tras estas verificaciones y aprobación.

El flujo crea artefactos descargables aun cuando `publish_release=false`. Para validar integridad en PowerShell: `Get-FileHash .\SPT_Go-Portable.exe -Algorithm SHA256`; compara con la línea del EXE en `SHA256SUMS`. El ZIP incluye guía, licencia y avisos de terceros. El EXE puede compartirse por separado junto con un enlace a los avisos de la Release.
