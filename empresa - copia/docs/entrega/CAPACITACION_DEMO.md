# Guía de práctica de NexoCredit

Material preparado el 11/10/2026 y actualizado para la demostración local el **14/10/2026**. **No se realizó ni certificó una capacitación.** No se convocó a asesores ni se inventaron participantes, firmas u horas. Es una guía para el operador en el equipo existente, no una reunión programada, instalación para terceros o acta firmada.

## Corte de la guía — 14/10/2026

Las nuevas evaluaciones usan `reglas-demo-v2`: score 0–499 → Alto, 500–679 → Medio y 680–1000 → Bajo. Margen ≤$7,000 implica Alto y >$7,000 hasta $15,000 implica al menos Medio; el resultado conserva la peor categoría de score y margen. Las evaluaciones v1 mantienen sus resultados y versiones, sin recálculo. Los resúmenes se redondean a pesos completos; captura, cálculos, base y detalles de evaluación/pagos conservan centavos. [Reglas y ejemplos](../manuales/REGLAS_RIESGO_DEMO.md).

Ollama explica, los documentos locales recuperan **3 guías / 15 secciones**, y scikit-learn predice únicamente en el laboratorio UCI/NTD independiente. No son la misma función. Azure OpenAI, ML, Search y Entra permanecen implementados con evidencia histórica del 04/10/2026 y campos privados de keys. El catálogo cloud histórico es 2 guías / 14 secciones; **la guía v2 aún requiere carga y comprobación en Azure Search**. No se simula esa carga ni se explica v2 con la guía anterior si falta la compatible.

La suite local final del **14/10/2026** registra **197 backend/PostgreSQL y 129 frontend aprobadas**, sin omisiones, lint/build, auditoría npm con cero vulnerabilidades reportadas y cinco archivos PowerShell. La corrida inicial fue 190/129; se añadió regresión Ollama. Incluye **14 pruebas del empaquetador sin omisiones**, en fixtures sin DB/red, no sumadas de nuevo a 197. [Evidencia de entrega local](../evidencias/2026-10-14/entrega-demo.md). Son pruebas de software, no resultados de aprendizaje, capacitación, firmas o aceptación. Se conserva por separado el corte [histórico del 13/10/2026](../evidencias/2026-10-13/reglas-v2-y-importes.md): 175 backend/129 frontend.

