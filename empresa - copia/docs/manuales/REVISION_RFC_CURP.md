# Revisión de RFC con CURP

Función adicional para la demo de NexoCredit, 11/10/2026. Usa solo datos ficticios en esta aplicación. No es un servicio fiscal, KYC, certificación de identidad ni decisión crediticia.

## Uso

En Datos del solicitante, captura el RFC de persona física (13 caracteres) y, opcionalmente, una CURP de 18 posiciones. Pulsa **Revisar formato y fecha**. La revisión verifica una máscara general, que la fecha sea posible y, si hay CURP, que las fechas incluidas coincidan. Se normalizan mayúsculas/espacios externos para revisar. No se calcula ni genera una homoclave a partir del nombre.

La CURP se mantiene fuera de la solicitud de evaluación. Solo se envía a la ruta autenticada `POST /api/v1/identidad/revisar`, no se guarda en PostgreSQL, no se pone en URLs ni se envía a Azure/Ollama. La respuesta no devuelve los identificadores y usa `Cache-Control: no-store`; los errores de esquema tampoco los reflejan.

La revisión es opcional y separada de las reglas del riesgo. Se conservan las solicitudes demo anteriores y sus identificadores, incluso si no son RFC oficiales. No transforma el historial ni convierte una evaluación en una autorización de crédito.

## Alcance real

“Comprobación básica · No oficial” no significa que el RFC exista ni que corresponda a la persona. No se verifican la asignación de homoclave, el dígito verificador de CURP, el catálogo completo RENAPO, la identidad del titular ni inscripción fiscal. Tampoco se compara el nombre: las iniciales pueden tener reglas y excepciones, y una coincidencia de fecha no prueba identidad. Los RFC genéricos se advierten expresamente como no identificadores personales.

El botón **Consultar RFC por CURP en el SAT** abre la [consulta oficial](https://wwwmat.sat.gob.mx/aplicacion/31274/consulta-tu-clave-de-rfc-mediante-curp) sin incorporar datos personales al enlace. El usuario realiza la consulta y cualquier CAPTCHA directamente en el SAT. La [descripción oficial del trámite](https://wwwmat.sat.gob.mx/aplicacion/31274/consulta-tu-clave-de-rfc-mediante-curp) indica que devuelve el RFC registrado relacionado con una CURP; esto es distinto de la revisión de formato de NexoCredit. La [información de RENAPO](https://www.gob.mx/segob/acciones-y-programas/obtencion-de-la-curp) describe las 18 posiciones y la asignación de sus últimos caracteres.

No se integra una API oficial automática, no se omiten CAPTCHAs y no se guarda un resultado como “SAT verificado”. Una automatización oficial requeriría un proveedor/API autorizado, credenciales, consentimiento, políticas de protección/retención y evidencia de la respuesta; eso permanece fuera de esta implementación.
