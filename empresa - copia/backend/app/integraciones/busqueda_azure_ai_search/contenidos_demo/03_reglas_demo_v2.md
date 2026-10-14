# NexoCredit: reglas de demostración por score y margen

Identificador: guia-demostracion-v2
Versión: 2.0
Actualización: 13/10/2026

## DEM-02. Reglas del formulario principal, reglas-demo-v2

Esta guía corresponde exclusivamente a `reglas-demo-v2`. Las evaluaciones existentes con `reglas-demo-v1` mantienen sus reglas, resultados y guía versión 1.0; no se recalculan.

El margen es ingresos menos gastos, redondeado a dos decimales, en MXN. Los centavos siguen en el cálculo y la base aunque la interfaz muestre resúmenes redondeados a pesos.

Primero se obtiene el riesgo por score capturado: de 0 a 499 es Alto; de 500 a 679 es Medio; de 680 a 1000 es Bajo. Un score menor indica mayor riesgo dentro de esta escala ilustrativa. No son bandas oficiales de Buró ni una probabilidad de incumplimiento; la fuente del score no está verificada.

Después se obtiene el riesgo mínimo por margen: hasta 7 000 MXN, incluido cero y negativo, es Alto; más de 7 000 y hasta 15 000 MXN es Medio; más de 15 000 MXN es Bajo. Exactamente 7 000 es Alto y exactamente 15 000 es Medio.

El resultado es el mayor riesgo de los dos, en el orden Bajo < Medio < Alto. Un margen insuficiente puede elevar el riesgo del score, pero un margen bueno no mejora un score Alto o Medio. Score 200 y margen 20 000 producen Alto; score 500 y margen 20 000 producen Medio; score 700 y margen 20 000 producen Bajo; score 900 y margen 7 000 producen Alto.

Deuda, pagos y atraso se conservan, pero no se incorporan como nuevas variables de esta regla. El laboratorio UCI y la explicación de IA siguen separados del cálculo. La explicación describe el resultado guardado, no lo modifica, autoriza o rechaza créditos. Es demostración educativa, sin validación para solicitantes reales, y requiere revisión humana.
