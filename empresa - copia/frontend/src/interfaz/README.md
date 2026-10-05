# Interfaz de evaluación

`MarcoAplicacion.jsx` contiene el menú lateral, cabecera y pie del diseño Enterprise adaptado del HTML proporcionado por el usuario. Sus enlaces apuntan a las cinco secciones implementadas: resumen, evaluación, historial, laboratorio Azure ML y documentos. La identidad mostrada proviene de `UsuarioContext`, después de la verificación con Entra ID. Los controles de sesión siguen en `autenticacion/Acceso.jsx`.

Los estilos de `styles/Enterprise.css` se limitan a `.enterprise-app`, salvo la posición visual de los controles de sesión. El login mantiene su diseño y tipografía independientes. En pantallas pequeñas la navegación pasa a una fila desplazable y el formulario y resultado se apilan.

Los cuatro indicadores de `evaluacion_crediticia/componentes/IndicadoresEscenario.jsx` usan la captura enviada y el margen devuelto por la API; antes de evaluar muestran guiones. El resumen conserva escala 0–1000, factores del servidor, advertencias demo y explicación automática de Azure OpenAI. No se adoptaron cifras, personas, tendencias, escalas, políticas ni afirmaciones de cumplimiento del ejemplo visual. Tampoco se incorporaron campos que el contrato de la API no contempla.

`TablaHistorial.jsx` presenta los registros recibidos por `EvaluationHistory.jsx`. La carga, paginación y selección para revisión manual permanecen en este último componente; no cambian sus endpoints ni la persistencia.

La sección Documentos conserva su buscador y ahora carga automáticamente las guías del índice demo de Azure AI Search. Muestra fuente, versión y secciones desplegables, con estados explícitos de carga y error; consultar `azure_search/README.md`.

Las pruebas `frontend/tests/interfaz.test.mjs` comprueban estos contratos visuales con datos ficticios y sin consultas a Azure.

Para QA visual aislada, ejecutar desde `frontend/`: `node tests/previsualizar-interfaz.mjs` (añadir `--documentos` para enfocar las guías). Publica una página estática únicamente en `127.0.0.1`, con puerto efímero indicado en la salida y un aviso de datos ficticios. No inicia la aplicación, MSAL ni llamadas a API, no guarda información y no permite iniciar/cerrar sesión ni revisar registros. Las guías de esta vista proceden de los archivos demo locales, no de Azure. Sirve para comprobar escritorio y celular sin alterar una sesión real. Detener con Ctrl+C o escribiendo `detener` en su entrada estándar. Esta vista no se incluye en los archivos `dist` publicados por Nginx.
