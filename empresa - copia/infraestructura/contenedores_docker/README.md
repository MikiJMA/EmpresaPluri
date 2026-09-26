# Ejecución en contenedores — Docker

Función: empaquetar frontend, backend y PostgreSQL para ejecución reproducible.
Estado: implementado y probado localmente. React compilado se sirve con Nginx, que reenvía /api/ a FastAPI; PostgreSQL 17 utiliza un volumen persistente. El servicio migraciones termina correctamente antes del arranque de la API. Que aparezca como Exited (0) es normal.

## Uso en Windows

Abrir Docker Desktop y esperar a que el motor esté activo. Desde la carpeta interior del proyecto:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir http://127.0.0.1:8080/; documentación de API en http://127.0.0.1:8080/docs. El comando construye las imágenes y espera los controles de salud. Volver a ejecutarlo después de cambiar código. La primera construcción requiere Internet.

Otras acciones:

Para el uso diario: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 abrir`. Reutiliza las imágenes existentes sin construir ni descargar, espera la salud de los servicios, comprueba la página y abre el navegador. Si faltan imágenes, primero completar `iniciar`. Los cambios de código requieren `iniciar` para reconstruir.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 estado
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 pruebas
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 logs
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 detener
```

Detener elimina los contenedores, pero conserva el volumen plurione-docker_datos_postgresql. No utilizar down -v ni eliminar el volumen si se necesitan los datos. El volumen no sustituye un respaldo.

## Configuración y separación de datos

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

Es un entorno de demostración sin autenticación, TLS ni respaldos automáticos. Usar datos ficticios y no exponerlo públicamente. Dependencias Python e imágenes base aún requieren fijación de versiones/digests para reproducibilidad estricta de producción.