El usuario informó recarga/acceso y apertura/actualización/guardado Power BI. La revisión posterior encontró diálogo «Abrir» y **5 evaluaciones frente a 10 en PostgreSQL**, con **29 diferencias de 96 comparaciones DAX**; una segunda conciliación aún mostró cinco frente a doce. Tras dos altas ficticias se requieren **12 evaluaciones** y **Power BI sigue pendiente**, con [pasos manuales](../evidencias/2026-10-14/entrega-demo.md#power-bi); se detuvo el control UI por solicitud del usuario. [CI del código](../evidencias/2026-10-14/github-actions.md) aprobó 197/129, el ZIP candidato pasó CRC/hashes/exclusiones y se aprobó restauración aislada de doce tablas. No se inventa una práctica completa, participantes u horas.

La primera alta ficticia UI fue score 200/margen $20,000 → Alto v2, con guía v2 e inferencia local scikit-learn clase False; mostró Alto 2/$12,500 y limpio 11/$18,636. Se conserva el error de aquella generación Ollama como hallazgo histórico. Tras desplegar la corrección, **la segunda alta ficticia** comprobó una respuesta real correcta para ese caso: score 200 en banda 0–499 Alto; margen $20,000 mínimo Bajo; final Alto, hechos **NO IA**, comentario académico IA separado y fuente **2.0**. Reintentar el botón conservó ID/fecha sin duplicar. Captura local privada `output/revisiones_visuales/2026-10-14/explicacion-v2-corregida.jpg`, no subida ni empaquetada. No se garantiza la semántica de cualquier respuesta libre. [Contrato y límites](../manuales/ACCESO_LOCAL_Y_PROVEEDORES.md#contrato-ollama-corregido--14102026).

Corte tras ambas altas: 12 evaluaciones, margen promedio $18,750, ingresos promedio $30,000, deuda promedio exacta $10,020.05 sobre 10 capturas, cobertura 83.333 %; Bajo 7/Medio 2/Alto 3 y Pendiente 10/Aprobada 2. Son datos ficticios del corte de QA, no metas de capacitación, contadores permanentes o autorizaciones de crédito.

## Preparación

Docker Desktop y aplicación local disponibles; cuenta propia ya creada por el operador, modo Azure/Ollama/local identificado, datos ficticios y copia de respaldo. Nunca compartir contraseñas ni enviar llaves por chat. La cuenta Analista no ve auditoría global nueva; una cuenta Administrador sólo debe crearse por una decisión explícita del operador.

Al evaluar se guarda un registro y puede solicitarse IA automáticamente con el proveedor configurado. Advertir consumo si está en Azure; Ollama necesita su modelo instalado. El seguimiento de cuotas/pagos no llama IA. Los ejercicios de escritura siguientes son futuros: no se ejecutaron en la base de trabajo al redactarlos.

### Copia para entrega local — acción opcional aún no acreditada

Desde la carpeta interior, con Python disponible:

```powershell
python .\scripts\preparar_entrega.py --nombre NexoCredit_Entrega_2026-10-14
```

El ZIP y su manifiesto se crean sin sobrescribir bajo `output/entregas/` exterior. No basta con aprobar pruebas del generador: hay que ejecutar y revisar la copia y las huellas antes de compartirla. Excluye credenciales, base/dumps, dependencias/imágenes instaladas y modelo Ollama; mantiene fuente, definiciones Power BI y modelo numérico scikit-learn. Redacta el bloque de identificación del plan sólo en la copia y usa un marcador para la ficha privada del alumno.

Quien lo ejecute necesita un **primer build Docker**, configuración nueva y **usuario propio**; no recibe las cuentas o llaves de este equipo. El paquete no es offline/autocontenido. `LEEME_PRIMERO.md` contiene la secuencia build → modo local → cuenta propia. Para generar texto requiere Ollama/modelo instalados, o la selección explícita `EXPLICACIONES_PROVEEDOR=local`, una plantilla **NO IA generativa**. No usar el empaquetado como evidencia de capacitación, despliegue o aceptación.

## Ejercicios propuestos

1. **Acceder:** distinguir Microsoft de cuenta local; recargar y observar que debe volver a autenticarse localmente. No desactivar seguridad para continuar.
2. **Evaluar:** explicar primero sin guardar: con margen $20,000, score 200 → Alto, 500 → Medio y 700 → Bajo; con score 900 y margen $7,000 → Alto. Si el operador decide guardar un nuevo escenario ficticio, ingresos 30.000, gastos 10.000, deuda 0, pagos 0, atraso 0 y score 700 producen margen 20.000, Bajo y `reglas-demo-v2`; no aprobación real. Advertir que se guardará y se solicitará explicación automáticamente. Revisar guía DEM-02 versión 2.0 y fuente, sin RFC enviado al modelo. Un registro histórico v1 se interpreta con su guía 1.0, sin cambiarlo.
3. **Entrada inválida:** pagos 12.000 frente a gastos 10.000; esperar rechazo y corregir. La validación no duplica evaluaciones.
4. **Revisión:** abrir detalle, registrar motivo demo y comprobar responsable/versión. Cambiar revisión no cambia el riesgo original.
5. **Plan de seguimiento:** elegir una evaluación ficticia acordada; total 100 MXN, dos cuotas de 50, apertura hace 30 días, primera vencida hace 5 días y segunda dentro de 5 días. Usar fechas reales relativas a hoy UTC. Esperado: saldo pendiente 100, vencido 50 y atraso 5.
6. **Abonos:** registrar 20 a la primera cuota, saldo vencido esperado 30; un abono de 31 debe rechazarse. Registrar los 30 restantes: alerta Resuelta y cuota completa. La puntualidad no sube a 100 % si se terminó tarde.
7. **Atención de alerta:** antes de completar la cuota, registrar motivo de atención; debe seguir existiendo deuda. Atendida no es pagada. Actualizar versiones ante conflicto; no reenviar con otra clave a ciegas.
8. **Consulta:** usar resumen y documentos locales (3 guías / 15 secciones). Comparar un importe resumido sin decimales con el detalle exacto; distinguir ausencia de cero y versiones v1/v2. Identificar periodos de fuente, hora de consulta y actualización manual de Power BI. Consultar proveedores económicos o actualizar el reporte sólo si se decide esa operación adicional; no afirmar que un dato capturado fue verificado en Buró/SAT.
9. **Incidente:** identificar 401/403/409/422 y un error de proveedor simulado en pruebas, no apagando PostgreSQL de trabajo. Consultar el runbook.
10. **Laboratorio IA local:** identificar `nexocredit-uci-logistica-v1`, 19 variables UCI en NTD y métricas/límites. «Cargar ejemplo ficticio» sólo llena los campos. Si se decide consultar el modelo local, la salida binaria no se guarda como evaluación, no llama a Azure ni cambia Bajo/Medio/Alto del formulario MXN. No copiar datos del solicitante en ese laboratorio. [Manual del laboratorio](../manuales/LABORATORIO_IA_LOCAL.md).

## Lista de comprensión

- ¿Distingue score capturado, reglas demo, explicación y predicción UCI?
- ¿Comprende que un score bajo implica mayor riesgo en v2, que el margen sólo puede empeorarlo y que v1 no se recalcula?
- ¿Distingue centavos conservados de un resumen visual redondeado, y catálogo local 3/15 de carga Azure v2 pendiente?
- ¿Distingue historial de evaluaciones de historial interno de pagos ficticios?
- ¿Comprende ausencia frente a cero, y cumplimiento frente a puntualidad?
- ¿Entiende que Atendida/Resuelta son estados operativos, no autorizaciones de crédito?
- ¿Puede identificar modo de proveedores, posibles costes y dónde NO pegar secretos?
- ¿Puede abrir la aplicación y reporte, y describir cómo escalar un error sin datos privados?

Registrar respuestas sólo cuando una persona real haga la práctica. No se fija un porcentaje de aprobación académica sin rúbrica definida.

## Registro disponible para una sesión futura

Fecha/hora: pendiente. Participantes: pendiente. Facilitador: pendiente. Versión usada: pendiente. Ejercicios realizados: pendiente. Resultados/dudas: pendiente. Duración real: pendiente. Decisión/observaciones: pendiente. Firmas, si se requieren: sólo después de la sesión y por sus titulares.

Referencias: [manual general](../manuales/OPERACION.md), [reglas versionadas](../manuales/REGLAS_RIESGO_DEMO.md), [laboratorio local](../manuales/LABORATORIO_IA_LOCAL.md), [seguimiento](../manuales/SEGUIMIENTO_CREDITICIO.md), [soporte](../manuales/MANTENIMIENTO_Y_SOPORTE.md), [entrega local](ENTREGA_DEMO.md).
