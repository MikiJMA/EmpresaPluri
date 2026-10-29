# Modelo mexicano experimental · ENIF 2024

## El modelo en 5 minutos

**¿Qué predice?** Si una persona que ya tiene un crédito formal declaró haberse atrasado en algún pago durante el último año. No predice impagos futuros ni calcula una probabilidad de incumplimiento.

**¿De dónde salen los datos?** De la [Encuesta Nacional de Inclusión Financiera 2024](https://www.inegi.org.mx/programas/enif/2024/) (ENIF) del INEGI: 3,906 personas mayores de edad con ingreso laboral y al menos un crédito formal. Son datos públicos de encuesta, no expedientes crediticios.

**¿Qué variables usa?** 15 respuestas del encuestado: ingreso laboral y su periodicidad, si el ingreso es fijo o variable, si lleva presupuesto, si le alcanza para los gastos, cuánto tiempo cubriría con ahorros, y cuáles productos de crédito tiene (tarjeta bancaria, automotriz, hipotecario, etc.). **No usa** el score, RFC, edad, sexo ni los datos en pesos del formulario principal.

**¿Qué tan bien funciona?** El AUC de prueba es **0.605** (un clasificador al azar tendría 0.5 y uno perfecto 1.0). Detecta al 72 % de quienes sí se atrasaron, pero de cada 4 alertas sólo 1 es correcta. Esto significa que el modelo **distingue patrones asociados con el atraso mejor que el azar, pero con capacidad limitada**. No debe usarse como único criterio para aprobar o rechazar un crédito.

**¿Por qué aparece como segunda opinión?** Porque complementa las reglas de negocio (score + margen) con una perspectiva estadística independiente. Las reglas dicen si el perfil financiero capturado cae en una zona de riesgo; el modelo dice si el patrón de la persona se parece al de quienes declararon atrasos en la encuesta. Ambos se muestran juntos para que un analista los considere, no para que uno sustituya al otro.

---

Uso vigente: componente de un **piloto empresarial en sombra**. Hay una comparación adicional de tres modelos, calibración interna e intervalos de incertidumbre; no se demostró una mejora consistente y se conserva este artefacto v1 sin promoverlo como apto para decisiones reales. [Resultados y condiciones empresariales pendientes](../../docs/desarrollo/PILOTO_EMPRESARIAL.md).

Modelo **entrenado y conectado al POST principal `/api/v1/evaluar`**, no una carpeta preparada ni una respuesta de Ollama. Clasifica patrones asociados con algún atraso reportado en una encuesta mexicana. **No es un predictor validado de incumplimiento futuro** y no se promueve como motor de aprobación.

## Origen y autorización de uso

Fuente: INEGI/CNBV, [Encuesta Nacional de Inclusión Financiera 2024](https://www.inegi.org.mx/programas/enif/2024/), microdatos de uso público. [Metadatos y condiciones de acceso](https://www.inegi.org.mx/rnm/index.php/catalog/1081), [diccionario TMODULO](https://www.inegi.org.mx/rnm/index.php/catalog/1081/data-dictionary/F42). Consulta/descarga: 15/10/2026. INEGI no elaboró, avaló ni certificó este modelo.

- ZIP oficial: `https://www.inegi.org.mx/contenidos/programas/enif/2024/microdatos/enif_2024_bd_csv.zip`.
- SHA-256 ZIP: `00e4b0b42775276b2da236a5bba8c64dc5a92c289908a4727dec93dc7684f039`.
- TMODULO: 13,502 entrevistas, 398 variables. SHA-256 CSV: `5f1be142073f5758cbfb302fd7fb5dbf89c006b00729994207a9f05a46e1b8fd`.
- No se versionan el ZIP ni los registros de encuesta: sólo código, parámetros numéricos y un informe agregado sin personas identificadas.

## Población y objetivo

Casos completos de personas de la encuesta (18 años o más) con ingreso laboral positivo declarado y al menos un crédito formal. Se excluyen 8,254 personas sin crédito formal, 13 con respuesta desconocida/no declarada sobre el atraso de algún producto que poseen y 1,329 por perfil incompleto/no elegible. Quedan **3,906** observaciones. No se considera «sin crédito» equivalente a «no se atrasó».

Etiqueta: 1 cuando alguna `P6_3_1` a `P6_3_9` de los créditos poseídos declara atraso; 0 sólo cuando todas las respuestas aplicables son «No». Blancos por salto, «No responde» y «No sabe» no se convierten en cero. Las preguntas se refieren al periodo entre junio de 2023 y la entrevista de 2024, no a resultados futuros.

## Entradas y correspondencia con el formulario

| Entrada declarada | Variable ENIF | Tratamiento |
|---|---|---|
| Ingreso laboral por periodo | P3_11A | `log1p`, positivo; 98,000 es tope de captación; 99,888 es rechazo y se excluye |
| Periodicidad | P3_11B | Semana, quincena, mes, año; one-hot, sin conversión monetaria supuesta |
| Ingreso fijo o variable | P3_12 | Categoría 1/2 |
| Registro de presupuesto | P4_1 | Categoría 1/2 |
| Ingreso suficiente para gastos en 12 meses | P4_3 | Categoría 1/2; asociación contemporánea, no información previa al desenlace |
| Tiempo cubierto con ahorros sin ingresos | P4_10 | Categoría 1 a 5 |
| Productos de crédito formal | P6_2_1 a P6_2_9 | Nueve indicadores de tenencia |

Son **15 entradas originales / 25 características numéricas** tras logaritmo y one-hot. La misma función `vectorizar()` se usa al entrenar y evaluar. El ingreso del perfil no se rellena desde el ingreso total mensual: representan preguntas distintas. No se extraen variables de RFC/CURP ni se transforman datos MXN a las variables UCI de Taiwán.

Se excluyen el objetivo `P6_3_*`, la frecuencia de atraso `P6_4_*`, los indicadores directos de atrasos `P4_4_7`/`P4_6_2`, la percepción de pago `P6_7`, el score capturado, días de atraso, identificadores, sexo, edad, origen étnico y discapacidad. Esta selección evita atajos directos al objetivo; **no acredita ausencia de sesgo**. P4_3 y las demás covariables son contemporáneas: no se puede demostrar precedencia temporal o causalidad.

## Entrenamiento y prueba

StandardScaler + LogisticRegression L2. Partición por `UPM_DIS` con GroupShuffleSplit y semillas 20261015/20261016. Ninguna unidad de muestreo se comparte entre entrenamiento (2,333), validación (790) y prueba (783). Partición aleatoria por conglomerados, no temporal ni validación prospectiva. El escalador sólo se ajusta en entrenamiento. Se comparan C = 0.1, 1 y 10 exclusivamente en validación; gana C=10 por AUC. Umbral **0.18**, elegido por F1 en validación, no por score ni margen. Prueba no utilizada para seleccionar C o umbral. No hay categorías manuales Bajo/Medio/Alto en este modelo.

Resultados de prueba:

| Métrica | Resultado |
|---|---:|
| AUC ROC | 0.605496 |
| Average precision | 0.334050 |
| Brier | 0.174866 |
| Sensibilidad | 71.58 % |
| Precisión positiva | 26.73 % |
| F1 | 0.389302 |
| Exactitud | 47.51 % |
| Exactitud de predecir siempre «sin atraso» | 76.63 % |

Matriz `[[TN, FP], [FN, TP]]`: `[[241, 359], [52, 131]]`. Hay muchos falsos positivos. La baseline probabilística constante utiliza la prevalencia de entrenamiento; su AUC es 0.5, AP 0.233716 y Brier 0.179099. Con el mismo umbral 0.18 clasifica a todos como positivos (F1 0.378882). La mejora es modesta: **no se presenta como listo para crédito real**. Las métricas no usan factores de expansión, intervalos de diseño de encuesta ni validación de equidad; no son estimaciones nacionales.

## Reproducción

Desde `nexocredit/`, usar Python 3.12 y las versiones de `requirements-entrenamiento.txt` en un entorno aislado. Descargar el ZIP desde INEGI, respetando sus condiciones. No son necesarias llaves Azure ni un modelo Ollama.

```powershell
python -m pip install -r inteligencia_artificial/prediccion_mexico/requirements-entrenamiento.txt
python -m inteligencia_artificial.prediccion_mexico.entrenar --zip C:\ruta\enif_2024_bd_csv.zip --salida C:\ruta\salida_nueva
```

El script rechaza otra huella ZIP y una carpeta de salida ya existente. Produce `modelo.json` y `entrenamiento.json`, sin datos individuales. Contraste JSON–sklearn de las 3,906 filas: error máximo observado 0.0. Python 3.12.14, sklearn 1.9.1, pandas 3.0.1, numpy 2.3.5. Las plataformas/versiones pueden variar mínimamente los coeficientes; no sustituir el artefacto servido sin nueva revisión, prueba y versión.

Artefacto integrado: `backend/app/integraciones/prediccion_mexico/artefactos/modelo.json`; SHA-256 `1f6238b217583d0f5c00320d9caf3c331e422452104776b9b99b57a75440e621`. Inferencia sólo con biblioteca estándar, Pydantic y parámetros numéricos verificados, sin cargar pickle. El cliente falla cerrado si falta/cambia el archivo. El informe completo incluye las versiones y métricas de cada conjunto.

## Alcance y pendientes

El modelo aparece primero en la evaluación y en su detalle; las reglas se conservan como comparación y siguen alimentando el dashboard histórico. Su salida asociativa **no es PD calibrada ni un score de Buró**. Ollama/Azure no deciden esta clase. La inferencia no requiere servicios externos. El perfil es opcional para compatibilidad y para personas no elegibles; si falta se anuncia «sólo reglas» sin inventar un resultado ML.

Para un predictor de impagos futuros se necesitan datos longitudinales autorizados, variables disponibles antes del préstamo, desenlaces posteriores, validación temporal, calibración, controles de sesgo y revisión humana. No se sustituyen esas evidencias por etiquetas sintéticas ni por una respuesta generativa.
