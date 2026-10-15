# Seguimiento crediticio ficticio — implementación y comprobaciones

Fecha local del trabajo: 11/10/2026, America/Mexico_City. Los respaldos/muestras usan UTC 12/10/2026. Solicitud: implementar pendientes técnicamente posibles, sin involucrar todavía al asesor. No se contactó a personas externas, publicaron cambios cloud ni crearon cuentas/roles nuevos.

## Implementado

- Módulo funcional FastAPI/PostgreSQL/React **Créditos y pagos**, no una carpeta preparada.
- Un plan por evaluación existente, 1–60 cuotas, total y fechas coherentes, dinero Decimal/NUMERIC/texto decimal.
- Abonos parciales declarados, máximo 500 por plan, idempotencia por UUID/cuerpo/acción/cuenta, sin sobrepago concurrente.
- Saldo pendiente/vencido, atraso pendiente, cumplimiento y puntualidad; indicadores descriptivos de captura. Datos ausentes distintos de cero; un pago tardío no se vuelve puntual.
- Alertas persistidas Pendiente/Atendida/Resuelta, atención con motivo/versión y recálculo sin duplicar eventos.
- Eventos en la misma transacción que el movimiento. Responsable autenticado, no enviado por cliente. Auditoría global del nuevo módulo sólo Administrador; Analista recibe 403.
- Migración 005 aditiva, cinco tablas nuevas y doce tablas totales. Evaluaciones/revisiones/identidad y scoring previos conservados.

No se calculan tasas/intereses/amortizaciones bancarias, importan Buró/expedientes privados ni verifican depósitos. El calendario y abonos son ficticios, no operaciones financieras reales. Alertas se recalculan al crear/pagar o pulsar Actualizar vencimientos, no existe vigilancia permanente. Las acciones son pasos operativos, no recomendaciones de aprobación. Azure ML UCI sigue separado y local deshabilitado; no se inventó un modelo predictivo para estas variables.

## Calidad y regresiones

Suite inicial: **154 backend/PostgreSQL y 104 frontend** aprobadas; tras endurecer contratos de ledger/auditoría, suite final **154 y 105**, sin fallos ni omisiones. Lint/build, `npm audit` (cero vulnerabilidades reportadas) y cinco archivos PowerShell aprobados. Migraciones repetidas dos veces en PostgreSQL temporal aislado; no fixtures en la base de trabajo.

La primera construcción detectó un cierre de expresión JSX incorrecto en el nuevo formulario de atención; se corrigió antes de desplegar. No se sustituyó ese resultado por un éxito inventado.

Casos nuevos: Decimal `0.10 + 0.20 = 0.30`, fechas reales/futuras, cuotas ordenadas/suma exacta, lectura con corte, ausencia/cero, ratios extremos, auth/RBAC, idempotencia/conflictos, pagos parciales, cuota ajena, no suplantación, atención versionada, resolución sin aprobación, rollback al fallar evento y contrato UI. Ocho abonos concurrentes con la misma clave guardan uno; cuatro abonos independientes sobre saldo insuficiente admiten sólo uno. El formulario conserva claves ante fallos y la selección impide mostrar una respuesta de otro crédito.

Frontend valida importes/sumas/relaciones, estados de cuota, días, ledger de abonos y porcentajes, además de fechas de auditoría. Escapa texto, sin HTML ejecutado. No confunde categoría demo con predicción crediticia.

## Medición acotada de rendimiento

Método reproducible en `backend/tests/test_seguimiento.py`, prueba `test_medicion_local_lecturas_secuenciales_y_concurrentes`. TestClient/FastAPI con PostgreSQL 17 Docker temporal, Python 3.12, motor Docker observado 29.8.0. Una evaluación, un crédito, dos cuotas, sin navegador, TLS ni red externa. Recursos del backend/herencia de Docker Desktop no se controlaron como benchmark comparativo de hardware.

