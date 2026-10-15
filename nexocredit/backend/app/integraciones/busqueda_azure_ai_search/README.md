# Documentos demo — Azure AI Search

`buscador.py` consulta el índice `plurione-documentos-demo` del servicio `search-plurione-demo-julian`. Contiene alcance y guía académica, no políticas oficiales ni expedientes de clientes. La consulta real del catálogo comprobó dos documentos y 14 secciones; esto no acredita aptitud para decisiones crediticias ni disponibilidad permanente.

Comprobación autenticada del 04/10/2026: catálogo, lectura y búsqueda «margen» con recuperación DEM-02; guía usada también por la explicación automática. Ver [evidencia integral](../../../../docs/evidencias/2026-10-04/prueba-e2e.md).

Rutas protegidas por Entra ID en `main.py`:

- `GET /api/v1/azure-search/estado`: indica si la configuración está presente; no hace una consulta cloud.
- `GET /api/v1/azure-search/documentos`: recupera automáticamente el catálogo demo completo, hasta 50 secciones, ordenado por fuente, versión y sección. Comprueba el total recibido para no mostrar una lista parcial como completa.
- `POST /api/v1/azure-search/buscar`: consulta textual literal, de 2 a 200 caracteres y hasta cinco fragmentos; no acepta filtros, URLs ni sintaxis Lucene del cliente.

Todas las respuestas conservan identificador, fuente, título, sección, contenido, versión y aviso. El adaptador utiliza una clave de consulta privada, timeout de ocho segundos y errores sanitizados. No crea ni modifica índices, no expone claves y no llama a OpenAI. La generación de explicaciones usa por separado la búsqueda existente, cuyo contrato no cambia.

Desde el 13/10/2026, `scripts/cargar_documentos_search.py` prepara los tres archivos fijos de `contenidos_demo/` (quince secciones), conservando la guía histórica y agregando DEM-02 v2. `--validar` comprueba solo los archivos locales. La clave administrativa para cargar se introduce oculta y no se guarda. No se cargó el índice cloud en este incremento: la evidencia Azure anterior sigue siendo de dos guías/catorce secciones. Con documentos Azure, explicar v2 requiere cargar su guía; falta de guía falla cerrado sin utilizar v1. [Reglas y versiones](../../../../docs/manuales/REGLAS_RIESGO_DEMO.md). Las políticas empresariales y documentos privados requieren otro alcance.

Pruebas: `python -m unittest backend.tests.test_azure_search backend.tests.test_azure_openai`. Usan respuestas simuladas y comprueban fuentes, límites, autenticación, catálogo vacío/parcial y fallos sin revelar datos privados.
