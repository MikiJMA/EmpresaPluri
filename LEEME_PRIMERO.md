# Instalación y datos locales

El código está en `nexocredit/`. Docker Desktop debe estar iniciado; la primera construcción requiere Internet. Esta instalación usa `plurione-docker`, conservando el volumen PostgreSQL existente. No copiar su configuración privada a la entrega, no usar `down -v` ni iniciar otra copia con el mismo nombre Compose o sobre los mismos puertos.

Desde `nexocredit/`, ejecutar:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

### Alternativa directa con Docker Compose (sin PowerShell)

Desde `nexocredit/`:

```bash
docker compose --project-name plurione-docker --project-directory infraestructura/contenedores_docker --env-file infraestructura/contenedores_docker/.env -f infraestructura/contenedores_docker/docker-compose.yml up -d --build --wait
```

Para detener conservando el volumen de datos de PostgreSQL (nunca usar `down -v`):

```bash
docker compose --project-name plurione-docker --project-directory infraestructura/contenedores_docker --env-file infraestructura/contenedores_docker/.env -f infraestructura/contenedores_docker/docker-compose.yml down
```

### Acceso y cuenta

Abrir [localhost:8080](http://localhost:8080/) y usar la cuenta propia existente. Sólo en una instalación nueva sin configuración/cuenta, activar proveedores locales y crear un usuario, por separado:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\modo-local.ps1 -Accion local
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\modo-local.ps1 -Accion usuario
```

No existe contraseña predeterminada. El modelo numérico mexicano está incluido y evalúa sin conexión a Azure o INEGI; sus límites aparecen en pantalla. Ollama requiere servicio y modelo instalados (`llama3.1:8b` por defecto). Sin ellos, configurar `EXPLICACIONES_PROVEEDOR=local` y `VALORACION_IA_PROVEEDOR=deshabilitado` en el `.env` privado; la explicación será una plantilla marcada NO IA generativa. No editar otras variables ni borrar keys Azure.

La copia pública de entrega utiliza `nexocredit-demo`: no comparte cuentas, secretos o base de esta instalación. Su guía de instalación es propia. [Recorrido breve y documentación](README.md), [operación](nexocredit/docs/manuales/OPERACION.md) y [respaldos](nexocredit/operacion/README.md).

## Verificación

Las mismas pruebas que ejecuta [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Desde `nexocredit/`, con el entorno virtual activado y PostgreSQL disponible:

```powershell
# Backend — 247 pruebas esperadas (API, PostgreSQL, integraciones, validación)
python -m unittest discover -s backend/tests -v

# Frontend — 168 pruebas esperadas (componentes, servicios, contratos)
cd frontend
npm test

# Lint y compilación
npm run lint
npm run build
```

La suite aislada completa (PostgreSQL temporal propio, sin tocar datos de trabajo) se ejecuta con `operacion/pruebas/Probar programacion.cmd`.
