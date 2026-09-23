# Integración continua — GitHub Actions

Función: automatizar pruebas Python, lint y compilación React.
Estado: publicado y verificado en la raíz Git, ../../../.github/workflows/ci.yml. Este directorio interior no es donde GitHub descubre los workflows. Backend y frontend finalizaron correctamente en https://github.com/MikiJMA/EmpresaPluri/actions/runs/35911875318 (commit d3cd93d).

El workflow ejecuta pruebas API con PostgreSQL 17 temporal, migraciones repetidas, instalación limpia npm ci, lint y compilación. Usa Python 3.12, Node 24 y rutas de la carpeta interior. Se activa con push a main, pull request o ejecución manual. No despliega servicios ni usa credenciales locales. La contraseña de CI solo pertenece al servicio efímero del runner. El fallo local de certificados npm no se evita desactivando TLS; la instalación limpia debe verificarse en GitHub.

Referencia: https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers
