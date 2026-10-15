# Ceros convencionales y ayuda del score — 11/10/2026

Cambio de presentación solicitado por el usuario. No cambia `reglas-demo-v1`, la validación de los siete campos, las integraciones, el guardado ni el cálculo del riesgo.

## Implementación

- Se sustituyó IBM Plex Mono en cifras, inputs, score, KPI, métricas y tablas por una fuente local (`Segoe UI`, Arial como alternativa) con números tabulares. Se desactiva la variante de cero marcado y se retira la solicitud de la fuente monospace del HTML y de la vista de QA. No se agregaron fuentes remotas.
- La ayuda debajo del score cambia con su valor: de 0 a 679 no cumple la condición de Bajo; desde 680 puede ser Bajo, Medio o Alto según el margen. Un campo vacío no se interpreta como cero y un valor inválido muestra el rango entero permitido.
- Un desplegable explica las condiciones completas: Bajo con score ≥680 y margen >15,000 MXN; si no cumple Bajo, Medio con margen >7,000 MXN; Alto en otro caso. Los límites son estrictos y el resultado definitivo se confirma al evaluar en la API.
- El campo enlaza la orientación y su aviso mediante `aria-describedby`; la ayuda usa `aria-live="polite"`. No hace peticiones, genera IA ni persiste datos al escribir.

## Verificación

Las 72 pruebas frontend pasaron tanto en Node local como al construir la imagen Docker; lint y build también pasaron. Se agregaron seis pruebas de ayuda del score y dos de tipografía. Se cubren vacío/cero, score 679/680/1000, decimal, fuera de rango y mensajes que no inventan riesgo Alto solo por tener score bajo.

La revisión visual aislada usa los componentes reales con datos ficticios, sin MSAL ni llamadas a APIs. Se observaron ceros normales en deuda, pagos y atraso, la orientación para score 700 y las tres condiciones desplegadas. El estilo computado del campo confirmó `Segoe UI`, `tabular-nums` y `"zero" 0`. La captura local está en `output/revisiones_visuales/2026-10-11/ceros-y-score.jpg` de la raíz Git exterior, excluida del repositorio público.

Solo se reconstruyó y recreó el frontend de trabajo, que quedó saludable. Backend y PostgreSQL no se reiniciaron; no se cambiaron cuentas, claves ni evaluaciones. La sesión local del usuario se observó antes de recargar; para cargar el nuevo bundle debe recargar y volver a iniciar sesión. No se acredita una evaluación nueva ni una consulta financiera real en esta revisión.

El score es capturado y no verificado. Esta ayuda describe únicamente la demo académica, no rangos de una entidad financiera ni autorización de créditos. Las pruebas backend anteriores permanecen como evidencia histórica separada; no se volvieron a ejecutar en este cambio de frontend.
