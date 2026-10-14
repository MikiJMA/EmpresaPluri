# Acceso local, Ollama y configuración de llaves

Actualización de desarrollo: 14/10/2026. NexoCredit conserva Microsoft Entra ID y los adaptadores Azure. La alternativa local es adicional, no elimina las tecnologías requeridas ni acredita una instalación productiva. Las evidencias anteriores conservan su fecha.

Azure OpenAI, Machine Learning, AI Search y Entra **sí se implementaron en la demo**, con pruebas reales fechadas del 04/10/2026. Sus campos y credenciales se conservan aunque el proveedor seleccionado sea local. Ver [resumen de implementación Azure y espacios para las keys](AZURE_IMPLEMENTADO_Y_CONFIGURACION.md); no se afirma vigencia actual de la suscripción por mantener esa documentación.

## Dónde poner las llaves, sin pegarlas en una terminal

Para la aplicación Docker, el único archivo privado es:

`infraestructura/contenedores_docker/.env`

Está excluido de Git y de la imagen Docker. No lo adjuntes, fotografíes ni publiques. El ejemplo público comentado es [.env.example](../../infraestructura/contenedores_docker/.env.example): úsalo como referencia de nombres, no como almacén de llaves reales. No copies el ejemplo completo encima de tu archivo privado: sobrescribirías la configuración PostgreSQL existente.

Abre [Editar configuración privada](<../../operacion/integraciones/Editar configuracion privada.cmd>) con doble clic: abre el archivo en Bloc de notas. También puedes abrirlo en VS Code. Cambia únicamente el valor después de `=` y guarda. Usa [Actualizar NexoCredit](<../../operacion/aplicacion/Actualizar NexoCredit.cmd>) para aplicar código/configuración. Después de tener las imágenes actualizadas, los accesos de cambio de modo solo recrean el backend sin recompilar.

| Campo | Valor que se introduce |
|---|---|
| `AZURE_OPENAI_RESPONSES_URL` | URL completa del endpoint Responses Azure |
| `AZURE_OPENAI_DEPLOYMENT` | Nombre exacto de la implementación, no necesariamente el nombre genérico del modelo |
| `AZURE_OPENAI_API_KEY` | Solo el valor de la llave privada del recurso correspondiente |
| `AZURE_SEARCH_ENDPOINT` | Dirección del servicio Search |
| `AZURE_SEARCH_INDEX_NAME` | Nombre del índice de guías demo |
| `AZURE_SEARCH_QUERY_KEY` | Llave de consulta del índice; no una llave administrativa |
| `AZURE_ML_SCORING_URI` | Dirección del endpoint ML |
| `AZURE_ML_MODEL_ID` | Identificador configurado del candidato académico |
| `AZURE_ML_API_KEY` | Llave privada del endpoint ML |
| `BANXICO_API_TOKEN` | Solo el valor del token SIE, sin `Bmx-Token:` ni `token=` |
| `LOCAL_AUTH_SECRET` | Secreto aleatorio que genera el configurador; NO es la contraseña del usuario |
| `OLLAMA_MODEL` | Nombre exacto de un modelo instalado, por ejemplo `llama3.1:8b` |

Ollama y Banco Mundial no requieren llaves. Nunca pongas secretos en `frontend/`, `public/`, `VITE_*` ni en este manual. No cambies las contraseñas PostgreSQL después de crear el volumen: editar `.env` no cambia las contraseñas dentro de la base.

## Usar Ollama y documentos locales

Mantén Docker Desktop y Ollama abiertos. [Activar modo local](<../../operacion/integraciones/Activar modo local.cmd>) configura explícitamente:

```dotenv
LOCAL_AUTH_ENABLED=true
EXPLICACIONES_PROVEEDOR=ollama
DOCUMENTOS_PROVEEDOR=local
ML_PROVEEDOR=local
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
```

