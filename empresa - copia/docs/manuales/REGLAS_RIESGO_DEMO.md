# Score, margen e importes — NexoCredit

Actualización: 13/10/2026. Reglas ilustrativas de la demostración; no son rangos oficiales de Buró, una predicción calibrada ni una política de aprobación de crédito.

## Evaluaciones nuevas: reglas-demo-v2

Un score menor corresponde a mayor riesgo. El margen disponible es ingresos mensuales menos gastos mensuales, redondeado a dos decimales por la API. Los gastos incluyen los pagos de créditos. El resultado final conserva el peor riesgo entre score y margen: un buen margen nunca mejora el riesgo del score.

| Score capturado | Margen de $7,000 o menos | Más de $7,000 y hasta $15,000 | Más de $15,000 |
|---|---|---|---|
| 0–499 | Alto | Alto | Alto |
| 500–679 | Alto | Medio | Medio |
| 680–1000 | Alto | Medio | Bajo |

499 es Alto; 500 y 679 son Medio; 680 y 1000 pueden ser Bajo. Exactamente $7,000 obliga a Alto; exactamente $15,000 impide Bajo. Formatear una cifra no cambia estos cortes.

Con margen de $20,000: score 200 → Alto, 500 → Medio, 700 → Bajo. Con score 900: margen $5,000 → Alto, $10,000 → Medio, $20,000 → Bajo. Son ejemplos ficticios, no recomendaciones para una solicitud real.

El score es capturado, no consultado ni verificado. Deuda, pagos y atraso se validan y conservan, pero no son nuevas entradas del scoring demo. El laboratorio UCI, Azure ML y scikit-learn siguen separados; estas reglas no son un modelo entrenado.

## Historial y versiones

Las nuevas evaluaciones llevan `version_modelo=reglas-demo-v2`. Los registros `reglas-demo-v1` conservan resultado, solicitud, centavos y versión; no se recalculan. Repetir una solicitud idéntica con el mismo UUID devuelve la evaluación original. Para evaluar las reglas nuevas se crea otro escenario.

La guía v1 conserva la regla anterior: Bajo si margen > $15,000 y score >= 680; en otro caso Medio si margen > $7,000; Alto en los demás casos. Un registro antiguo con score 200 y margen $20,000 puede indicar Medio. La interfaz lo identifica como anterior, no recalculado. Dashboard y Power BI resumen los resultados originales, aunque haya más de una versión.

## Importes sin decimales en los resúmenes

Tarjetas monetarias, dashboard y margen del historial se redondean al peso más cercano: $18,333.33 → **$18,333**; $18,333.67 → **$18,334**. No se truncan ni se reemplazan los datos originales. Ausencia sigue siendo «—» o «Sin datos»; cero es $0.

La captura admite centavos. El detalle de evaluación, cuotas, abonos, saldos contables y explicaciones exactas conservan decimales necesarios. Tasas, porcentajes, tipo de cambio y métricas ML no se redondean como pesos.

Un margen de $7,000.01 puede verse como $7,000 en una tarjeta, pero el corte usa $7,000.01: con score 700 es Medio, no Alto. La tarjeta advierte el redondeo y su título conserva el importe exacto; el detalle permite consultarlo también en móvil.

## Explicaciones locales y Azure

| Versión guardada | Fuente de DEM-02 | Versión documental |
|---|---|---|
| reglas-demo-v1 | guia-demostracion-v1 | 1.0 |
| reglas-demo-v2 | guia-demostracion-v2 | 2.0 |

El catálogo local incluye tres guías/quince secciones: mantiene v1 y agrega `03_reglas_demo_v2.md`. Plantilla local, Ollama y Azure OpenAI seleccionan la guía correspondiente. Si falta, devuelven error controlado: no explican v2 con v1. La clave de caché incluye la versión de evaluación.

Azure y sus campos de keys permanecen implementados. El catálogo cloud comprobado históricamente era de dos guías/catorce secciones; **esta actualización no carga ni consulta Azure**. Antes de usar documentos Azure con v2, cargar la guía nueva con [Cargar documentos Azure AI Search](<../../operacion/integraciones/Cargar documentos Azure AI Search.cmd>). Es una operación cloud separada, con credenciales y recursos vigentes. `python scripts/cargar_documentos_search.py --validar` comprueba localmente tres guías/quince secciones sin cargar el índice.

La IA explica el resultado guardado, no lo cambia ni autoriza créditos; no recibe RFC, CURP, identidad o revisiones. Mantener evidencia histórica no garantiza vigencia de la suscripción.

## Comprobación

Pruebas de los cortes, monotonía con margen fijo, nueve combinaciones de la tabla, guías versionadas, caché separada, conservación/idempotencia del historial y redondeo con centavos/ausencia. [Resultados y límites del incremento](../evidencias/2026-10-13/reglas-v2-y-importes.md).
