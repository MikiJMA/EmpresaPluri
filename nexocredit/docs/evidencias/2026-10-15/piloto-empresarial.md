# Piloto empresarial — comprobación técnica del 15/10/2026

## Contexto y alcance

El usuario pidió tratar el proyecto como una prueba empresarial y mejorar lo posible. Confirmó que todavía no dispone de historial autorizado/anonimizado de préstamos y pagos posteriores. Se trabajó en la copia local; no se modificó la instalación original ni se ejecutó push, CI remota o uso de datos de clientes. Los antecedentes académicos se conservaron, sin usarlos como prueba de aceptación empresarial.

## Comparación real de modelos

Antes de ejecutar se fijó `plan_piloto.json`: regresión logística, Random Forest, Gradient Boosting y selección interna entre ellos, con validación anidada 5×3 por UPM, calibración sigmoide interna y 300 remuestreos bootstrap agrupados. Se excluyeron los 783 casos de prueba histórica ya observada; sólo se usaron 3,123 de desarrollo. Código/ZIP montados de sólo lectura en un contenedor sin red, dos CPU y 2 GB. Sin Ollama/Azure, datos originales o entrenamiento contra la prueba conocida.

Resultados OOF de desarrollo: logística AUC 0.642223, bosque 0.648446, boosting 0.646821 y selección anidada 0.644602. El intervalo de la diferencia bosque−logística incluye cero (−0.006378, +0.018477); boosting también (−0.004898, +0.013843). No se demostró mejora consistente; no se cambió el artefacto servido ni se reinterpretó su AUC de prueba 0.605496 como 0.648.

Informe agregado real: `backend/app/integraciones/prediccion_mexico/piloto/comparacion-v1/comparacion.json`, SHA-256 `50de28cba9113d3751bdfbc66d3857e40bfc3fba293f21c77e1fcb047ce70ea5`. No contiene registros o predicciones individuales. [Protocolo, entorno, métricas y límites completos](../../desarrollo/PILOTO_EMPRESARIAL.md).

## Software comprobado

Suite `scripts/probar-programacion.ps1`: **247 backend/PostgreSQL y 168 frontend**, sin omisiones; backend 23.843 segundos en ese recorrido; migraciones repetidas, cinco pruebas PowerShell, lint/build y auditoría npm con cero vulnerabilidades reportadas. Log local `output/tmp/enif2024/suite-piloto.log` del espacio de trabajo exterior. Después del cambio de título del banner, la construcción frontend volvió a ejecutar las 168 pruebas, lint y build, aprobados en `build-piloto-ui.log`.

Regresiones nuevas: control de piloto pendiente no modificable desde el formulario/query; autenticación, ausencia de POST de aprobación, informe alterado sin mejoras ficticias; conservación de modelo/test y contratos de interfaz. El validador del historial usa sólo fixtures sintéticas y comprueba columnas de identidad prohibidas, duplicados, UUID, importes/fechas, variables posteriores al origen, resultado desconocido y horizontes/seguimiento incompletos sin inventar negativos. No entrena ni certifica autorización/anonimización/suficiencia por superar esas comprobaciones.

## Navegador real aislado

Chrome headless con perfil nuevo, no ventanas/perfil del usuario. PostgreSQL tmpfs/red interna, API y Nginx temporales propios; único puerto de frontend loopback efímero. Cuenta ficticia con contraseña/token aleatorios mantenidos en memoria, no publicados. Explicación local marcada sin IA; Azure/Ollama deshabilitados y economía externa abortada, sin simular disponibilidad.

Se comprobaron estado del piloto vía API, comparación/calidad y pendientes visibles en pantalla, modelo real sin cambio, perfil y gobernanza persistidos, reintento idempotente, conflicto 409, historial, cambio de score independiente de ENIF y modo sin perfil explícito. Cero errores JS. A 390 px, panel x=14…376 con scrollWidth=clientWidth=360: sin desbordamiento. El ensayo usa tres evaluaciones ficticias y no demuestra rendimiento o comportamiento crediticio real.

Capturas/manifiesto:

`C:\Users\julia\Music\empresa - copia\output\evidencias\Piloto_Empresarial_2026-10-15\nexocredit-enif-64a2e50e2b\`

- `01_Perfil_Mexicano.png`.
- `02_Modelo_Mexico_Escritorio.png`.
- `03_Modelo_Mexico_Movil.png`.
- `04_Modelo_Mexico_Historial.png`.
- `manifest.json`, con SHA-256 de capturas, estado y comprobaciones/limpieza.

La captura móvil se inspeccionó visualmente: tabla comparativa ajustada y gobernanza legible. Los controles desplegados alargan el panel; no se interpreta el tamaño de la captura como un fallo de scroll de la aplicación. No son imágenes generadas. Tres contenedores y dos redes propios retirados mediante comprobación de etiquetas; identificadores de los servicios originales conservados. Sin acceso a su base ni control del navegador del usuario.

## Qué no queda demostrado

No hay historial empresarial, validación prospectiva/temporal, aprobación de costes o umbrales, prueba de equidad ni aprobación operativa. El piloto en sombra no es un sistema DLP, una certificación legal o un motor validado de crédito. El modelo sigue siendo asociativo ENIF y de capacidad limitada. No se ocultan estas restricciones ni se declaran mejoras por cambiar la denominación a empresarial.

No se regeneraron PDFs/ZIP anteriores, no se creó un commit nuevo ni se subió código. La siguiente fase con datos empresariales requiere autorización, calidad, definición del desenlace y validación independiente; no se presume disponible por dejar preparado el validador.
