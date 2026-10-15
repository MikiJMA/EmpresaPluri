# Explicación directa del score — 13/10/2026

Solicitud: mostrar en la aplicación la explicación dada en el chat, evitando que ambos rangos parezcan riesgo Bajo.

Se sustituyó «alcanza el umbral» por condiciones directas en la tarjeta y la ayuda del input: 0–679 no puede dar Bajo, será Medio con margen >7.000 MXN y Alto con ≤7.000. Score 680–1000 puede dar Bajo únicamente con margen >15.000; Medio con >7.000 y ≤15.000; Alto con ≤7.000. Se añadió un ejemplo ficticio visible con margen de 20.000: 500 → Medio / 700 → Bajo. La tarjeta del margen indica su fórmula ingresos − gastos.

124 pruebas frontend aprobadas, sin fallos/omisiones, ESLint y compilación Vite aprobados. Se mantienen los tests de cortes 679/680, 7.000/15.000 y centavos adyacentes; el nuevo caso verifica la redacción explícita, el ejemplo identificado como ficticio y valores en blanco antes de evaluar.

Solo frontend fue reconstruido/recreado y quedó saludable. Backend/PostgreSQL conservan sus identificadores. HTTP local 200 con nuevo bundle `index-CMWusVuq.js`. No cambios de reglas, datos, proveedores, llaves o migraciones; sin consultas de IA o CI remota nuevas.

QA estática de componentes actuales con usuario/datos ficticios: escritorio con ambas tarjetas, ejemplo visible y ningún desplegable; móvil en iframe de 390 px con cuatro tarjetas y documento/contenido de 375 px sin desbordamiento horizontal. No acredita una nueva sesión humana o evaluación guardada.

Capturas locales:

```text
output/revisiones_visuales/2026-10-13/explicacion-score.jpg
output/revisiones_visuales/2026-10-13/explicacion-score-movil.jpg
```

Estas rutas son relativas a la raíz exterior del espacio de trabajo. Las capturas son privadas y locales; no se incluyen en la publicación ni en el paquete de entrega.

Servidor/pestaña temporales cerrados al terminar. Azure y su documentación/campos de keys permanecen conservados. Son reglas ilustrativas, no bandas oficiales de Buró ni autorización crediticia.
