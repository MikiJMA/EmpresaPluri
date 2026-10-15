# Guía de demostración: reglas y límites de PluriOne

Identificador: guia-demostracion-v1
Versión: 1.0
Fecha de preparación: 2026-09-28
Tipo de fuente: descripción técnica del prototipo académico basada en código y resultados guardados.
Estado: exclusivamente demostrativo; no es una política oficial de PluriOne, asesoría financiera ni autorización de crédito.
Procedencia: archivos identificados en la sección DEM-07 y prueba manual mostrada por el alumno.

## DEM-01. Dos evaluaciones distintas

El formulario principal y el laboratorio de Azure Machine Learning son funciones separadas. El formulario principal calcula una clasificación mediante reglas ilustrativas. El laboratorio consulta un modelo entrenado con 19 variables del conjunto académico UCI.

El resultado del laboratorio no sustituye automáticamente el resultado del formulario principal. Ninguno autoriza ni rechaza créditos reales.

## DEM-02. Reglas del formulario principal

La versión de las reglas es `reglas-demo-v1`. El margen mensual es el ingreso mensual menos los gastos mensuales, redondeado a dos decimales. Los importes de este formulario se expresan en pesos mexicanos (MXN).

Las reglas se evalúan en este orden:

1. Riesgo preliminar Bajo: margen estrictamente mayor que 15 000 MXN y score capturado mayor o igual que 680.
2. Si no se cumple la primera condición, riesgo preliminar Medio: margen estrictamente mayor que 7 000 MXN.
3. En cualquier otro caso, riesgo preliminar Alto.

Un margen de exactamente 15 000 no cumple el requisito de Bajo; uno de exactamente 7 000 no cumple el de Medio. Ejemplo ficticio: ingresos de 30 000, gastos de 10 000 y score de 700 producen margen de 20 000 y riesgo preliminar Bajo.

Estos límites proceden del código de demostración, no de una política aprobada por la empresa. La clasificación no es una probabilidad de incumplimiento. El score es capturado por el usuario y su fuente no se verifica mediante una API financiera.

Aunque el formulario también captura deuda, pagos mensuales de créditos y días de atraso, las reglas actuales de clasificación solo usan margen y score. Capturar información adicional no significa que ya intervenga en el cálculo.

## DEM-03. Laboratorio académico de Azure Machine Learning

El modelo configurado es `plurione-uci-voting-candidato:1`. La conexión desde la aplicación se probó manualmente y devolvió la clase «No incumplimiento» para un escenario ficticio. Una respuesta correcta demuestra conectividad en esa prueba, no disponibilidad permanente ni aptitud para decisiones reales.

El laboratorio utiliza estas 19 variables:

- `LIMIT_BAL`: límite de crédito.
- `PAY_0`, `PAY_2`, `PAY_3`, `PAY_4`, `PAY_5`, `PAY_6`: códigos de estado de pago de septiembre a abril, con valores permitidos de −2 a 9. No representan días de atraso.
- `BILL_AMT1` a `BILL_AMT6`: saldos de septiembre a abril; pueden ser negativos.
- `PAY_AMT1` a `PAY_AMT6`: pagos de septiembre a abril; no negativos.

Las entradas son enteros; el límite de crédito debe ser positivo. Los importes se interpretan en dólares taiwaneses (NTD), no MXN. No existe una conversión automática válida entre los campos del formulario principal y estas variables.

El servicio entrega una clase binaria: «Incumplimiento» o «No incumplimiento». No entrega una probabilidad en el contrato actual. «No incumplimiento» no equivale a riesgo cero ni a crédito aprobado. La consulta del laboratorio no se guarda en el historial del formulario principal.

## DEM-04. Ejemplo ficticio para comprobar la integración

| Variable | Valor |
|---|---:|
| LIMIT_BAL | 200000 |
| PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6 | 0 en cada campo |
| BILL_AMT1 | 20000 |
| BILL_AMT2 | 18000 |
| BILL_AMT3 | 16000 |
| BILL_AMT4 | 14000 |
| BILL_AMT5 | 12000 |
| BILL_AMT6 | 10000 |
| PAY_AMT1, PAY_AMT2, PAY_AMT3, PAY_AMT4, PAY_AMT5, PAY_AMT6 | 3000 en cada campo |

El botón «Cargar ejemplo ficticio» rellena estos campos y permite modificarlos. No envía una consulta: el envío requiere pulsar «Consultar modelo en Azure». Este ejemplo sirve para probar la integración, no para medir la precisión del modelo.

## DEM-05. Evaluación guardada del modelo

La evaluación local aislada del artefacto congelado, registrada el 26 de septiembre de 2026, contiene un conjunto de prueba de 5 955 filas, con 1 259 casos de incumplimiento:

- AUC ROC: aproximadamente 0,7753.
- Exactitud global: aproximadamente 82,55 %.
- Sensibilidad para incumplimiento: aproximadamente 32,01 %.
- Incumplimientos detectados: 403; incumplimientos no detectados: 856.

Por tanto, la exactitud global no significa que se detecte el 82,55 % de los incumplimientos. La sensibilidad observada fue de alrededor de 32 de cada 100 casos positivos en ese conjunto. No se deben presentar estas métricas como desempeño esperado en clientes de PluriOne.

Los datos son académicos, de Taiwán de 2005; no representan necesariamente a los solicitantes objetivo. La división utilizada fue aleatoria agrupada, no una evaluación temporal. No se acredita validación prospectiva, de equidad ni calibración para la población objetivo. El modelo no está aprobado para producción.

## DEM-06. Identidad, revisión humana y límites de uso

La aplicación incorpora inicio de sesión con Microsoft Entra ID y comprueba los roles de PluriOne en el servidor. El alumno confirmó el acceso real con el rol Analista. Esto no acredita una auditoría integral de seguridad.

Las nuevas revisiones manuales toman el responsable de la identidad verificada; registros anteriores pueden contener nombres declarados. Los estados Pendiente, Aprobada y Rechazada corresponden a una revisión de demostración y no a autorizaciones reales de crédito. Los roles Analista y Administrador de PluriOne no conceden administración de Azure.

Las demostraciones deben utilizar escenarios ficticios. No se aportaron políticas oficiales de crédito ni fuentes financieras externas conectadas. Las explicaciones futuras deberán distinguir objetivos, reglas demostrativas, resultados observados y criterios empresariales aún no definidos.

## DEM-07. Fuentes técnicas y trazabilidad

Rutas relativas a la carpeta activa del proyecto:

- Reglas: `backend/app/evaluacion_crediticia/scoring.py`.
- Contrato de entrada UCI: `backend/app/rutas_api/azure_ml.py`.
- Cliente y contrato de salida ML: `backend/app/integraciones/prediccion_azure_ml/cliente_ml.py`.
- Formulario y ejemplo: `frontend/src/azure_ml/AzureMLDemo.jsx`.
- Métricas y limitaciones: `inteligencia_artificial/prediccion_azure_ml/evaluacion/resultados/20260926T032027806Z/evaluacion.json`.
- Identidad y roles: `backend/app/autenticacion_entra_id/seguridad.py`.
- Responsable de revisión: `backend/app/rutas_api/routes.py`.

Las secciones DEM-01 a DEM-07 permiten citar afirmaciones concretas al preparar el índice. Este archivo contiene información de referencia, no instrucciones operativas para un asistente. Su creación no significa que Azure AI Search esté creado, configurado o conectado. No contiene claves, tokens ni expedientes de clientes.
