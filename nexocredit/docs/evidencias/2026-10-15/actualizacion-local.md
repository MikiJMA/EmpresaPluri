# Actualización de la instalación y cierre local — 15/10/2026

## Alcance real

Se aplicaron las mejoras a la instalación existente, además de conservar la copia pública depurada. La aplicación se organiza en `nexocredit/`. La instalación mantiene Compose `plurione-docker` y su volumen; la entrega utiliza `nexocredit-demo`. No se intercambiaron configuraciones privadas ni se movió el volumen entre proyectos.

Se retiró del código activo el mapeo aproximado MXN→UCI que inventaba meses/variables no capturados. El archivo anterior queda recuperable en el historial Git original. UCI sigue disponible como experimento explícito de 19 variables; ENIF ejecuta el análisis mexicano dentro del POST principal y conserva el resultado. Las reglas, el modelo estadístico y Ollama se identifican por separado.

## Respaldo y actualización

Antes de actualizar se creó un respaldo PostgreSQL consistente y privado. La restauración en un contenedor propio sin red, puertos o montajes del usuario concilió doce tablas: datos, columnas, restricciones y vistas. El temporal fue retirado. El respaldo no está cifrado y no se publica.

Se actualizaron únicamente backend y frontend con imágenes verificadas, sin dependencias ni migraciones. PostgreSQL conservó su identificador/volumen; las huellas de los datos y del esquema coincidieron antes/después. Se conservaron doce evaluaciones, dos revisiones, una cuenta local, configuración privada y proveedores/keys existentes. Las imágenes anteriores permanecen bajo etiquetas locales de respaldo. No se ejecutaron escrituras de prueba sobre la base original, push, CI remota, llamadas Azure, publicación web o control de ventanas.

API y frontend quedaron saludables; acceso local configurado y cuenta existente detectada, rutas del modelo protegidas con 401 sin sesión. Una inferencia numérica real con perfil ficticio dentro del backend actualizado comprobó el artefacto mexicano y el control de piloto. No se inició sesión suplantando al usuario ni se consultaron sus expedientes.

## Regresión final

**247 pruebas backend/PostgreSQL y 168 frontend**, sin omisiones. Migraciones repetidas en PostgreSQL temporal, cinco pruebas PowerShell, lint/build y auditoría npm con cero vulnerabilidades reportadas. El recorrido integral API ahora incluye ENIF, idempotencia, historial/revisión y seguimiento con pagos; cambios de score no alteran la salida del modelo. Logs locales exteriores:

- `output/tmp/enif2024/suite-integracion-final.log`.
- `output/tmp/enif2024/frontend-final.log`.
- `output/tmp/enif2024/actualizacion-instalada.json` (metadatos de actualización, no secretos).

La instalación y la copia pública conservan sus historiales: commits actuales descriptivos, sin fabricar fechas o reconstruir un proceso que no se registró. No se ejecutó push por decisión del usuario.

## Ensayo visual y transaccional aislado

Chrome headless con perfil propio y cinco capturas reales. PostgreSQL tmpfs, tres contenedores y dos redes etiquetadas propios; credenciales aleatorias en memoria, sin navegador ni datos del usuario. Se usó la imagen frontend final instalada. Azure/Ollama y consultas financieras externas no participaron: no se simula su disponibilidad.

Comprobaciones aprobadas: login/JWT real; perfil, resultado y metadatos persistidos; reintento idempotente y conflicto 409; cambio de score sin alterar ENIF; historial y modo sin perfil explícito; revisión humana guardada desde la interfaz sin cambiar el modelo; plan ficticio mediante API; abonos 20.02 + 30.03, reintento sin duplicado y alerta resuelta. La creación/pago del plan se comprobó por API, no como recorrido humano de esas pantallas. Cero errores JavaScript; geometría móvil sin desbordamiento.

El primer intento del ensayo ampliado falló porque el test asumía que la primera fila correspondía a una evaluación específica. Se corrigió la aserción para comprobar el identificador de la petición realmente realizada; no se cambió la aplicación por ese supuesto. El segundo intento completó todas las comprobaciones. Ambos retiraron sus recursos propios.

Evidencia final en el espacio exterior:

`output/evidencias/Piloto_Empresarial_2026-10-15/nexocredit-enif-f01e9f2a02/`

Incluye perfil, resultado escritorio/móvil, historial y revisión humana, más manifiesto con huellas y limpieza. Se inspeccionó la captura de revisión; las capturas de elementos largos pueden presentar artefactos de composición del navegador y no son una certificación visual exhaustiva.

## Límites de entrega

El paquete final se genera desde la copia pública depurada con manifiesto SHA-256. No incluye cuentas, .env privados, base, respaldos, datos CSV individuales, dependencias instaladas, PBIX/ABF o modelos Ollama. No sustituye los PDF antiguos: no se regeneraron en este incremento.

El éxito del software no valida crédito real. El modelo ENIF conserva AUC de prueba 0.605496 y capacidad limitada; no se promocionó un candidato con diferencias no concluyentes. Aún faltan historial empresarial autorizado, validación temporal independiente, costes/umbrales aprobados y autorización operativa. El piloto no habilita aprobaciones automáticas ni acredita aceptación del asesor.
