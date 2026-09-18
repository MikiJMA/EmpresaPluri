# Frontend

Interfaz React + Vite. Ejecutar desde la raíz de empresa:

```powershell
.\scripts\iniciar-frontend.ps1
```

- src/main.jsx: punto de entrada de React.
- src/App.jsx: estado y composición de la pantalla.
- src/evaluacion_crediticia/componentes/: formulario y presentación del resultado.
- src/evaluacion_crediticia/servicios/creditApi.js: comunicación con FastAPI.
- src/styles/: estilos globales y de la aplicación.
- public/: archivos públicos como el favicon.
- .env.example: ejemplo de URL de la API.

Instalación: npm ci dentro de frontend. Verificación: npm run build y npm run lint.
