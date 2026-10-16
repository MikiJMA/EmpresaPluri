# Modelo mexicano ENIF — entrenamiento e integración comprobados

Fecha local: 15/10/2026, America/Mexico_City. QA web iniciada a las 02:17:19 UTC del 16/10/2026 (20:17:19 del día 15 en México). Trabajo sólo en copia académica local `NexoCredit/nexocredit`; sin push, CI remota ni actualización de la instalación original.

## Datos y entrenamiento reales

Se descargó el ZIP oficial ENIF 2024 de INEGI/CNBV, SHA-256 `00e4b0b42775276b2da236a5bba8c64dc5a92c289908a4727dec93dc7684f039`. TMODULO contiene 13,502 entrevistas; tras exclusiones documentadas quedan 3,906 casos completos. Ningún registro individual de encuesta se incorpora al repositorio. [Fuente, exclusiones, variables, algoritmo, reproducción y límites](../../../inteligencia_artificial/prediccion_mexico/README.md).

Regresión logística real, no categorías generadas por reglas/LLM. Entrenamiento 2,333, validación 790 y prueba 783, con UPM_DIS disjuntas. Selección de C/umbral sólo en validación. AUC de prueba 0.605496, sensibilidad 71.58 %, precisión positiva 26.73 %, F1 0.389302 y exactitud 47.51 %. Siempre «sin atraso» da 76.63 % de exactitud. Capacidad limitada y muchos falsos positivos: no se afirma aptitud para crédito real. No se ajustó el modelo después de observar esa prueba para mejorar artificialmente las cifras.

Modelo: `nexocredit-enif2024-logistica-v1`, SHA-256 `1f6238b217583d0f5c00320d9caf3c331e422452104776b9b99b57a75440e621`. Exportación numérica contrastada con sklearn en todas las 3,906 filas: error máximo 0.0 en el entorno del entrenamiento. No se carga pickle. La inferencia no requiere Azure/Ollama/red.

Se repitió el entrenamiento desde el mismo ZIP con el código reorganizado final y la misma versión de dependencias: el artefacto reprodujo exactamente ese SHA-256. `.gitattributes` fija LF para no romper su huella al clonar en Windows. La prueba de reproducción quedó en una carpeta temporal nueva; no sobrescribió el artefacto servido.

## Suite de regresión

Primera suite completa de este incremento: **235 backend/PostgreSQL y 165 frontend**, sin omisiones; cinco pruebas PowerShell, migraciones repetidas, lint/build y npm audit sin vulnerabilidades reportadas. Ejecución real mediante `scripts/probar-programacion.ps1` en contenedores y base efímeros, no la base de trabajo. Backend: 26.161 s en ese recorrido. Los nuevos casos comprueban inferencia real, SHA alterado, respuestas inválidas/ausentes, autenticación, privacidad 422, compatibilidad antigua, score independiente y selección correcta del objetivo ENIF.

Suite final tras exigir los dos artefactos ENIF en el paquete público y añadir la regresión de ambas clases: **236 backend/PostgreSQL y 165 frontend**, sin omisiones; backend 23.447 s, cinco pruebas PowerShell y auditoría npm con cero vulnerabilidades reportadas. El frontend se reutilizó de la capa de construcción ya probada (mismo código), con test/lint/build aprobados. Logs locales `output/tmp/enif2024/suite.log` y `suite-final.log` del espacio exterior. No CI remota.

Los primeros intentos detectaron pruebas frontend que contaban siete inputs sin distinguir el nuevo checkbox y un helper de prueba que no resolvía el nuevo import. Se adaptaron sin retirar validaciones de los siete campos originales. La suite pasó después de la corrección. Un TestClient en el entorno Windows temporal quedó sin responder y fue interrumpido; no se considera aprobado. Las comprobaciones aprobadas son las de Docker indicadas aquí.

## Recorrido real en navegador headless propio

Script QA local: `output/tmp/enif2024/verificar_ui.cjs` del espacio de trabajo exterior (no parte de la aplicación). Chrome headless en contexto nuevo, sin perfil/ventanas del usuario. Tres contenedores temporales propios, PostgreSQL en tmpfs/red interna sin publicar puertos, sin montajes de datos originales; frontend en puerto loopback efímero. Azure/Ollama deshabilitados, explicación de reglas por plantilla marcada sin IA generativa. Llamadas económicas externas abortadas; no se simularon como datos disponibles.

Comprobaciones aprobadas:

1. Login local real con cuenta ficticia temporal y JWT, sin exponer contraseña/token en evidencias.
2. Perfil ENIF completo capturado dentro de Evaluación y ejecución real del modelo por `/api/v1/evaluar`.
3. Resultado y perfil guardados en PostgreSQL; consulta detalle idéntica, incluyendo SHA/versión/métricas.
4. Reintento con mismo UUID/perfil conserva el resultado; otro perfil con misma clave devuelve 409 y no lo modifica.
5. Cambiar sólo score 900 → 200 modifica reglas Bajo → Alto, pero conserva la misma salida ENIF `0.111645`, umbral `0.18`, clase `perfil_no_asociado_a_atraso`.
6. Resultado mexicano visible en el detalle del historial y opción de desactivar el perfil sin inventar datos/modelo.
7. Vista móvil 390 px: panel entre x=14 y x=376, ancho interno/scroll 360 px; sin desbordamiento. Sin errores JavaScript de página.
8. Tres evaluaciones ficticias sólo en la base efímera; contenedores originales conservan sus identificadores. Retirados los tres contenedores y dos redes propios al finalizar, verificado por etiquetas. Base original no accedida y navegador del usuario no controlado.

Capturas y manifiesto local:

`C:\Users\julia\Music\empresa - copia\output\evidencias\Modelo_Mexico_ENIF_2026-10-15\nexocredit-enif-4359d9ea21\`

- `01_Perfil_Mexicano.png` — preguntas del formulario.
- `02_Modelo_Mexico_Escritorio.png` — resultado y calidad medida.
- `03_Modelo_Mexico_Movil.png` — vista móvil real, sin overflow.
- `04_Modelo_Mexico_Historial.png` — consulta de resultado persistido.
- `manifest.json` — huellas SHA-256 de capturas, resultado y comprobaciones/limpieza.

Las capturas de escritorio/móvil se inspeccionaron visualmente. Son evidencia de ese ensayo, no una revisión del navegador original ni aceptación humana/empresarial. No se recrearon con imágenes generadas.

## Límites y pendientes

El modelo estudia asociaciones contemporáneas con atrasos autodeclarados de la encuesta 2024. No sigue préstamos futuros, consulta Buró, confirma situación de una persona, presenta PD calibrada o acredita equidad. La selección de casos completos/no ponderados no estima prevalencia nacional. Las reglas históricas siguen alimentando dashboard/Power BI; no se mezclan sus categorías con la clase ENIF. Azure/Entra y keys se mantienen sin nuevas llamadas cloud.

La instalación original abierta no se actualizó, ni se realizó push, commit nuevo, capacitación o aceptación del asesor. No se regeneraron los PDFs de entrega previos; las fuentes Markdown actuales contienen esta adenda y los PDFs anteriores no deben presentarse como si ya la incluyeran.
