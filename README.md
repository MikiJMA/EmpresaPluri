# NexoCredit — espacio de trabajo

El código activo está en la carpeta [empresa - copia](empresa%20-%20copia/README.md). Se conserva esa ruta para no romper Docker, scripts, configuraciones privadas ni el workflow.

Para ver el proyecto ordenado en VS Code, abrir **NexoCredit.code-workspace** con «Archivo → Abrir área de trabajo desde archivo». Muestra la aplicación como NexoCredit y la automatización como GitHub Actions, sin la doble carpeta en el explorador.

- [Operación: abrir, actualizar, conexiones, pruebas y respaldos](empresa%20-%20copia/operacion/README.md).
- [Índice de documentación](empresa%20-%20copia/docs/README.md).
- [PRD](empresa%20-%20copia/docs/producto/PRD_NEXOCREDIT.md).
- [MVP](empresa%20-%20copia/docs/producto/MVP_NEXOCREDIT.md).
- [Tecnologías y estado](empresa%20-%20copia/REQUISITOS_TECNOLOGICOS.md).

El workflow ejecutable permanece en .github/workflows/ci.yml de esta raíz Git. Se conservan los datos locales, la configuración privada, el entorno Python activo y las dependencias actuales. El 14/10/2026 se retiraron a la Papelera la plantilla antigua, sus dependencias, el entorno `.venv-roto`, temporales sin referencias activas y cachés Python. Los documentos y evidencias se mantienen; no se publican secretos ni se cambia el alcance local de la demo.
