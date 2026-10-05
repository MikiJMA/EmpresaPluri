# Ejecución en contenedores — Docker

Función: empaquetar frontend, backend y PostgreSQL para ejecución reproducible.
Estado: implementado y probado localmente. React compilado se sirve con Nginx, que reenvía /api/ a FastAPI; PostgreSQL 17 utiliza un volumen persistente. El servicio migraciones termina correctamente antes del arranque de la API. Que aparezca como Exited (0) es normal.

## Uso en Windows

Abrir Docker Desktop y esperar a que el motor esté activo. Desde la carpeta interior del proyecto:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir [http://localhost:8080/](http://localhost:8080/) e iniciar sesión con Microsoft; documentación de API en http://localhost:8080/docs. La configuración Entra actual requiere ese origen exacto y el lanzador lo conserva. El comando construye las imágenes y espera los controles de salud. Volver a ejecutarlo después de cambiar código. La primera construcción requiere Internet.

Otras acciones:

Para el uso diario: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 abrir`. Reutiliza las imágenes existentes sin construir ni descargar, espera la salud de los servicios, comprueba la página y abre el navegador. Si faltan imágenes, primero completar `iniciar`. Los cambios de código requieren `iniciar` para reconstruir.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 estado
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 pruebas
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 logs
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 detener
```

Detener elimina los contenedores, pero conserva el volumen plurione-docker_datos_postgresql. No utilizar down -v ni eliminar el volumen si se necesitan los datos. El volumen no sustituye un respaldo.

Desde la raíz interior, `Probar programacion.cmd` ejecuta las suites completas en una base temporal aislada, sin puertos publicados ni datos de trabajo. `Respaldar PostgreSQL.cmd` crea el respaldo privado manual y `Probar restauracion PostgreSQL.cmd` ensaya su recuperación en un contenedor temporal; no sobrescribe la base original. El ensayo del 04/10/2026 aprobó la conciliación de tres tablas. Dump sin cifrado ni roles globales/ACL; no automatiza retención ni acredita recuperación de producción. [Evidencia técnica](../../docs/evidencias/2026-10-04/cierre-tecnico.md).

## Configuración y separación de datos

### Conexión Banxico y PostgreSQL detenido — 03/10/2026

`Conectar Banxico.cmd` guarda el token privado sin mostrarlo y conserva las demás variables. Ahora enciende PostgreSQL primero (`--no-recreate`) y espera su salud; después recrea solo el backend (`--no-deps --force-recreate`) para aplicar la configuración. Usa las imágenes existentes (`--no-build --pull never`); no borra volúmenes, modifica registros ni ejecuta migraciones. Los mensajes de progreso de Docker en stderr no se confunden con fallos en PowerShell 5.1: se comprueba el código de salida y se muestran errores propios sin contenido privado.

Si el token ya quedó guardado pero el backend no pasó la comprobación de salud, ejecutar desde la raíz interior:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-banxico.ps1 -UsarTokenGuardado
```

El 03/10/2026 se confirmó PostgreSQL detenido, backend HTTP 200 pero sin acceso a la base. Se recuperaron ambos controles de salud conservando el contenedor/volumen PostgreSQL y el token; Banxico rechazó por separado aquel token. El 04/10/2026 ambos proveedores financieros estuvieron disponibles en la aplicación autenticada. Guardar configuración no confirma acceso al proveedor. Ver [contrato financiero](../../backend/app/integraciones/datos_financieros/README.md) y [prueba posterior](../../docs/evidencias/2026-10-04/prueba-e2e.md).

### Alternativa ante bloqueo de certificados npm (22 de septiembre de 2026)

Se comprobó UNABLE_TO_VERIFY_LEAF_SIGNATURE al descargar npm, incluso usando el almacén de certificados de Windows. No se desactivó TLS ni se instalaron certificados desconocidos. Se compiló con las dependencias ya instaladas en frontend/node_modules y se empaquetó el resultado con frontend-precompilado.Dockerfile. Esta alternativa no soluciona el certificado ni permite instalar dependencias nuevas. No acredita una instalación limpia desde package-lock.

Para repetirla, desde frontend ejecutar ESLint y Vite con Node instalado (o el runtime local), estableciendo VITE_API_URL=/ durante la compilación. Después, desde la raíz interior:

```powershell
docker build -t plurione-docker-frontend -f infraestructura/contenedores_docker/frontend-precompilado.Dockerfile .
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 abrir
```

El Dockerfile alternativo solo incluye dist y nginx.conf. El comando abrir reutiliza esta imagen. iniciar conserva la construcción estándar y puede volver a fallar hasta resolver el certificado de la red.

El primer inicio genera contraseñas aleatorias en el archivo privado .env de esta carpeta. No compartirlo ni publicarlo. Conservarlo: cambiar esas contraseñas en el archivo no cambia las de una base ya inicializada. La aplicación usa un usuario sin privilegios de superusuario; el administrador se reserva para inicializar PostgreSQL. .dockerignore excluye archivos .env y dependencias locales de las imágenes.

WEB_PORT permite cambiar el puerto web si 8080 está ocupado. Solo se publica en 127.0.0.1. PostgreSQL ahora publica 127.0.0.1:55433 para Power BI Desktop; el backend no publica puertos al equipo. Las solicitudes del navegador usan el mismo origen mediante Nginx. Ver analitica/reportes_power_bi para preparar el usuario lector.

Esta base es independiente de la instalación nativa de PostgreSQL y de .local/postgresql/datos. No se copiaron ni borraron registros locales. La versión de desarrollo en 5173 sigue siendo independiente de Docker en 8080.

Es un entorno de demostración con autenticación Entra, pero sin TLS local ni respaldos automáticos comprobados. Usar datos ficticios y no exponerlo públicamente. Dependencias Python e imágenes base aún requieren fijación de versiones/digests para reproducibilidad estricta de producción. El volumen persistente no acredita restauración de un respaldo.
