# Reporte QA — prototipo 0.1

## Verificación Docker del 17 de septiembre de 2026

- Construcción de imágenes completada; ESLint y Vite aprobados durante la construcción.
- PostgreSQL, backend y frontend saludables; migraciones finalizadas con código 0.
- 10 pruebas aprobadas dentro del backend con PostgreSQL real y esquemas temporales aislados. La prueba CORS utiliza el origen configurado para cada entorno.
- Chrome en http://127.0.0.1:8080/: evaluación ficticia PRUEBA-DOCKER guardada, reenvío sin duplicados e historial conservado al recargar, sin errores JavaScript. Capturas de escritorio y móvil revisadas.
- Se reinició PostgreSQL y se consultó nuevamente el historial: el registro ficticio permaneció.
- No hay archivos .env en /app/backend de la imagen. La base y el backend no exponen puertos al host; la web se publica solo en loopback.
- La instalación y los datos locales no se modificaron. Pendientes: respaldos, recuperación completa, autenticación, endurecimiento y despliegue de producción.

## Verificación PostgreSQL del 17 de septiembre de 2026

- 10 pruebas aprobadas con RUN_POSTGRES_TESTS=1 y PostgreSQL real: reglas, validación, CORS con Idempotency-Key, falta de configuración, fallos de conexión, guardado y lectura desde otra conexión, reintentos idempotentes, conflicto 409, detalle 404, paginación, migraciones repetibles y rollback.
- Las pruebas de persistencia utilizan esquemas temporales aislados y los eliminan al finalizar.
- ESLint y compilación Vite aprobados con el historial incorporado.
- Navegador Chrome: guardado de una evaluación ficticia, reenvío sin duplicarla e historial conservado tras recargar; sin errores JavaScript. Se revisaron vistas de escritorio y móvil.
- Se conserva una evaluación identificada como PRUEBA-POSTGRES-LOCAL para demostrar el historial. No corresponde a una persona real.
- Continúan pendientes respaldos/restauración, seguridad de usuarios, carga y precisión predictiva. Las notas siguientes corresponden a verificaciones anteriores a la persistencia.

## Verificaciones ejecutadas

- npm run build: aprobado; Vite generó dist correctamente.
- npm run lint: aprobado; ESLint no reportó errores.

## Pruebas preparadas

En backend/tests/test_api.py: evaluación explicada, límites de reglas (margen 15000 y 7000), score bajo, margen negativo, entradas inválidas y rechazo CORS de origen ajeno.

Backend: dependencias instaladas y 4 pruebas aprobadas mediante unittest (incluyen múltiples escenarios). Starlette emite una advertencia de futura migración de httpx a httpx2 en TestClient; no afecta el resultado actual.

## Pendientes del sistema final

Validación visual/interactiva en navegador; persistencia y migraciones; autenticación y permisos; integración con proveedores; pruebas de carga con objetivos acordados; precisión, calibración y sesgos del modelo con datos autorizados; recuperación de respaldos; aceptación por usuarios.

No hay resultados de precisión predictiva: el prototipo ejecuta reglas demo y no un modelo entrenado. Compilar y pasar lint no equivale a validar el sistema completo.


## Verificación tras reorganizar carpetas

- Backend separado en backend/app con rutas, esquemas y servicio: 4 pruebas aprobadas.
- React separado en componentes, servicios y estilos: compilación y lint aprobados.
- Archivo .env trasladado a backend/.env conservando su contenido; no se carga automáticamente.
- Recursos originales sin uso conservados en docs/archivo.
