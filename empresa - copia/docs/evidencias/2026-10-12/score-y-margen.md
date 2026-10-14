# Significado del score y margen en sus tarjetas — 12/10/2026

Solicitud: retirar el desplegable de reglas del formulario y explicar los valores/rangos directamente donde se muestran **Score capturado** y **Margen disponible**.

## Cambio realizado

`IndicadoresEscenario.jsx` incorpora explicación del último valor y rangos siempre visibles. `ScoreAyuda.jsx` conserva una orientación breve y accesible ligada al input, sin el desplegable rechazado. `ayudaScore.mjs` centraliza los textos; `ScoreAyuda.css` adapta tarjetas amplias a una columna en móvil, con bordes rectos y tipografía de ceros convencionales conservados.

- Score 0–679: no alcanza el umbral para Bajo; el margen decide entre Medio y Alto.
- Score 680–1000: alcanza el umbral para Bajo, únicamente con margen mayor a 15.000 MXN.
- Margen hasta 7.000: Alto, incluidos cero/negativos y el límite exacto.
- Margen mayor a 7.000 y hasta 15.000: Medio, incluido exactamente 15.000.
- Margen mayor a 15.000: Bajo con score ≥680; Medio con score menor.

Son los cortes existentes en `backend/app/evaluacion_crediticia/scoring.py`, no nuevos rangos oficiales de Buró o un scoring entrenado. No se cambió backend ni se recalcularon registros. Antes de evaluar, los cuatro valores siguen siendo guiones, pero se puede leer la guía. La interpretación numérica de las tarjetas usa la captura enviada y el margen de la API, no captura sin evaluar ni cifras previas.

## Verificación

123 pruebas frontend aprobadas, sin fallos u omisiones, en host y build Docker. Incluyen ausencia distinta de cero, entradas inválidas, score 0/679/680/1000, cortes de margen 7.000/15.000 y centavos adyacentes, contenido dentro de las tarjetas, retiro del desplegable, acceso/contratos existentes y conservación de los siete campos. ESLint y Vite aprobados tras corregir un paréntesis del helper de QA; el intento inicial fallido no llegó a reemplazar la interfaz.

Se reconstruyó/recreó **únicamente frontend**, que quedó saludable. Backend y PostgreSQL conservan exactamente sus identificadores previos, sin migración/recreación o escritura de trabajo. `localhost:8080/` devuelve 200 y referencia `index-Sk-Sntiz.js`; no se alteraron keys ni proveedores Azure/locales. No se ejecutaron nuevas suites backend, consultas cloud, generación Ollama, auditoría npm o CI remota: no son cambios de este incremento.

QA visual aislada con usuario/datos ficticios y componentes React actuales:

- Desktop: score/margen en dos tarjetas amplias, lectura del ejemplo 700 y 20.000 MXN, todos los rangos visibles y sin desplegable.
- Estado sin evaluación: cuatro guiones con las guías visibles; no se presenta el score del input como evaluación completada.
- Móvil en iframe de 390 px: una columna, cuatro tarjetas y documento/contenido de 375 px sin desbordamiento horizontal, salvo la navegación interna desplazable prevista.

Capturas locales (no sesión real ni llamada de evaluación):

```text
output/revisiones_visuales/2026-10-12/score-y-margen.jpg
output/revisiones_visuales/2026-10-12/score-y-margen-movil.jpg
```

Estas rutas son relativas a la raíz exterior del espacio de trabajo. Las capturas son privadas y locales; no se incluyen en la publicación ni en el paquete de entrega.

El servidor temporal inicial no respondió desde el navegador; se detuvo y se reinició con acceso local de red autorizado, comprobando HTTP 200 antes de la revisión. No se desactivaron protecciones o autenticación. Se cierra el servidor temporal al terminar. No se inició/reinició la sesión del usuario ni se guardaron nuevas evaluaciones para revisar la pantalla.
