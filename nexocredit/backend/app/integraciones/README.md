# Integraciones externas

Adaptadores del backend para servicios Azure y proveedores financieros.
Cada integración debe aislar su cliente, configuración y transformación de respuestas. Las rutas HTTP delegan en servicios de negocio; no deben contener credenciales ni llamadas específicas de proveedores.

Estado al 04/10/2026: adaptadores y rutas autenticadas implementados en la demo, con consultas reales documentadas. Los endpoints de estado comprueban configuración, no garantizan disponibilidad permanente. Ver [prueba integral](../../../docs/evidencias/2026-10-04/prueba-e2e.md).

- [Azure OpenAI](explicaciones_azure_openai/README.md): explica una evaluación guardada con guía demo recuperada de Search; la interfaz inicia la consulta automáticamente.
- [Azure AI Search](busqueda_azure_ai_search/README.md): catálogo de 2 guías / 14 secciones y búsqueda textual; no son políticas oficiales ni expedientes.
- [Azure ML](prediccion_azure_ml/README.md): clasificación académica UCI desde un formulario separado; la versión remota efectiva aún no está acreditada.
- [APIs financieras](datos_financieros/README.md): contexto público Banxico y Banco Mundial, con periodos y caché; no historial crediticio privado.

Ninguna integración altera las reglas demo ni autoriza créditos. Secretos solo en configuración privada del servidor, nunca en variables VITE_* ni evidencias. La generación IA y la consulta ML pueden generar consumo de los servicios existentes. No se crean recursos cloud durante una consulta normal.
