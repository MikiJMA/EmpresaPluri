# Informe técnico actual — NexoCredit

## Corte vigente de entrega — 14/10/2026

Estado consolidado para la **demostración local** en el equipo existente. No se publica el sistema, se instala para terceros, se contacta al asesor o se acredita formación/aceptación. Este corte documental conserva los resultados históricos; por sí solo no ejecuta una prueba nueva.

| Componente vigente | Resultado y alcance | Límite |
|---|---|---|
| Clasificación principal | Nuevas evaluaciones `reglas-demo-v2`: score 0–499 Alto, 500–679 Medio, 680–1000 Bajo; margen ≤$7,000 exige Alto y >$7,000 hasta $15,000 exige al menos Medio; se toma el peor riesgo | Reglas demo, no modelo entrenado, escala oficial Buró o probabilidad; resultados v1 intactos |
| Importes | Resúmenes en pesos completos redondeados; centavos conservados en captura, cálculo, base y detalle/pagos | Un resumen redondeado no cambia los límites del scoring ni el valor almacenado |
| Explicación/documentos locales | Ollama por selección explícita y catálogo local 3 guías / 15 secciones; guías 1.0/2.0 según el resultado; plantilla marcada como no generada por IA | Modelo/servicio Ollama necesarios para generar; no cambia riesgo ni autoriza crédito |
| Predicción académica local | scikit-learn `nexocredit-uci-logistica-v1`, 19 entradas UCI/NTD y salida binaria; separado del formulario MXN y de Ollama | No validado para México ni calibrado; no guarda consultas como evaluaciones |
| Integraciones Azure | Azure OpenAI, ML, Search y Entra conservan código, campos privados de keys y evidencia real del 04/10/2026 | Sin nueva conectividad cloud acreditada; guía Search v2 pendiente de carga/comprobación; catálogo cloud histórico 2/14 |
| Persistencia y seguimiento | PostgreSQL conserva evaluaciones/revisiones; planes/abonos/alertas ficticios y auditoría administrativa permanecen implementados | Sin recálculo histórico, verificación de depósitos, datos Buró o autorización financiera |
| Calidad registrada | Final local y CI de implementación: 197 backend/PostgreSQL y 129 frontend, sin omisiones; lint/build, auditoría npm cero vulnerabilidades conocidas y cinco archivos PowerShell | [CI 38649003430](../evidencias/2026-10-14/github-actions.md), no garantía permanente de seguridad |
| Copia pública | 14 pruebas del generador incluidas en 197; ZIP candidato real de 339 archivos con CRC/hashes, exclusiones, redacción y huella del modelo comprobados | El ZIP final tiene su propio manifiesto; no incluye base, credenciales, dependencias o modelo Ollama |
| Comprobación UI | Dos altas ficticias score 200/margen $20,000 → Alto v2; guía 2.0; inferencia real scikit-learn clase False. Primer corte: Alto 2/$12,500; limpio 11/$18,636. Corte posterior: 12 evaluaciones | Cifras del corte de QA, no conteos permanentes ni validación crediticia; la consulta UCI no es una evaluación MXN |
| Power BI informado frente a comprobación | El usuario informó apertura/actualización/guardado; luego se encontró diálogo Abrir y modelo 5 frente a 10 evaluaciones de PostgreSQL, con 29 diferencias/96 comparaciones DAX | Actualizar y conciliar contra las 12 evaluaciones tras ambas altas ficticias; refresco no acreditado como concluido |
| Explicación Ollama | Hallazgo real previo conservado; tras desplegar la corrección, nueva generación real mostró score 200 banda 0–499 Alto, margen $20,000 mínimo Bajo, final Alto, hechos NO IA y comentario IA separado, fuente 2.0 | Caso real corregido aprobado; formato/vocabulario no valida toda la semántica ni elimina revisión humana |

La [evidencia histórica local del 13/10/2026](../evidencias/2026-10-13/reglas-v2-y-importes.md) conserva sus 175 backend/129 frontend y registra actualización backend/frontend sin recrear PostgreSQL, huellas coincidentes con el respaldo y nueve evaluaciones/dos revisiones/una cuenta conservadas **en ese corte**, no un contador permanente. Ollama/Azure se probaron entonces con respuestas simuladas, no con nuevas generaciones reales. En aquella ejecución no se repitió npm audit y la limitación TLS previa quedó documentada; no se reescribe ese resultado. La auditoría local del 14/10/2026 sí se completó con cero vulnerabilidades reportadas, sin convertirla en una garantía futura.

