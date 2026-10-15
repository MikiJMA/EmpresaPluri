# IA predictiva local — 12/10/2026

Solicitud: ofrecer una alternativa de IA a Azure Machine Learning conservando su integración. Implementación local de un baseline UCI con scikit-learn, no sustitución de tecnologías obligatorias, publicación o validación de crédito real. No se involucró al asesor.

## Trabajo realizado y procedencia

- Entrenamiento StandardScaler + LogisticRegression independiente del AutoML anterior; 17.909 filas para ajuste, 6.136 para validación y 5.955 para prueba. Parámetros fijados sin búsqueda usando validación/prueba; solo entrenamiento ajusta escalado/coeficientes.
- Datos públicos académicos UCI, Taiwán 2005, NTD. Huellas/dimensiones de particiones comprobadas y cero grupos de predictores compartidos. Sin datos PostgreSQL, identificadores o cuatro variables demográficas.
- Entrenamiento realmente ejecutado en la imagen backend instalada, con red deshabilitada, raíz de solo lectura, 1 GB y dos CPU; únicamente datos/código y carpeta de salida montados, no secretos/volúmenes de trabajo.
- JSON numérico servido como `nexocredit-uci-logistica-v1`; SHA-256 `259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4`. Exportación contrastada contra `pipeline.predict` en 30.000 filas: cero discrepancias. No carga pickle/joblib ni el artefacto AutoML.
- Adaptador local, selector explícito, rutas autenticadas neutrales `/api/v1/ml/*` y alias `/api/v1/azure-ml/*`. Azure y deshabilitado conservados; no fallback ni clasificación inventada.
- React: **Laboratorio IA**, 19 entradas, ejemplo ficticio sin consulta automática, resultado con origen/modelo, retiro de resultados obsoletos, límites/métricas y aviso de extrapolación. No modifica `reglas-demo-v1`, evaluaciones, explicaciones Ollama o Power BI.

Entorno de entrenamiento observado: Python 3.12.15, scikit-learn 1.9.1, numpy 2.5.4, pandas 3.0.6. Parámetros, huellas y resultados están en [entrenamiento.json](../../../backend/app/integraciones/prediccion_local/artefactos/entrenamiento.json); procedimiento en [README IA local](../../../inteligencia_artificial/prediccion_local/README.md).

## Métricas reales

| Métrica | Validación | Prueba |
|---|---:|---:|
| Filas | 6.136 | 5.955 |
| AUC ROC | 0,718602 | 0,715048 |
| Exactitud | 69,92 % | 70,28 % |
| Sensibilidad positiva | 64,06 % | 60,92 % |
| Precisión positiva | 38,64 % | 37,51 % |
| F1 positivo | 48,20 % | 46,43 % |
| Exactitud siempre negativo | 78,15 % | 78,86 % |

Matrices: validación `[[3431,1364],[482,859]]`; prueba `[[3418,1278],[492,767]]`, con filas reales y columnas predichas en orden 0/1. El modelo detecta 767 de 1.259 positivos de prueba, omite 492 y produce 1.278 falsos positivos. No supera la exactitud del clasificador siempre negativo. No afirmar mejor precisión global ni validación de crédito real; tampoco trasladar métricas AutoML a este modelo.

## Pruebas ejecutadas

