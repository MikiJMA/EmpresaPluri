# Frontend

Marca visible: **NexoCredit** (nombre demostrativo, no razón social). `src/interfaz/marca.mjs` centraliza la identidad y adapta la presentación de nuestras dos guías demo sin modificar sus originales en Azure AI Search. Login, navegación, favicon y mensajes usan la nueva marca. Los recursos Azure, registros Entra, PostgreSQL, datos guardados y nombres técnicos de Docker conservan sus identificadores existentes para mantener las conexiones. No se renombra una empresa real ni se atribuye su aprobación a la demo.

Interfaz React + Vite. Ejecutar desde la raíz de empresa:

```powershell
.\scripts\iniciar-frontend.ps1
```

- src/main.jsx: punto de entrada de React.
- src/App.jsx: estado y composición de la pantalla.
- src/evaluacion_crediticia/componentes/: formulario y presentación del resultado.
- src/evaluacion_crediticia/servicios/creditApi.js: comunicación con FastAPI.
- src/styles/: estilos globales y de la aplicación.
- src/autenticacion/: acceso MSAL e identidad comprobada por FastAPI.
- src/azure_openai/: explicación automática de una evaluación guardada.
- src/azure_ml/: laboratorio académico UCI separado y estado del último intento.
- src/azure_search/: catálogo y búsqueda de guías demo.
- src/datos_financieros/: contexto Banxico/Banco Mundial con unidades, periodos y procedencia.
- public/: archivos públicos como el favicon.
- .env.example: ejemplo de URL de la API.

Instalación: npm ci dentro de frontend. Verificación: `npm test`, `npm run lint` y `npm run build`. Tras el cambio de marca, 48 pruebas, lint y compilación aprobados en Docker el 04/10/2026 (hora de México). Se comprobó NexoCredit en la sesión real de localhost:8080 y en las 2 guías / 14 secciones recuperadas de Azure AI Search, sin la marca anterior en su presentación. El historial conservó 7 evaluaciones. La captura queda en `.local/verificaciones_programacion/nexocredit-interfaz.jpg`, fuera de Git. No se ejecutó una nueva CI remota ni se publicó en GitHub; la publicación está pausada por solicitud del usuario. Las [evidencias anteriores](../docs/QA.md) conservan su fecha y alcance.

La demo autenticada probada es http://localhost:8080/, servida por Nginx. El servidor Vite en 5173 no coincide con el retorno Entra configurado; CORS por sí solo no resuelve esa diferencia. Nunca colocar claves privadas en variables VITE_*.
