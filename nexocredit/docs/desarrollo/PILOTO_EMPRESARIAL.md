# NexoCredit — piloto empresarial en sombra

## Alcance actual

Por petición del usuario, el objetivo vigente es una prueba empresarial controlada, no una presentación académica. **Eso cambia el criterio de aceptación, no convierte un modelo débil en fiable ni autoriza usar expedientes de clientes.** El usuario confirmó que aún no existe un historial empresarial autorizado y anonimizado con desenlaces posteriores al otorgamiento.

Se implementó un **piloto en sombra**: genera resultados y permite examinarlos, pero no crea decisiones crediticias automáticas ni actúa sobre cuentas o desembolsos. El servidor publica estado pendiente, motivos para no promover el modelo y comparaciones reproducibles. El software no se ha validado como motor de riesgo de una empresa y la instalación original abierta no se ha actualizado.

Los textos/evidencias académicos anteriores se conservan como antecedentes fechados, no como el alcance objetivo del piloto actual. Los identificadores API `modo=demostracion` y `reglas-demo-v*` se mantienen por compatibilidad e integridad histórica; no certifican una fase productiva ni se renombran registros antiguos. Las trece tecnologías obligatorias, los adaptadores Azure/Entra y sus campos de llaves permanecen.

## Mejoras ejecutadas

1. Protocolo de comparación escrito antes de ejecutar: [plan_piloto.json](../../inteligencia_artificial/prediccion_mexico/plan_piloto.json).
2. Tres algoritmos: regresión logística, Random Forest y Gradient Boosting, con parámetros prefijados. No búsqueda repetida hasta conseguir una cifra deseada.
3. Validación cruzada **anidada 5×3**, agrupada por UPM_DIS. Los 783 casos de prueba histórica, cuyo resultado ya conocíamos, quedan excluidos de este incremento. Se usan sólo los 3,123 casos de desarrollo.
4. Cada calibrador sigmoide utiliza predicciones internas fuera de muestra; no ve las etiquetas del fold externo. Los umbrales F1 se eligen dentro del entrenamiento de cada fold y son **provisionales técnicos**, no políticas empresariales aprobadas.
5. Predicciones externas completas y bootstrap por unidad de muestreo (300 remuestreos) con intervalos percentiles aproximados. No se versionan predicciones por persona ni datos de encuesta.
6. Estado en servidor y pantalla: `piloto_sombra`, validación empresarial pendiente, sin habilitación de decisiones/clientes reales. Informe con SHA-256 fijado; si falta/cambia, no se inventan mejoras.
7. Contrato y validador offline para un futuro historial empresarial autorizado, sin subir sus datos al servidor o servicios externos.

## Resultado real de la comparación

Estas cifras corresponden a **validación cruzada sobre desarrollo**, no a una prueba empresarial final. No es válido decir que el AUC de prueba anterior subió de 0.605 a 0.648: son conjuntos y procedimientos diferentes.

| Procedimiento | AUC | AP | Brier | IC 95 % aproximado AUC |
|---|---:|---:|---:|---|
| Regresión logística | 0.642223 | 0.362625 | 0.172764 | 0.616813–0.665406 |
| Random Forest | 0.648446 | 0.362479 | 0.172034 | 0.625436–0.669753 |
| Gradient Boosting | 0.646821 | 0.361969 | 0.172186 | 0.623992–0.669802 |
| Selección mediante validación interna | 0.644602 | 0.358044 | 0.172441 | 0.621223–0.666884 |

AP mayor favorece la comparación de ranking en esta población; Brier menor indica menor error probabilístico global, **no prueba por sí solo calibración**. El informe conserva frecuencias y estimaciones por intervalo para examinarlas, no una certificación de probabilidades de impago futuro.

Diferencia AUC Random Forest−logística: **+0.006222**, intervalo aproximado **−0.006378 a +0.018477**. Gradient Boosting−logística: +0.004597, intervalo −0.004898 a +0.013843. Ambos intervalos incluyen cero: **no se demostró una mejora consistente**. La logística conserva la mejor AP descriptiva por un margen mínimo. La selección anidada no aporta una mejora clara.

Por ello **no se modificó el modelo servido** ni su AUC de prueba 0.605496. Su SHA-256 sigue siendo `1f6238b217583d0f5c00320d9caf3c331e422452104776b9b99b57a75440e621`. Se mejoró el proceso de evaluación y control, no se fingió una ganancia predictiva.

Informe real: `backend/app/integraciones/prediccion_mexico/piloto/comparacion-v1/comparacion.json`, SHA-256 `50de28cba9113d3751bdfbc66d3857e40bfc3fba293f21c77e1fcb047ce70ea5`. Versiones observadas: Python 3.12.15, sklearn 1.9.1, NumPy 2.5.4 y pandas 3.0.6. Plan SHA-256 `4cc483f387b5f9daf8d45db560fe6abfc027a4e8eab3c2579af550e9140b6d5a`. Script SHA-256 `a61641b211e1b14ddb78b2babeaaf21b77317149d5f7f9240ebbf47311725608`.

## Controles implementados y límites

`GET /api/v1/modelo-mexico/piloto` exige sesión y devuelve `Cache-Control: no-store`. No existe POST de aprobación; enviar `habilitar=true` no cambia el estado. El formulario no puede modificar la gobernanza. `control_uso` y `comparacion_modelos` se conservan como parte del resultado de nuevas evaluaciones. Los registros previos sin esos campos siguen siendo legibles y se identifican como anteriores al control del piloto.

