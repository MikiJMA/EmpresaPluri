# Banxico, responsable y revisión RFC/CURP — 11/10/2026

## Cambios y límites

- Banxico SIE oportuno devolvió la tasa objetivo con fecha posterior a la consulta. La validación anterior descartaba toda la fuente, incluido un FIX válido. Ahora se admite exclusivamente SF61745 hasta siete días después de la fecha UTC de consulta, con `fecha_futura=true`, estado parcial y aviso explícito: no confirma la tasa vigente. FIX futuro y fechas más lejanas siguen rechazados. No se inventan valores, no se alteran las reglas del riesgo y las tarjetas financieras no se estiran a la altura de otra fuente.
- El responsable autenticado muestra su nombre. Los identificadores UUID se conservan internamente y en la atribución del servidor; no se cambia la cuenta, el historial ni la responsabilidad de auditoría. La presentación también limpia únicamente sufijos técnicos reconocidos en revisiones anteriores.
- La guía de score Bajo/Medio/Alto queda abierta por defecto. Las condiciones de margen y score siguen siendo las reglas demostrativas anteriores, no categorías oficiales de una entidad financiera.
- Revisión opcional autenticada `POST /api/v1/identidad/revisar`: máscara general y fecha posible para RFC de persona física; con CURP, máscara general de 18 posiciones y coincidencia de fecha. No acredita inscripción, homoclave, dígito verificador CURP, entidad RENAPO ni pertenencia a la persona. No se genera un RFC desde el nombre ni se implementa KYC.
- La CURP está separada del formulario de evaluación, no se guarda en PostgreSQL ni se envía a Azure/Ollama o a un tercero. La respuesta y los errores de esquema no reflejan RFC/CURP; la respuesta usa `Cache-Control: no-store`. La consulta SAT abre su URL fija sin identificadores y es manual. No hay API oficial automática ni resultado persistido como SAT verificado. [Manual y fuentes oficiales](../../manuales/REVISION_RFC_CURP.md).

## Pruebas automáticas

Se ejecutó `scripts/probar-programacion.ps1`: 116 pruebas backend/PostgreSQL y 79 frontend aprobadas, sin omisiones; lint/build, auditoría npm sin vulnerabilidades reportadas y cinco archivos de pruebas PowerShell aprobados. La base de pruebas PostgreSQL es aislada; sus migraciones se ejecutan dos veces. No se reutiliza ni modifica la base de trabajo.

Los casos nuevos cubren la tasa futura permitida, rechazo de FIX futuro/fechas excesivas, DTO financiero estricto, nombre visible sin cambiar el payload responsable, revisión básica con datos sintéticos, diferencias de fecha, formatos incorrectos, privacidad de respuesta/errores y autenticación. La integración no llama a PostgreSQL ni a proveedores externos al revisar RFC/CURP. El frontend rechaza respuestas de identidad que inventen verificación oficial, enlaces ajenos o comprobaciones mal formadas y oculta resultados correspondientes a otros valores.

Después del último endurecimiento del cliente de revisión de identidad se volvió a construir la imagen frontend: las 79 pruebas, lint y build pasaron nuevamente. La suite backend completa precede a ese ajuste exclusivamente de frontend; su código no cambió después.

## Consultas reales separadas de las pruebas simuladas

Lectura directa del adaptador financiero desde el backend Docker, aproximadamente a las 23:25 UTC del 11/10/2026, sin imprimir el token:

| Fuente/serie | Valor publicado | Periodo | Observación |
|---|---:|---|---|
| Banxico SF43718, FIX | 18.4163 MXN/USD | 09/10/2026 | Fecha válida; se conserva |
| Banxico SF61745, tasa objetivo | 6.5000 % | 12/10/2026 | Fecha futura reportada; proveedor parcial, no confirmada como vigente |
| Banco Mundial, inflación MEX | 3.80957950037393 % | 2025 | Último año devuelto, no dato del día |
| Banco Mundial, crecimiento PIB MEX | 0.561683456144578 % | 2025 | Último año devuelto, no dato del día |

La consulta acredita la respuesta observada del adaptador en ese momento, no disponibilidad permanente ni una consulta autenticada desde la nueva interfaz. Los errores anteriores del Banco Mundial fueron un timeout; no se sustituye la respuesta por datos fabricados. Contrato de [datos oportunos Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp).

## Aplicación y revisión visual

Backend, frontend y PostgreSQL de trabajo quedaron saludables. Tras aplicar la última imagen frontend se comprobaron, mediante conteos sin datos de expediente, 9 evaluaciones, 2 revisiones y 1 cuenta local. La nueva ruta de identidad a través de Nginx devuelve HTTP 401 sin sesión. No se crearon cuentas, evaluaciones ni revisiones para esta comprobación.

Se revisó el formulario mediante una previsualización aislada de los componentes reales, con datos ficticios y sin autenticación/API. CURP, botón de revisión, enlace SAT y avisos quedaron legibles. Captura privada local: `output/revisiones_visuales/2026-10-11/rfc-curp.jpg` en la raíz exterior, excluida de Git. No es evidencia de una consulta oficial ni de un flujo autenticado de identidad.

La pestaña de trabajo del usuario aún tenía el bundle anterior al observarla; necesita recargar y volver a iniciar sesión para cargar todos los cambios. No se interrumpió esa sesión ni se extrajeron credenciales. No se consultaron datos de una persona en el SAT, no se ejecutó una nueva generación de IA, nueva CI remota, publicación ni commit en este cambio.