El configurador genera un secreto local si no existe, conserva el existente al repetir y mantiene las llaves Azure y el volumen PostgreSQL. No descarga modelos, no cancela suscripciones y no elimina recursos cloud. Debes detener o eliminar por tu cuenta los recursos Azure que generen consumo si ya no deseas pagarlos; seleccionar un modo local no cambia su facturación.

| Función | Alternativa sin Azure |
|---|---|
| Inicio de sesión | Cuenta local con contraseña y sesión de 30 minutos por defecto; Microsoft sigue disponible |
| Explicación | Modelo instalado en Ollama, ejecutado en el equipo; resultado identificado como IA local |
| Documentos | Desde el 13/10/2026, tres guías/quince secciones locales, con reglas v1/v2; búsqueda textual, no búsqueda semántica Azure |
| Evaluaciones, historial y revisiones | PostgreSQL existente; cambiar proveedor no cambia reglas. Desde el 13/10/2026, nuevas evaluaciones v2 y resultados v1 conservados |
| Dashboard y Power BI | Conservan la base/vista existente; Power BI requiere actualización manual |
| Laboratorio IA UCI | Modelo logístico scikit-learn incluido; 19 entradas académicas NTD, separado de la evaluación principal; no carga AutoML |
| Indicadores financieros | Banxico/Banco Mundial siguen necesitando Internet; no dependen de Azure |

La alternativa local no equivale a trabajo completamente offline si sigues consultando APIs financieras. Con `DOCUMENTOS_PROVEEDOR=local` y `EXPLICACIONES_PROVEEDOR=ollama`, explicar y recuperar guías no requiere Azure. Si seleccionas documentos Azure con Ollama, la recuperación documental sí usa Azure: los proveedores se eligen por función.

Para una explicación sin modelo de IA, puedes poner `EXPLICACIONES_PROVEEDOR=local`: es una plantilla determinista marcada como **no generada por IA**, no un reemplazo equivalente a un modelo de lenguaje.

La integración Ollama limita dos generaciones simultáneas y espera hasta 60 segundos por respuesta HTTP. No reintenta ni cambia automáticamente a Azure si falla. Sólo envía el escenario numérico permitido, hechos calculados por el servidor y la guía demo; no RFC, CURP, identidad, UUID u observaciones. La respuesta distingue hechos/razón del servidor de comentario académico IA, requiere revisión humana, no cambia el riesgo ni autoriza créditos.

## Contrato Ollama corregido — 14/10/2026

En una generación real de QA se observó que Ollama comparó incorrectamente el score con un importe y con 499. El riesgo guardado era correcto; no se modifica para ajustarlo al texto. El código corregido produce **hechos, bandas y razón por código, no por IA**, con el margen/resultado original y la versión guardada. Conserva la interpretación histórica v1 y la guía 1.0; para v2 usa guía 2.0 y las bandas actuales. Si faltan la guía compatible o los hechos no concuerdan con el registro, falla explícitamente sin usar otra versión.

El modelo sólo añade un comentario académico en texto plano **hasta 65 palabras / 600 caracteres**, con máximo **450 tokens** de generación. No se admiten cifras, vocabulario de score/margen/riesgo, categorías o comparaciones. Los controles de formato/vocabulario no verifican la semántica completa ni garantizan la verdad de cualquier frase libre. La pantalla separa los hechos del servidor del comentario IA y conserva el aviso de revisión humana.

Una respuesta fuera del contrato devuelve **502**: no se muestra el comentario rechazado, no se reemplaza por una plantilla presentada como IA ni se usa Azure automáticamente. El registro permanece guardado; no se reintenta. Timeout, guía/modelo/configuración ausentes o cuota mantienen los códigos específicos del proveedor. Las pruebas automáticas están aprobadas, pero **la nueva generación real corregida no se declara verificada por este manual**.

