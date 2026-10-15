# Créditos, pagos y alertas — guía de la demo

Implementación local del 11/10/2026. Sólo obligaciones ficticias declaradas: no importa Buró, no confirma depósitos, no desembolsa y no modifica `reglas-demo-v1`.

## Recorrido

1. Iniciar sesión con Microsoft o cuenta local y abrir **Créditos y pagos** en el menú.
2. Desplegar **Crear un plan de cuotas ficticio**. Seleccionar una evaluación ya guardada; las páginas permiten recorrer las evaluaciones sin copiar UUID.
3. Escribir concepto, fecha de apertura UTC y monto total pactado en MXN. Añadir una o más cuotas (hasta 60), con fechas únicas ordenadas, posteriores o iguales a la apertura. Su suma exacta debe ser el total.
4. Guardar. Una evaluación admite un plan; no es autorización de crédito. Reintentar sin cambiar campos reutiliza la misma clave. No se convierten automáticamente evaluaciones antiguas.
5. Abrir **Ver pagos y alertas**. Consultar saldo por cuota, abonado, saldo vencido y días de atraso.
6. Registrar un abono en una cuota. Admiten pagos parciales hasta su saldo; no fechas anteriores a la apertura o posteriores a hoy UTC. Cambiar campos inicia otra operación. El pago registrado es una declaración ficticia, no una conexión bancaria.
7. Consultar alertas. **Registrar atención** requiere motivo y versión actual; atender no liquida la cuota. Un pago que completa la cuota resuelve su alerta al recalcular.
8. Pulsar **Actualizar vencimientos** al revisar otro día. Las alertas se recalculan al crear el plan, registrar pagos o pulsar ese botón. No existe un servicio de vigilancia diaria en segundo plano.

El total pactado es el total de obligaciones del plan: el programa no calcula capital/interés, tasas, comisiones, amortización bancaria, condonación, refinanciación o penalizaciones. No se editan ni eliminan pagos desde la API; una herramienta de reversión contable requeriría otro diseño. No usar datos reales.

## Cálculos

| Dato | Método |
|---|---|
| Saldo de cuota | Importe pactado menos abonos registrados hasta el corte |
| Saldo pendiente total | Total pactado menos abonos al corte |
| Saldo vencido | Suma del saldo de cuotas con vencimiento anterior al corte UTC |
| Atraso máximo pendiente | Mayor número de días desde vencimiento de una cuota con saldo |
| Cumplimiento | Cuotas vencidas ya completas / cuotas vencidas; sin vencidas es ausencia, no 0 % |
| Puntualidad | Cuotas vencidas cubiertas a más tardar en su fecha / cuotas vencidas |
| Pagos / ingresos | Pago mensual capturado / ingreso mensual capturado × 100 |
| Gastos / ingresos | Gasto mensual capturado / ingreso mensual capturado × 100 |
| Deuda / ingreso mensual | Saldo de deuda capturado / ingreso mensual capturado, en veces |

Completar una cuota tarde mejora cumplimiento, no puntualidad. La cuota que vence hoy todavía no se clasifica vencida. Pagar antes del vencimiento reduce saldo sin crear atraso. Los indicadores de captura no reemplazan el ledger: son dos fuentes distintas y explícitas. Ausencia de deuda/pagos capturados se presenta como No capturado, no cero.

Los importes del seguimiento se validan con dos decimales, límite 1.000.000.000 MXN y almacenamiento `NUMERIC(12,2)`. La API devuelve texto decimal canónico (`"0.30"`), no números de coma flotante para saldos. Máximo 500 abonos por plan. No se definen límites de endeudamiento “aceptables”, probabilidades ni recomendaciones de aprobación.

## Alertas y trazabilidad

Una cuota con saldo y fecha vencida genera `CUOTA_VENCIDA`. El estado inicia Pendiente; Atendida registra una revisión, no un pago; Resuelta se deriva de ausencia de saldo vencido. Cambios de saldo/días/estado incrementan versión y conservan eventos. Un recálculo sin cambios no duplica esos eventos.

Cada creación, pago y atención conserva responsable autenticado; el cliente no lo envía. Los eventos se guardan en la misma transacción que el movimiento. Fallar la escritura del evento revierte el movimiento, no deja un pago sin trazabilidad. Las cuotas se bloquean mediante la fila de su crédito para serializar abonos concurrentes.

Analista y Administrador pueden crear planes, consultar, registrar abonos y atender alertas compartidas de la demo. **La auditoría global del seguimiento exige Administrador en el servidor**. No se elevó el rol de la cuenta local del alumno. Las facultades anteriores del resto de la aplicación permanecen iguales. La auditoría no cubre todos los accesos/lecturas ni reemplaza una auditoría productiva.

## API

Todas las rutas exigen sesión; configuración y llaves nunca van en el body.

| Método | Recurso, relativo a `/api/v1/seguimiento` | Función |
|---|---|---|
| GET | `/creditos?limite=20&offset=0` | Lista paginada, límite 1–100 y offset hasta 1.000.000 |
| POST | `/creditos` | Plan con UUID `id`, `evaluacion_id`, concepto, apertura, total y cuotas |
| GET | `/creditos/{id}` | Snapshot consistente de cuotas, pagos, cálculos y últimas alertas |
| POST | `/creditos/{id}/pagos` | UUID `id`, `cuota_id`, importe decimal y fecha del pago |
| POST | `/creditos/{id}/actualizar-alertas` | Recálculo persistido, sin proveedor externo |
| POST | `/alertas/{id}/atender` | UUID de operación, versión anterior y observaciones visibles |
| GET | `/auditoria?limite=20&offset=0` | Metadatos de eventos, sólo Administrador |

401 sesión inválida; 403 falta de facultad administrativa; 404 recurso ausente; 409 conflicto/idempotencia/saldo; 422 captura inválida; 503 base indisponible. No se cambian claves para “resolver” un timeout: reintentar el mismo body/id evita duplicados. Si cambió la versión de alerta, actualizar el detalle antes de una nueva atención.

Operación, respaldo y límites generales: [acceso y proveedores](ACCESO_LOCAL_Y_PROVEEDORES.md), [mantenimiento](MANTENIMIENTO_Y_SOPORTE.md), [arquitectura y datos](../desarrollo/ARQUITECTURA_Y_DATOS.md).