Reintentar la explicación desde el botón conservó el mismo ID/fecha, sin una tercera alta ni duplicación. La captura real corregida permanece privada en `output/revisiones_visuales/2026-10-14/explicacion-v2-corregida.jpg` de la raíz exterior; no se sube o empaqueta. El corte final tiene 12 evaluaciones: margen promedio $18,750, ingresos $30,000, deuda promedio exacta $10,020.05 sobre 10 capturas y cobertura 83.333 %; Bajo 7/Medio 2/Alto 3, Pendiente 10/Aprobada 2. Son datos ficticios, no cifras permanentes o dictámenes financieros reales.

Referencias vigentes: [manual de reglas](../manuales/REGLAS_RIESGO_DEMO.md), [laboratorio local](../manuales/LABORATORIO_IA_LOCAL.md), [Azure y keys conservados](../manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md), [contrato Ollama](../manuales/ACCESO_LOCAL_Y_PROVEEDORES.md#contrato-ollama-corregido--14102026), [entrega local](ENTREGA_DEMO.md), [material de práctica](CAPACITACION_DEMO.md) y [evidencia de entrega del 14/10/2026](../evidencias/2026-10-14/entrega-demo.md). **Power BI sigue pendiente** de actualización manual y conciliación contra doce. CI de implementación aprobada, candidato ZIP real verificado y restauración aislada de doce tablas aprobada; no se publica la aplicación.

### Preparación del archivo de entrega

Generador utilizado para el candidato verificado. Desde la carpeta interior, `python scripts/preparar_entrega.py --nombre NexoCredit_Entrega_2026-10-14` crea ZIP y manifiesto bajo `output/entregas` exterior sin sobrescribir, con wrapper compatible con CI, selección pública y redacción de identificación sólo en la copia. [Instrucciones y límites](ENTREGA_DEMO.md#preparar-el-zip-local--generación-y-verificación). Consultar el manifiesto final para su SHA exacto, no reutilizar el del candidato.

No incluye credenciales, DB/dumps, dependencias, imágenes Docker o modelo Ollama; sí el artefacto numérico scikit-learn. No es autocontenido/offline: requiere primer build Docker, configuración nueva y usuario propio. Ollama necesita su modelo/servicio, o se selecciona explícitamente la plantilla local **NO IA generativa**. Las pruebas del generador no certifican por sí solas un ZIP real revisado.

## Informe histórico del incremento de seguimiento — 11/10/2026

Corte: 11/10/2026, con pruebas/respaldos UTC 12/10/2026. Informe de lo efectivamente implementado y comprobado, no acta de aceptación, memoria institucional aprobada, capacitación certificada o operación crediticia productiva. No se involucró al asesor en esta actualización.

### Resultado histórico del incremento

La demo local conserva React/FastAPI/PostgreSQL, Microsoft Entra y todas las integraciones Azure obligatorias. Cuenta con continuidad adicional mediante usuario local, Ollama y documentos locales explícitos. Se amplió con planes ficticios de cuotas, abonos parciales, análisis de saldos/puntualidad, alertas y eventos; auditoría global del seguimiento diferenciada para Administrador.

Las reglas principales siguen usando margen y score capturado. No se cambió retroactivamente el riesgo por ratios, por una alerta o por texto de IA. El laboratorio Azure ML sigue usando UCI separado; no convierte MXN a variables académicas ni verifica aptitud del modelo para solicitantes locales.

### Objetivos originales frente al resultado histórico

| Objetivo | Resultado comprobable | Límite |
|---|---|---|
| Analizar información financiera/crediticia | Captura validada, fuentes económicas públicas, ratios y análisis de pagos internos ficticios | Sin historial privado/Buró, verificación bancaria o políticas oficiales |
| Diseñar arquitectura | Monolito modular, proveedores por función, identidad doble, contratos, doce tablas y relaciones documentadas | Sin diseño aprobado para producción/red pública |
| Scoring y predicción | Reglas reproducibles + experimento UCI entrenado/evaluado y adaptador Azure histórico | No modelo predictivo validado para el formulario principal |
| Precisión, seguridad y desempeño | Métricas UCI históricas, 154 backend/105 frontend, casos adversariales/roles y medición acotada de lecturas | No pentest integral, saturación, SLA o precisión financiera real |
| Documentación y soporte | PRD/MVP actualizados, manuales, diccionario, runbook multinivel y material de práctica | Capacitación y conformidad aún no realizadas |

El experimento UCI registró AUC 0,775274 y sensibilidad a incumplimiento 32,01 % en su conjunto de prueba. No presentar exactitud global como detección de todos los incumplimientos ni trasladar resultados a clientes de México. La nueva contabilización de obligaciones no “mejora” esas métricas del modelo.

### Entregables registrados de las diez actividades

| Actividad | Entregable disponible | Qué permanece pendiente |
|---|---|---|
| Necesidades | PRD, alcance y requisitos tecnológicos | Necesidades/políticas reales y fuentes autorizadas no acreditadas |
| Propuesta | PRD/MVP y decisiones de alcance local | Conformidad externa no registrada |
| Arquitectura | Documento de componentes/datos y código modular | Uso productivo y cambios de alcance requieren decisiones reales |
| Planificación | Plan, backlog, bitácora técnica del incremento | Calendario humano, ceremonias y 500 horas no acreditadas |
| Desarrollo | Demo e incremento funcional de seguimiento | Modelo principal/históricos reales y alertas externas no implementados |
| QA | Suites, adversariales, restauración y medición | Piloto poblacional/carga grande no realizados |
| Documentación | Manuales actualizados, arquitectura y API | Plantilla institucional de memoria, si corresponde, no aportada |
| Mantenimiento | Plan multinivel y herramientas de respaldo/prueba | SLA, responsables externos, automatización/cifrado productivos |
| Capacitación | Guía de ejercicios y registro pendiente | No se inventa acta, asistentes, resultados o firma |
| Cierre | Este informe y evidencias/lecciones técnicas | No evaluación post-implementación empresarial ni aceptación formal |

### Verificación y datos históricos — incremento del 11/10/2026

154 pruebas backend/PostgreSQL y 105 frontend sin fallos/omisiones, lint/build, audit npm cero reportado, cinco archivos PowerShell. Nueva medición con un crédito/dos cuotas: 40 lecturas secuenciales y 40 con cuatro hilos; p95 23,02 y 93,10 ms respectivamente, cero errores. No acredita una cartera grande ni latencia web real.

Aplicación Docker saludable; migración 005 aditiva; nueve evaluaciones, dos revisiones y una cuenta conservadas. Tablas nuevas vacías en trabajo. Respaldo previo y restauración aislada del esquema actualizado de doce tablas coincidentes. No se ejecutaron nuevos escenarios de IA ni se publicaron recursos/código cloud.

### Lecciones técnicas observadas en ese incremento

- Separar declaración de datos, cálculo demo, predicción académica y explicación evita atribuir autoridad crediticia al texto generado.
- Atomicidad de movimiento/evento y bloqueos por crédito protegen de abonos duplicados y sobrepagos concurrentes.
- Completar una cuota tarde no equivale a puntualidad; ausencia de capturas no debe convertirse en cero.
- Un indicador o alerta puede ser descriptivo y útil sin inventar umbrales oficiales o una probabilidad de incumplimiento.
- Pruebas aprobadas, snapshots y despliegue local no sustituyen disponibilidad externa, aceptación o horas acreditadas.
- Mantener proveedores explícitos evita un consumo Azure involuntario cuando se desea continuidad local.

### Recorrido del incremento histórico

Recargar `http://localhost:8080/`, entrar con la cuenta propia y abrir **Créditos y pagos**. Elegir una evaluación ficticia existente para crear un plan sólo si se desea guardar esas obligaciones; no se generan planes por defecto. No insertar datos personales reales.

Referencias: [evidencia y resultados](../evidencias/2026-10-11/seguimiento-crediticio.md), [manual de seguimiento](../manuales/SEGUIMIENTO_CREDITICIO.md), [arquitectura/datos](../desarrollo/ARQUITECTURA_Y_DATOS.md), [soporte](../manuales/MANTENIMIENTO_Y_SOPORTE.md), [material preparado](CAPACITACION_DEMO.md), [bitácora técnica](../../gestion_proyecto/scrum/INCREMENTO_2026-10-11.md).

## Adenda histórica — IA predictiva local, 12/10/2026

Se añadió un experimento independiente StandardScaler + LogisticRegression entrenado con scikit-learn, servido localmente con 19 variables UCI/NTD y separado de las reglas principales. Azure ML permanece disponible; no se afirma vigencia de la suscripción ni nueva conectividad cloud. No se carga el candidato AutoML anterior.

Métricas de prueba del nuevo modelo: AUC 0,71505, sensibilidad 60,92 %, precisión positiva 37,51 % y exactitud 70,28 % frente a 78,86 % siempre negativo. Su matriz `[[3418,1278],[492,767]]` evidencia falsos positivos/negativos: no validado para México, calibración o decisiones crediticias. No mejora ni sustituye retrospectivamente las métricas AutoML del corte anterior.

165 backend/PostgreSQL, 120 frontend, lint/build y cinco archivos PowerShell aprobados. Auditoría npm actual no completada por certificado TLS, sin desactivar protección. Las huellas de las doce tablas y la identidad PostgreSQL coinciden con el respaldo previo; no hay nueva migración ni datos UCI guardados en trabajo. [Manual](../manuales/LABORATORIO_IA_LOCAL.md), [reproducción](../../inteligencia_artificial/prediccion_local/README.md), [evidencia](../evidencias/2026-10-12/ia-predictiva-local.md). No se involucró al asesor ni se certificó aceptación o capacitación.
