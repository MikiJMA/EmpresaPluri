# Reglas v2 e importes sin decimales

Comprobación local del 13/10/2026. Incremento autorizado para que score bajo implique mayor riesgo y para quitar decimales de los resúmenes monetarios. No es validación crediticia, producción ni aceptación del asesor.

## Implementación

- Nuevos resultados `reglas-demo-v2`: score 0–499 Alto, 500–679 Medio, 680–1000 Bajo. Margen <= $7,000 Alto, > $7,000 y <= $15,000 Medio, > $15,000 Bajo. Se conserva el mayor riesgo de ambos.
- Registros v1 y respuesta idempotente conservados; sin migración nueva, recálculo histórico o conversión en créditos.
- Guías por versión, catálogo local tres guías/quince secciones, manteniendo v1. El motor de plantillas es compatible con ambas; cada explicación identifica su versión.
- Resúmenes React redondeados al peso más cercano. Captura, cálculos y PostgreSQL conservan centavos; detalles de evaluación/pagos, tasas y métricas mantienen precisión pertinente.
- Ayuda dentro de tarjetas de score/margen, ejemplo ficticio, advertencias y etiqueta histórica v1.

[Manual y ejemplos](../../manuales/REGLAS_RIESGO_DEMO.md). PRD/MVP 1.4 actualizados sin inventar firmas o aceptación.

## Pruebas ejecutadas

| Comprobación | Resultado | Alcance |
|---|---|---|
| Backend completo | 175 aprobadas, sin omisiones | Imagen final; PostgreSQL temporal, red aislada, sin puertos/montajes privados; migraciones dos veces |
| Frontend | 129 aprobadas, sin omisiones | Construcción final; componentes, formato, contratos, acceso y regresiones |
| ESLint / Vite build | Aprobados | Incremento frontend servido localmente |
| Scripts PowerShell | Cinco archivos aprobados | URL/proxy, Banxico, suite aislada, organización y modo local; pruebas simuladas sin secretos |
| Cargador `--validar` | Tres documentos/quince secciones únicas | Solo archivos locales, sin Azure |
| `git diff --check` | Sin errores | CRLF admitido como terminador, sin cambiar configuración persistente Git |

Scoring: nueve combinaciones, cortes 499/500 y 679/680, margen con centavos y monotonía para 1001 scores con siete márgenes. Persistencia: evaluación v1 idéntica tras reintento, escenario nuevo v2 y cantidades conservadas. Explicación: guías exactas v1/v2, cachés distintas y ausencia de v2 controlada antes de solicitar Azure OpenAI. Ollama/Azure se prueban con respuestas simuladas, no generaciones reales.

Comprobación del backend desplegado, sin guardar ni llamar a IA: margen $20,000 y scores 200/500/700 devuelven Alto/Medio/Bajo; score 900 y margen $7,000 devuelven Alto; score 700 y margen $7,000.01 devuelven Medio. Catálogo local tres fuentes/quince secciones.

## Aplicación local y preservación

Respaldo privado anterior a la actualización: `.local/respaldos_postgresql/20261013T182814Z-4be06f15ff6b`. No compartir: dump sin cifrado, sin roles globales/ACL. No se restauró sobre la base original.

Compose actualizó backend/frontend sin descargar ni recrear PostgreSQL o migraciones. Los tres servicios saludables. Identidad del contenedor/imagen PostgreSQL, datos de todas las tablas y esquema coinciden por completo con el respaldo. Se mantienen nueve evaluaciones, dos revisiones, una cuenta y cinco migraciones; seguimiento/caché siguen vacíos. No se publican filas, hashes, contraseñas o identificadores personales.

`localhost:8080` sirve `/assets/index-DTtQkTef.js`. Evaluaciones, dashboard y estado de proveedores devuelven 401 sin token. No se creó sesión, cuenta o evaluación de trabajo para QA.

La construcción estándar encontró fallo de resolución de `auth.docker.io`. Se usaron imágenes/runtime/dependencias ya presentes y Dockerfiles temporales excluidos de Git, copiando código público actual. No se cambió DNS, proxy, aislamiento, TLS o autenticación ni se instalaron dependencias nuevas. Frontend ejecutó test/lint/build y backend final la suite completa aislada. Una construcción limpia futura necesita acceso al registro/dependencias.

## Revisión visual

Vista aislada de componentes actuales, score 700 y margen ficticio $18,333.33, sin API ni persistencia. Desktop 1280×900: dos tarjetas explicativas en paralelo y $18,333 visible. Móvil 390×844: una columna, rangos completos y sin desbordamiento del documento. La navegación horizontal móvil es intencional.

Capturas privadas fuera del proyecto activo: `output/revisiones_visuales/2026-10-13/score-v2-escritorio.jpg` y `score-v2-movil.jpg`, relativas a la raíz exterior. No muestran sesión de trabajo ni un nuevo resultado persistido. Vista QA detenida y contenedores temporales propios retirados; localhost permanece activo.

## Límites

Sin llamadas nuevas a Azure, Ollama generativo, Banxico/Banco Mundial o actualización Power BI. Evidencia cloud histórica: dos guías/catorce secciones; guía v2 preparada pero **no cargada en Azure AI Search**. Con documentos Azure hay que cargarla antes de explicar v2; falta de guía devuelve error, no una explicación v1.

Sin nueva CI remota, commit/push, publicación, capacitación o gestión con el asesor. No se repitió npm audit; la limitación TLS anterior continúa documentada, sin desactivar validación. No se afirma predicción de incumplimiento o aptitud para expedientes reales.