La interfaz distingue la prueba histórica del modelo servido de la comparación nueva. No promociona automáticamente al algoritmo con mayor cifra ni atribuye la precisión de ENIF a Ollama. Un informe alterado aparece «no disponible». Esto es un control de alcance/estado y de la ausencia de automatismos, **no un sistema DLP que impida físicamente teclear datos reales**. No certifica cumplimiento legal, privacidad de un archivo o seguridad empresarial completa.

## Historial futuro: contrato antes de entrenar

Validador: `python -m inteligencia_artificial.prediccion_mexico.validar_historial`. Sólo funciona localmente, emite conteos agregados y no entrena. Exige confirmación del operador `--datos-autorizados`, que no sustituye la verificación de permisos y anonimización. No usar datos de clientes mientras esa verificación no exista.

Una fila por crédito, CSV UTF-8, columnas exactas:

| Campo | Requisito |
|---|---|
| credito_id_anonimo | UUID opaco único; no RFC, contrato identificable o número de cuenta |
| persona_id_anonima | UUID estable para agrupar créditos de una misma persona sin identificarla |
| fecha_otorgamiento | Fecha de origen YYYY-MM-DD |
| fecha_captura_variables | No posterior al otorgamiento; evitar información futura |
| fecha_ultima_observacion | Entre origen y fecha de corte |
| ingresos_mensuales_al_otorgar | Positivo, capturado al origen |
| gastos_mensuales_al_otorgar | No negativo, capturado al origen |
| deuda_previa_al_otorgar | No negativa, excluye información posterior |
| cuota_mensual_pactada | No negativa, conocida al origen |
| monto_otorgado | Positivo |
| plazo_meses | Entero 1–600 |
| max_dias_atraso_en_horizonte | Resultado observado en el horizonte definido; no el atraso fuera de esa ventana |
| seguimiento_completo | `si` o `no`; falta de seguimiento no implica buen pagador |

Los importes admiten hasta dos decimales, sin separadores de miles ni códigos desconocidos como cifras. No se aceptan columnas extra con nombres, RFC, CURP o contactos. Comprobar ese esquema no garantiza anonimización: la empresa deberá revisar qué datos se pueden procesar, con qué fundamento/permiso, acceso, minimización, retención y seguridad.

La fecha de corte, el horizonte y el umbral de atraso son **parámetros obligatorios**, sin valores de negocio predeterminados. Este ejemplo exclusivamente sintético usa 365 y 90 para enseñar el comando, no para imponer la definición de incumplimiento:

```powershell
python -m inteligencia_artificial.prediccion_mexico.validar_historial --csv .local/historial_autorizado.csv --fecha-corte 2025-03-01 --horizonte-dias 365 --atraso-umbral-dias 90 --datos-autorizados
```

El validador detecta duplicados, fechas futuras respecto al corte, variables posteriores al origen, valores imposibles y resultados desconocidos. Los horizontes no maduros y seguimientos incompletos quedan fuera de las clases, no como «sin atraso». La salida no imprime UUID, importes ni contenido de las filas. Tampoco afirma suficiencia estadística, autorización, equidad o aptitud crediticia por tener dos clases.

**No existe todavía un entrenamiento empresarial con ese CSV** ni una importación al producto. Antes hay que aprobar la definición del desenlace y sus fuentes. La partición futura debe ser temporal y por persona; no se debe reutilizar un mismo cliente entre ajuste y prueba ni calibrar contra el test final.

## Condiciones para avanzar a uso real

- Historial autorizado y validado, con población y resultados posteriores pertinentes.
- Objetivo y horizonte acordados; costes de falsos positivos/negativos y umbrales de negocio definidos.
- Comparación con el proceso actual, calibración y validación independiente/temporal; revisión de sesgos, estabilidad y errores por segmentos.
- Prueba en sombra sobre nuevos casos autorizados, monitorización, reversión y revisión humana registradas.
- Aprobación operativa y revisión de requisitos de seguridad/privacidad aplicables. Ninguna está inventada o concedida por este documento.

No hay un número AUC universal ni una cantidad mágica de filas que apruebe el sistema. ENIF transversal no se convierte en historial prospectivo aunque se cambie el algoritmo. Referencias técnicas primarias: [validación cruzada](https://scikit-learn.org/stable/modules/cross_validation.html), [calibración](https://scikit-learn.org/stable/modules/calibration.html), [umbrales](https://scikit-learn.org/stable/modules/classification_threshold.html).

## Reproducción de la comparación

En un entorno aislado con `requirements-piloto.txt`, desde `nexocredit/`:

```powershell
python -m inteligencia_artificial.prediccion_mexico.comparar_piloto --zip C:\ruta\enif_2024_bd_csv.zip --salida C:\ruta\comparacion_nueva
```

Requiere el ZIP público con huella auditada del [modelo ENIF](../../inteligencia_artificial/prediccion_mexico/README.md); rechaza una salida existente y no reemplaza modelos. Las dependencias del informe son distintas de las del entrenamiento v1, ambas registradas. No consulta servicios externos ni necesita Azure/Ollama para el cálculo. No reutilizar el test histórico para tunear nuevas variantes hasta conseguir una cifra deseada.
