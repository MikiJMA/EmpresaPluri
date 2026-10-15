# Documentos demo

Al montar la aplicación después del acceso con Microsoft, `BuscadorDocumentos.jsx` carga automáticamente el catálogo con `GET /api/v1/azure-search/documentos`. El backend consulta el índice demo de Azure AI Search con su clave de consulta privada; la nueva ruta conserva la protección central de Entra ID. No consulta Azure OpenAI ni escribe en Azure o PostgreSQL.

`PanelDocumentos.jsx` presenta el buscador arriba y las guías agrupadas por fuente y versión abajo, con un extracto y un desplegable para leer las secciones originales. Los resultados de búsqueda no reemplazan ni ocultan las guías. Carga, error con reintento, catálogo vacío y búsqueda sin coincidencias tienen mensajes separados. No hay contenido ficticio de respaldo si Azure falla.

El catálogo admite hasta 50 secciones y comprueba el total devuelto para no presentar silenciosamente una lista incompleta. Desde el 13/10/2026 el proveedor documental local sirve tres guías/quince secciones, con reglas v1/v2 agrupadas por fuente y versión. La evidencia histórica de Azure es de dos guías/catorce secciones; no se cargó el índice cloud en este incremento. No son políticas oficiales, archivos de solicitantes ni criterios de aprobación. Las búsquedas usan `POST /buscar`, máximo cinco fragmentos. El acceso local y Entra protegen las mismas rutas; el proveedor se selecciona por función, no por método de acceso.

Pruebas aisladas: `node --test tests/documentos.test.mjs` y `python -m unittest backend.tests.test_azure_search`. No hacen consultas reales a Azure. La vista estática `tests/previsualizar-interfaz.mjs` utiliza únicamente los archivos demo locales para comprobar el diseño; no acredita una conexión cloud.
