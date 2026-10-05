# Autenticación y permisos — Microsoft Entra ID

Función: identificar usuarios y comprobar permisos de analista y administrador.
Estado al 04/10/2026: implementado en la demostración. React usa MSAL y FastAPI valida el acceso delegado. La sesión real y el rechazo sin token se comprobaron en la [prueba integral](../../../docs/evidencias/2026-10-04/prueba-e2e.md).

## Contrato y controles actuales

- `seguridad.py` valida JWT RS256 contra claves públicas de Microsoft: firma, expiración y claims requeridos, audiencia, emisor, tenant, cliente autorizado, versión, identidad UUID, ámbito access_as_user y rol Analista o Administrador.
- `main.py` protege centralmente los routers de evaluación, historial, dashboard, revisión y las integraciones. Ausencia de token o token inválido: 401; ámbito/rol insuficientes: 403; fallo al recuperar claves públicas: 503, sin abrir acceso.
- `GET /api/v1/auth/config` es público y devuelve configuración de la SPA, no secretos. `GET /api/v1/auth/me` requiere token. Health y OpenAPI no equivalen a acceso a datos.
- Ambos roles acceden actualmente al mismo conjunto de funciones; no hay panel administrativo, permisos distintos por registro ni auditoría completa de accesos.
- El backend sustituye el responsable de nuevas revisiones por la identidad autenticada. Las revisiones anteriores pueden contener responsables declarados.

## Operación local

Abrir exactamente `http://localhost:8080/`: es el retorno configurado en la API. La interfaz en 127.0.0.1, 5173 u otro origen dirige al usuario a localhost:8080. Cambiar CORS no cambia los registros/retorno Entra. No desactivar autenticación ni modificar permisos para evitar un error de acceso.

Las credenciales se introducen solo en Microsoft. MSAL usa sessionStorage; no copiar ni compartir tokens. Los identificadores públicos de los registros no son secretos. La aplicación no envía el token Entra a las APIs de Azure ML, OpenAI, Search o proveedores financieros: cada adaptador usa su propia configuración del servidor.

Pruebas `backend/tests/test_entra.py`: claves de prueba y claims controlados, roles válidos, firma/claims/algoritmos inválidos, ámbito/rol insuficientes, rutas protegidas, CORS, identidad del responsable y fallo de claves. Estas pruebas no sustituyen la consulta real autenticada documentada.

Pendiente para producción: permisos diferenciados según alcance acordado, auditoría operativa, retención, cuotas y validación de seguridad del despliegue. No habilitar datos crediticios reales solo por contar con inicio de sesión.
