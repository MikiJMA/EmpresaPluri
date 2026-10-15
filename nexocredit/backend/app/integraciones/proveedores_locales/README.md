# Alternativas explícitas sin Azure

Los clientes Azure siguen implementados y son los valores predeterminados. Cada función se selecciona en la configuración del **servidor**, nunca con claves o nombres de modelo enviados desde el navegador. No existe fallback automático: un fallo de Ollama/local no consume Azure ni cambia silenciosamente el origen.

| Variable | Valores | Responsabilidad |
|---|---|---|
| `EXPLICACIONES_PROVEEDOR` | `azure`, `ollama`, `local` | Azure OpenAI; IA local Ollama; o plantilla de reglas sin IA |
| `DOCUMENTOS_PROVEEDOR` | `azure`, `local` | Azure AI Search o búsqueda textual en tres guías/quince secciones locales versionadas |
| `ML_PROVEEDOR` | `azure`, `local`, `deshabilitado` | Azure ML, modelo scikit-learn académico local o inferencia deshabilitada explícitamente |
| `OLLAMA_URL` | HTTP local en puerto 11434 | Solo localhost, 127.0.0.1, ::1 o host.docker.internal; sin credenciales, consultas o redirecciones |
| `OLLAMA_MODEL` | Nombre de modelo local ya instalado | Por ejemplo `llama3.1:8b`; no instala/descarga modelos ni acepta nombres cloud |

Ejemplo para una operación sin consumo Azure:

```dotenv
EXPLICACIONES_PROVEEDOR=ollama
DOCUMENTOS_PROVEEDOR=local
ML_PROVEEDOR=local
# Desde el contenedor backend hacia Ollama instalado en Windows:
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
```

Para backend ejecutado directamente en Windows, la URL es `http://127.0.0.1:11434`. Los cambios requieren reiniciar/recrear solo el backend. La disponibilidad de Ollama en la red de Docker depende de la configuración de escucha de esa instalación; no se modifica ni se expone un puerto automáticamente.

## Contratos y límites

- Los endpoints heredados `/api/v1/azure-openai`, `/api/v1/azure-search` y `/api/v1/azure-ml` se mantienen por compatibilidad. El nombre de la ruta no representa el proveedor actual: consultar `proveedor` y `origen` en la respuesta y `/api/v1/proveedores/estado` (autenticado).
- `configurado` comprueba configuración, no una ejecución correcta del modelo ni disponibilidad permanente. El estado no consume IA ni consulta redes externas. No incluye claves o URLs privadas.
- El catálogo local vigente contiene tres fuentes/quince secciones: conserva v1 y agrega DEM-02 v2. El catálogo Azure comprobado históricamente tenía dos guías/catorce secciones; la guía v2 no está acreditada como cargada en cloud. La búsqueda offline distingue palabras literales, elimina diferencias de acentos y exige todas las palabras; no es búsqueda semántica ni reproduce el analizador de Azure.
- La explicación usa sólo ingresos, gastos, score capturado y resultado guardado, sin RFC, identidad, UUID u observaciones. Recupera DEM-02 versión 1.0 para `reglas-demo-v1` o versión 2.0 para `reglas-demo-v2`; falta de guía compatible devuelve 503, no usa otra versión. Elegir Ollama con documentos Azure **sí** consulta Azure Search: para operar sin Azure hay que elegir documentos locales explícitamente.
- `local` devuelve `generada_por_ia: false`: plantilla determinista de reglas, nunca presentada como IA. `ollama` devuelve `generada_por_ia: true`, proveedor y modelo, distinguiendo hechos del servidor y comentario IA. Ninguno cambia el resultado de evaluación; la ruta sí utiliza caché/cuotas privadas PostgreSQL descritas abajo.
- Ollama usa únicamente `POST /api/chat`, salida JSON con esquema, `stream: false`, temperatura 0 y máximo **450 tokens**. Tiempo límite HTTP 60 segundos, dos generaciones simultáneas; sin reintentos, herramientas, proxies del entorno, redirecciones o descargas. Se validan finalización, modelo, texto y cita; los errores no muestran respuestas internas del servicio.

- Desde el 11/10/2026, la ruta de explicación comparte caché/cuotas PostgreSQL con Azure: éxito reutilizable 24 horas, error un minuto, diez nuevas generaciones por cuenta/hora y exclusión de duplicados concurrentes. La caché almacena texto/referencias privados, no RFC/CURP ni credenciales. No cambia automáticamente de proveedor, no borra texto vencido y no garantiza ausencia de consumo tras una interrupción durante la generación. Ver [manual de continuidad local](../../../../docs/manuales/ACCESO_LOCAL_Y_PROVEEDORES.md).
- Desde el 12/10/2026 `ML_PROVEEDOR=local` sirve `nexocredit-uci-logistica-v1`, modelo scikit-learn independiente exportado a JSON numérico. No carga el pickle AutoML histórico ni equivale al candidato Azure: usa diecinueve entradas UCI/NTD y no modifica el formulario principal MXN. `deshabilitado` bloquea explícitamente la inferencia; un fallo local no inventa resultados ni cambia de proveedor. [Manual y métricas](../../../../docs/manuales/LABORATORIO_IA_LOCAL.md).
- Todo sigue siendo una demostración con datos ficticios. Local no significa precisión, autorización de crédito ni aptitud productiva.

Fuentes oficiales consultadas para el adaptador: [API chat de Ollama](https://docs.ollama.com/api/chat) y [salidas estructuradas](https://docs.ollama.com/capabilities/structured-outputs). El modo cloud de Ollama no forma parte de esta alternativa.

## Contrato Ollama corregido — 14/10/2026

Una generación real de QA produjo una comparación numérica incorrecta; el resultado guardado siguió correcto. La nueva composición **no permite que el LLM redacte los hechos ni la razón del riesgo**: `hechos_calculados()` y `_texto_hechos()` los producen por código, respetando el margen original, las bandas y la versión guardada. v1 conserva su regla histórica; v2 usa las bandas independientes y el peor riesgo. Si los importes/resultados guardados no concuerdan con su versión, devuelve 409 sin alterar el registro.

Ollama sólo añade un comentario académico **de hasta 65 palabras y 600 caracteres**, en texto plano, sin cifras, categorías/decisiones de riesgo o comparaciones. El JSON limita contenido/cita, la generación tiene techo de 450 tokens y `validar_comentario_ia()` aplica control de formato/vocabulario. **No es una verificación semántica completa**: no demuestra que toda frase libre sea verdadera. La respuesta separa «Hechos calculados por el servidor (no generados por IA)» de «Comentario académico de IA», con aviso de revisión humana.

Una salida fuera del contrato falla con **502**, sin mostrar ese comentario, recalcular el riesgo, reintentar o usar fallback. Configuración/guía ausente, modelo no encontrado, cuota o timeout mantienen sus códigos propios; no todo error se convierte en 502. Las regresiones automáticas están aprobadas, pero este documento **no afirma todavía texto real nuevo corregido verificado**.

La clave de caché añade `revision_ollama=hechos-servidor-comentario-academico-v3` **sólo para Ollama**, de modo que no reutiliza narraciones anteriores. No cambia las claves Azure/plantilla, no borra filas de caché, evaluaciones o DB y no modifica registros v1/v2. La siguiente generación respeta cuota/caché existentes. [Hallazgo, suites y pendientes](../../../../docs/evidencias/2026-10-14/entrega-demo.md).