| Muestra final | Peticiones | p50 | p95 | Máximo | Errores HTTP |
|---|---:|---:|---:|---:|---:|
| Secuencial | 40 | 20,99 ms | 23,02 ms | 24,24 ms | 0 |
| Cuatro hilos | 40 | 65,11 ms | 93,10 ms | 96,07 ms | 0 |

No es una prueba de saturación, usuarios concurrentes reales, latencia de navegador o SLA. No extrapolar a una cartera grande, cloud o proveedor ML/IA. Primera corrida: p95 24,55/96,36 ms, sin errores. Resultado final privado: `output/verificacion_seguimiento/2026-10-11/rendimiento.json`, raíz exterior excluida de Git.

## Datos y operación local

Antes de migrar se creó respaldo privado. Compose construyó/recreó migraciones/backend/frontend, mantuvo PostgreSQL y su volumen, y aplicó 005. Después se construyó/recreó sólo frontend para los contratos finales. Las imágenes base no se fijaron nuevamente; sus comprobaciones no equivalen a lock de dependencias productivo.

Se verificaron **9 evaluaciones, 2 revisiones, 1 cuenta local** conservadas. Las cinco tablas de seguimiento estaban vacías, sin créditos/pagos/alertas/eventos de prueba insertados en la base de trabajo. `/health` respondió `ok`, tres servicios saludables, migraciones 001–005 registradas y doce tablas presentes. Se leyó el listado nuevo vacío desde el repositorio de trabajo sin exponer datos.

Las huellas y cantidades de evaluaciones, revisiones y usuarios del respaldo previo coinciden con el posterior, no sólo sus conteos. Las rutas nuevas de créditos y auditoría rechazaron solicitudes anónimas con HTTP 401. La página y bundle final se comprueban con HTTP 200.

Tras la última guarda contra lecturas antiguas del detalle se reconstruyó frontend, repitiendo sus 105 pruebas, lint y build. Bundle servido: `/assets/index-C3Y8gnMw.js`, HTTP 200; los tres servicios siguieron saludables. Backend no cambió después de su suite final de 154. La vista temporal y su servidor fueron cerrados; la aplicación de trabajo sigue en localhost:8080.

Respaldos privados en `.local/respaldos_postgresql`: previo `20261012T012236Z-a9fe2901cb6d`; esquema actualizado `20261012T013243Z-a0769dc63de6`. El segundo se restauró únicamente en un contenedor temporal: **doce tablas**, datos, huellas, columnas, restricciones y vistas coincidentes; origen conservado y temporal retirado. Dumps sin cifrado ni roles globales/ACL: no compartir. No es recuperación de host completo.

## Presentación y documentación

Revisión visual estática de componentes reales con datos ficticios, sin API/auth: escritorio y un iframe de 390 px; contenido medido 375/375 px (barra vertical incluida en ancho del marco), sin desbordamiento horizontal global. Tabla con contenedor desplazable. No fue una prueba manual completa de creación/abono en la sesión del usuario. El primer servidor de QA no respondió por el aislamiento de red; reabierto en loopback autorizado respondió 200. Los servidores temporales se detienen al finalizar.

Capturas privadas, raíz exterior `output/revisiones_visuales/2026-10-11/seguimiento-creditos.png` y `seguimiento-creditos-movil.png`. No representan créditos reales ni filas guardadas en la base del usuario.

Manuales nuevos: seguimiento, arquitectura/datos, mantenimiento/soporte y material de práctica. PRD/MVP incorporan seguimiento vigente manteniendo línea base histórica. Informe técnico compara objetivos y límites. Bitácora individual registra implementación, no certifica Scrum/horas. Guía preparada no es acta de capacitación ni aceptación.

## Pendientes no cerrados por este incremento

Dataset/históricos autorizados representativos, política crediticia y definición/horizonte de incumplimiento, modelo validado para el caso, vigilancia/notificaciones externas, reversión de movimientos, ledger en Power BI, auditoría de todos los accesos, operación de producción y evidencia real de formación/ceremonias/aceptación. No se pidió intervención del asesor. No hay nuevas llamadas de IA, CI remota, commit publicado o recursos cloud.