1. Suite backend completa: **165 pruebas aprobadas**, sin omisiones, con PostgreSQL real temporal aislado; migraciones repetidas sin diferencias. El contenedor de prueba usó `network=none` y almacenamiento temporal; el helper verificó su identidad/etiquetas y eliminó solo ese contenedor al terminar.
2. Frontend: **120 pruebas aprobadas**, ESLint y compilación Vite aprobados en Docker. Las pruebas del ML local cubren captura estricta, contrato/huella, mensajes de proveedor, 19 campos, métricas/baseline, procedencia/escapado, Azure conservado y guardas de intentos obsoletos. Se corrigió una fixture de test para que el frontend no necesite copiar archivos backend en su build.
3. Cinco archivos de pruebas PowerShell aprobados. El modo local selecciona ML local y conserva secreto/modelo Ollama/llaves Azure existentes; repetición de configuración cubierta sin restablecer la cuenta.
4. Pruebas ML backend incluyen clases positiva y negativa reales, huella/métricas, alias, 401 sin identidad, 422 de entradas inválidas, 503 ante archivo ausente/alterado, ausencia de HTTP/deserialización/guardado y proveedores Azure/deshabilitado. Las pruebas de contrato con identidad inyectada no acreditan una nueva sesión humana.
5. Auditoría `npm audit --audit-level=high` **no completada**: fallo de cadena TLS («unable to verify the first certificate»). No se desactivó validación SSL ni se afirmó cero vulnerabilidades en esta ejecución. Las auditorías históricas tienen su fecha; no sustituyen la actual. No se añadieron dependencias para este incremento.

## Aplicación local y conservación

Respaldo privado creado antes de reconstruir: `.local/respaldos_postgresql/20261012T195505Z-cd9180a4696c`. El dump es privado/no cifrado; no se adjunta ni publica.

Se cambió únicamente `ML_PROVEEDOR` de deshabilitado a local en el `.env` privado Git-ignorado. Backend/frontend se reconstruyeron y recrearon con Compose `--no-deps --pull never --wait`; ambos saludables. PostgreSQL no se recreó: su identidad/imagen y las huellas completas de datos/esquema/vistas de las doce tablas coinciden exactamente con el manifiesto previo. Conservadas **9 evaluaciones, 2 revisiones y 1 cuenta local**; tablas de créditos/cuotas/pagos/eventos/alertas siguen vacías. No hay nueva migración.

Comprobación después del despliegue:

- Frontend localhost:8080 devuelve 200 y referencia el nuevo bundle `index-b1zYClYD.js`.
- `GET /api/v1/ml/estado` sin sesión devuelve 401, con autenticación intacta.
- Ejecución directa del adaptador empaquetado en el backend: artefacto configurado/huella correcta y clase No incumplimiento sobre 19 valores ficticios, origen scikit-learn local, sin variables fuera de rango. No acredita sesión de navegador o validez de una solicitud real.

## Revisión visual

Vista estática aislada con los componentes React actuales, métricas del artefacto y usuario ficticio; no inicia MSAL, ejecuta consultas ni guarda datos. Desktop de 1.280 px: 19 entradas, sin desbordamiento horizontal del documento, bordes de tarjetas/inputs/botones a 0 px y fondo existente conservado. Móvil en iframe de 390 px: 19 entradas, controles dentro del ancho disponible y documento sin desbordamiento; navegación horizontal propia del diseño móvil.

Captura local de QA: `output/revisiones_visuales/2026-10-12/laboratorio-ia-local.jpg`. No es una captura de nueva sesión humana ni de una consulta en el navegador de trabajo. El servidor/las pestañas temporales se cierran al terminar.

Estas rutas son relativas a la raíz exterior del espacio de trabajo. Las capturas son privadas y locales; no se incluyen en la publicación ni en el paquete de entrega.

## Límites y pendientes

Datos antiguos de Taiwán, particiones agrupadas no temporales, clase ponderada y ausencia de calibración/fairness/piloto mexicano. No probabilidad de crédito real, score de Buró, aprobación, rechazo o verificación oficial. El nuevo modelo no sirve las entradas financieras del formulario principal; no valida los objetivos productivos originales.

No se comprobó nueva conectividad Azure, vigencia de suscripción, CI remota, carga masiva o sesión humana del laboratorio actualizado. No se desplegó públicamente, alteró main, creó cuentas o contactó al asesor. [Manual de uso](../../manuales/LABORATORIO_IA_LOCAL.md); Azure sigue siendo opción explícita y requisito final.
