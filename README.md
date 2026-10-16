# NexoCredit — piloto de análisis de riesgo crediticio

Código activo en [nexocredit/](nexocredit/README.md): React, FastAPI, PostgreSQL, modelo mexicano ENIF, valoración generativa opcional y revisión humana. El modelo se ejecuta en la evaluación principal y su resultado se guarda junto a la solicitud. Las reglas se muestran como comparación, no como salida del modelo.

Piloto en sombra con datos públicos y escenarios ficticios: todavía no hay historial autorizado de la empresa ni validación de impagos futuros. No consulta Buró, certifica identidad ni autoriza créditos reales. El modelo ENIF tiene capacidad limitada (AUC de prueba 0.605); comparar otros algoritmos no demostró una mejora consistente. [Protocolo y pendientes](nexocredit/docs/desarrollo/PILOTO_EMPRESARIAL.md).

## Abrir o actualizar

Windows y Docker Desktop iniciado. Desde `nexocredit/`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir [localhost:8080](http://localhost:8080/) y entrar con la cuenta existente. La primera construcción requiere Internet. Para una instalación nueva, consultar [LEEME_PRIMERO.md](LEEME_PRIMERO.md); nunca hay contraseña predeterminada.

Esta instalación conserva el proyecto Compose `plurione-docker` y su volumen; la copia pública depurada utiliza `nexocredit-demo`. No intercambiar sus `.env`, levantar ambas sobre los mismos puertos ni borrar volúmenes. La carpeta exterior conserva su nombre físico, pero código, workflow, lanzadores y workspace apuntan a `nexocredit/`.

## Recorrido para el revisor — 4 pasos

1. En **Evaluación**, usar RFC ficticio `AAAA010101AA1`, ingresos `30000`, gastos `10000`, deuda `0`, pagos `0`, atraso `0` y score `900`. Dejar desactivada la revisión opcional CURP.
2. Incluir el análisis mexicano: ingreso laboral `12000`, periodo **Mes**, ingreso **Fijo**, presupuesto **Sí**, gastos cubiertos **Sí**, ahorros **Tres meses a menos de seis meses** y **Tarjeta bancaria**. Evaluar: aparece primero el modelo mexicano con versión, resultado asociativo, métricas y límites. No necesita Azure ni Ollama.
3. Repetir cambiando sólo el score a `200`: las reglas pasan de Bajo a Alto; la salida ENIF no cambia porque ese modelo no usa el score. No se inventan 19 variables UCI a partir del formulario mexicano.
4. Abrir **Historial**, consultar el detalle y registrar una revisión ficticia. Ver los resúmenes en **Dashboard**, guías en **Documentos** y el módulo **Seguimiento** para planes, pagos y alertas. Las explicaciones Ollama son adicionales y requieren el modelo local instalado; no sustituyen la inferencia estadística.

## Documentación esencial

- [PRD](nexocredit/docs/producto/PRD_NEXOCREDIT.md) y [MVP/MoSCoW](nexocredit/docs/producto/MVP_NEXOCREDIT.md).
- [Arquitectura y datos](nexocredit/docs/desarrollo/ARQUITECTURA_Y_DATOS.md).
- [Operación](nexocredit/docs/manuales/OPERACION.md), [soporte](nexocredit/docs/manuales/MANTENIMIENTO_Y_SOPORTE.md) y [QA](nexocredit/docs/calidad/QA.md).
- [Modelo ENIF y reproducción](nexocredit/inteligencia_artificial/prediccion_mexico/README.md), [tecnologías y estado](nexocredit/REQUISITOS_TECNOLOGICOS.md) e [índice ampliado](nexocredit/docs/README.md).

Azure OpenAI, Azure Machine Learning, Azure AI Search y Microsoft Entra conservan adaptadores, plantillas de keys y evidencias históricas. Su uso requiere recursos y credenciales vigentes; las alternativas locales no demuestran conectividad Azure actual. Power BI, APIs financieras, Docker, GitHub Actions y Scrum conservan sus responsabilidades documentadas; no se inventan aprobaciones o ceremonias.

## Proceso y uso de IA

Este es el espacio de desarrollo original, con su historial Git. La copia depurada de entrega está en `output/repositorios/G19X-TESOEM-JJVR-174-ACADEMIC/NexoCredit/` y mantiene historial independiente: sus primeros commits no representan todo el trabajo anterior. Las mejoras actuales se guardan en commits descriptivos locales; no se presume push o CI remota.

Se utilizó **Codex** para implementar, depurar, probar, organizar y documentar. El historial previo también declara asistencia de Google Antigravity/Gemini. La asistencia de IA no equivale a validación humana, aprobación empresarial o aceptación del asesor.

Las llaves van únicamente en archivos privados del servidor. No compartir `.env`, bases, cuentas, respaldos ni capturas privadas. Abrir [NexoCredit.code-workspace](NexoCredit.code-workspace) para una vista ordenada de código y CI.