La revisión `hechos-servidor-comentario-academico-v3` separa la **clave de caché sólo de Ollama** para no reutilizar textos anteriores. No borra caché, registros o base, no altera las claves Azure/plantilla y no recalcula v1/v2. Un intento nuevo sigue sujeto a cuota y coste/recursos del proveedor elegido. [Hallazgo y estado de comprobación](../evidencias/2026-10-14/entrega-demo.md).

## Crear la primera cuenta local

Después de actualizar las imágenes y activar el modo local, abre [Crear usuario local](<../../operacion/aplicacion/Crear usuario local.cmd>). Introduce usuario y nombre; la contraseña se solicita dos veces con entrada oculta, entre 6 y 128 caracteres. No se exige combinar mayúsculas, números o símbolos; no puede ser solo espacios. Este mínimo de seis es para la demo local: usa una contraseña difícil de adivinar y no reutilizada. No hay cuentas predeterminadas, registro público ni contraseñas en código. La cuenta creada por este acceso recibe el rol Analista.

Recarga `http://localhost:8080/` y usa los campos Usuario local / Contraseña local. La cuenta Microsoft continúa siendo una opción separada.

La contraseña se guarda como hash scrypt con sal aleatoria. Los JWT locales usan clave/emisor/audiencia distintos de Entra. Cada petición comprueba que la cuenta siga activa y que su versión de sesión no haya sido revocada. Los tokens locales se conservan solo en memoria del navegador: al recargar la página debes volver a iniciar sesión local. No se renuevan automáticamente.

Cinco fallos por cuenta o veinte fallos por origen en quince minutos bloquean temporalmente el acceso. Los accesos correctos no consumen ni borran la cuota de fallos. También se limita a sesenta peticiones de acceso por origen y minuto, incluidos éxitos. Nginx sobrescribe la IP del cliente y el backend solo la acepta desde el servicio `frontend` configurado/resuelto; los encabezados enviados al puerto directo no conceden confianza. Clientes detrás de la misma IP/NAT todavía pueden compartir el límite: no es un sistema de identidad productivo. Los contadores anteriores conservan su valor hasta vencer, sin desactivar bloqueos existentes.

Administración explícita desde Exec del contenedor backend:

```sh
# Crear cuenta; solicita contraseña oculta.
python scripts/crear_usuario_local.py --usuario asesor --nombre "Asesor demo"

# Resetear contraseña/roles y revocar sesiones anteriores.
python scripts/crear_usuario_local.py --usuario asesor --nombre "Asesor demo" --actualizar

# Desactivar y revocar todas las sesiones de la cuenta.
python scripts/crear_usuario_local.py --usuario asesor --desactivar
```

No escribas contraseñas como argumentos ni en el chat. No exponer este servicio HTTP a Internet ni a una red pública. El modo local no proporciona MFA, recuperación por correo, auto-registro ni un servicio de identidad productivo.

## Volver a Azure

Para nuevas evaluaciones v2, DEM-02 versión 2.0 debe estar cargada en Search si se seleccionan documentos Azure. Este incremento actualiza solo catálogo local/cargador, no índice cloud; falta de guía falla controladamente sin usar reglas antiguas. [Score, margen, versiones y carga](REGLAS_RIESGO_DEMO.md).

[Activar modo Azure](<../../operacion/integraciones/Activar modo Azure.cmd>) cambia los tres proveedores a `azure`, mantiene la cuenta local habilitada y no borra llaves. Necesita recursos y credenciales Azure vigentes. Microsoft y la contraseña local son métodos de acceso; no determinan por sí solos el proveedor de IA.

Las rutas históricas `/api/v1/azure-search`, `/api/v1/azure-openai/estado` y `/api/v1/azure-ml` se conservan por compatibilidad. El laboratorio también usa `/api/v1/ml/estado` y `/api/v1/ml/predecir`; sus alias anteriores obedecen al mismo proveedor. El campo `proveedor` informa qué implementación atiende la petición. `/api/v1/proveedores/estado` exige sesión y publica solo metadatos sin llaves ni URLs privadas; `configurado` no garantiza conectividad. En ML local verifica la presencia/huella del artefacto, sin afirmar una consulta realizada o aptitud crediticia.

