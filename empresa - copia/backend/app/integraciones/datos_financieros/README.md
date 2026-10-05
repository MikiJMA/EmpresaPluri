# Consulta de datos — APIs financieras

Función implementada: consultar indicadores económicos públicos de México. No consulta historial crediticio, pagos ni deuda de personas. Los importes del formulario siguen siendo capturados por el usuario.

Estado al 04/10/2026: Banxico y Banco Mundial disponibles en la interfaz autenticada, con cuatro observaciones y sus periodos, unidades y procedencia. [Prueba integral](../../../../docs/evidencias/2026-10-04/prueba-e2e.md) comprobada; esto sustituye el fallo de token del 03/10/2026 documentado históricamente en QA. No garantiza disponibilidad futura ni datos en tiempo real. No se muestran valores ficticios cuando un proveedor falla.

## Fuentes y contrato

| Proveedor | Serie | Indicador | Periodo mostrado |
|---|---|---|---|
| Banco de México | SF43718 | Tipo de cambio FIX, MXN por USD | Fecha de la última observación publicada |
| Banco de México | SF61745 | Tasa objetivo, porcentaje anual | Fecha de la última observación publicada |
| Banco Mundial, WDI fuente 2 | FP.CPI.TOTL.ZG | Inflación de México, porcentaje anual | Año de la observación |
| Banco Mundial, WDI fuente 2 | NY.GDP.MKTP.KD.ZG | Crecimiento del PIB de México, porcentaje anual | Año de la observación |

- [Contrato SIE API de Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/), [datos oportunos](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp) y [límites](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/limiteConsultas). Se usa TLS 1.3 con validación de certificados y el token en `Bmx-Token`, nunca en la URL.
- [Contrato de indicadores del Banco Mundial](https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries). Petición pública para MEX, `format=json`, `mrnev=1`, `source=2`. Año más reciente no significa dato del día: la consulta comprobada devolvió 2025 para ambas series.
- API local: `GET /api/v1/datos-financieros/indicadores`. Requiere Microsoft Entra ID y los permisos/roles del resto de las rutas. Sin sesión devuelve 401; no existe una ruta pública alternativa.
- React: `frontend/src/datos_financieros/`, sección «Indicadores financieros». Consulta automáticamente después de iniciar sesión; permite volver a consultar sin forzar llamadas externas.
- Respuesta: `pais`, `aviso`, `cache_segundos` y `proveedores`. Cada fuente incluye estado (`disponible`, `parcial`, `sin_configurar`, `error`), mensaje propio, hora del intento/comprobación UTC, próxima renovación y observaciones con código, valor, unidad, frecuencia, periodo y enlace oficial. La hora de consulta no es la fecha del indicador.

## Privacidad, consumo y fallos

Solo se envían los códigos de series/país acordados. No se envían RFC, evaluaciones ni información de clientes a estos proveedores. No se modifica el riesgo demo, el modelo ML, la explicación OpenAI ni la base de evaluaciones.

Destinos HTTPS fijos, sin redirecciones; respuestas JSON acotadas a 128 KiB y tiempos de espera. Se comprueban país, series, fechas, duplicados y números finitos. Cero, negativo y ausencia permanecen distintos. Un fallo de una fuente no elimina los datos de la otra; no se sirve una observación vencida como vigente. Los mensajes externos y los tokens nunca se reenvían al navegador.

Caché por proveedor y proceso: una hora para respuestas válidas; un minuto para errores/configuración pendiente. Bloqueo por fuente para compartir consultas simultáneas. Con varios procesos o réplicas se necesita una caché compartida y revisar los límites antes de producción. No hay actualizaciones en segundo plano ni reintentos automáticos: una nueva petición después del vencimiento renueva la consulta.

## Configurar o recuperar Banxico en Windows

1. En el sitio oficial del SIE, usar «Obtener token». No copiar la clave de ejemplo de la documentación ni compartir credenciales en el chat.
2. Ejecutar `Conectar Banxico.cmd` en la raíz interior. Pegar el token en la consola de entrada oculta. Se guarda únicamente `BANXICO_API_TOKEN` en `infraestructura/contenedores_docker/.env`, conservando las demás variables; el archivo está excluido de Git, pero no cifrado en disco.
3. El configurador enciende PostgreSQL y espera su salud, sin recrearlo ni cambiar el volumen. Después recrea solo el backend para aplicar el token. No construye/descarga imágenes, ejecuta migraciones ni modifica registros. Si falla PostgreSQL, no continúa a recrear el backend.
4. Recargar PluriOne y consultar el estado real de Banxico. Guardar el token no acredita que el proveedor lo acepte.

Para recuperar un arranque fallido sin volver a pegar ni modificar el token:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-banxico.ps1 -UsarTokenGuardado
```

Requiere Docker Desktop activo, la configuración privada y las imágenes del proyecto existentes. El fallo del 03/10/2026 fue causado por PostgreSQL detenido: el backend respondió HTTP 200, pero su control de salud también consulta la base. Se encendió el contenedor existente y se comprobó la recuperación. No borrar el volumen ni cambiar contraseñas para resolver este caso.

Pruebas sin secretos ni proveedores reales:

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.test_datos_financieros -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-banxico.ps1 -SoloValidar
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\tests\banxico-config.test.ps1
```
