# Seguridad

Para informar una vulnerabilidad, utiliza la opción privada **Report a vulnerability** de GitHub si está habilitada. Si no lo está, abre un issue sin detalles explotables y solicita un canal privado al mantenedor. No publiques credenciales, archivos de proyectos reales ni datos de instalaciones en issues.

La aplicación realiza operaciones locales; no necesita conexión para generar rutas. Los archivos KML/KMZ de referencia son entrada del usuario y pueden contener enlaces externos que otros programas, como Google Earth, interpreten al abrirlos. Abre únicamente archivos de origen confiable. Verifica la suma SHA-256 del EXE descargado contra `SHA256SUMS` de la misma Release.

El ejecutable no está firmado digitalmente. Windows SmartScreen puede mostrar una advertencia de editor desconocido; comprueba el origen y la suma antes de decidir si ejecutarlo. No desactives el antivirus ni las protecciones de Windows.