## Base de datos y respaldos

La migración 003 agrega `usuarios_locales` y `auth_intentos_locales`; no modifica evaluaciones ni revisiones antiguas. El respaldo enumera las tablas dinámicamente y ahora puede incluir hashes de cuentas y contadores de acceso: el dump sigue siendo privado y no cifrado. La evidencia histórica de restauración de tres tablas no demuestra una restauración actual de estas dos tablas nuevas.

La migración 004 agrega contadores separados de fallos/ráfagas y `cache_explicaciones` / `cuotas_explicaciones`. No cambia los resultados de riesgo, revisiones, nombres ni contraseñas. Las explicaciones completas ahora se conservan en una caché privada PostgreSQL: se reutilizan durante 24 horas con el mismo proveedor/modelo/versión; los errores se conservan un minuto. No se elimina automáticamente el texto vencido: deja de reutilizarse y puede sobrescribirse al renovar. La respuesta no incluye RFC, CURP, identidad ni claves de proveedor, pero el texto generado debe tratarse como privado. El identificador de evaluación relaciona internamente la caché; nunca se envía al modelo. Cuota de diez nuevas generaciones por cuenta y hora, compartida entre procesos; una respuesta en caché no consume cuota. No hay reintentos automáticos ni garantía de retención cero. Una interrupción del proceso o de la base durante una generación puede perder su resultado aunque el proveedor haya cobrado; consultar de nuevo tras recuperarlo puede consumir.

Si restauras una base con cuentas locales, rota `LOCAL_AUTH_SECRET` por otro secreto aleatorio fuerte para invalidar los JWT existentes y protege el archivo de respaldo. Las cuentas/password hashes seguirán en la base restaurada. No borrar el volumen PostgreSQL para cambiar de proveedor.

Actualización de segunda ronda: el intento de explicación se reserva y confirma en PostgreSQL antes de llamar al proveedor. No se pierde su contador por una excepción inesperada, interrupción o fallo posterior de escritura de caché. La cuota cuenta intentos, no cargos confirmados: también puede consumir un intento un fallo de configuración/TLS antes de enviar una solicitud. Un error inesperado devuelve un aviso saneado y queda disponible en caché un minuto, sin reintentar. Aún puede perderse una respuesta generada si el proceso o la base fallan después; no hay garantía exactly-once ni garantía de recuperar un texto cobrado. No desactivar la validación TLS para resolver un error de certificados.

Las nuevas evaluaciones bloquean pagos de créditos superiores a los gastos mensuales (deben incluirlos) y días de atraso pendientes con deuda actual cero. No se exige saldo positivo por el mero hecho de haber realizado pagos en el mes si no hay atraso; puede tratarse de un crédito ya liquidado. La API antigua puede omitir deuda/pagos/atraso y no se modifica el historial existente. Estas validaciones son de captura de la demo, no una nueva política de riesgo.

## Límites académicos

El candidato `model.pkl` AutoML existente no se carga como sustituto local: requiere un entorno compatible no integrado. El 12/10/2026 se añadió un modelo logístico independiente entrenado con scikit-learn y exportado a JSON numérico verificado. No se inventa una clasificación al fallar Azure ML ni se cambia de proveedor automáticamente. Consulta [operación, métricas y límites del laboratorio IA local](LABORATORIO_IA_LOCAL.md). La evaluación principal usa reglas ilustrativas y continúa funcionando; nunca es una decisión crediticia real.

Tener Azure implementado y documentado no acredita que la suscripción siga activa. El modo local no elimina ese código ni cambia evidencias pasadas. Ver [pruebas y generación real local del 11/10/2026](../evidencias/2026-10-11/acceso-local-y-ollama.md).
