"""Revisión local limitada, sin consultas externas ni certificación de identidad."""
from datetime import date, datetime, timezone
import re

SAT_CURP_URL = 'https://wwwmat.sat.gob.mx/aplicacion/31274/consulta-tu-clave-de-rfc-mediante-curp'
RFC_FISICA = re.compile(r'[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}')
# Máscara general de 18 posiciones. No valida asignación, dígito verificador,
# catálogo de entidades ni pertenencia a una persona ante RENAPO.
CURP_GENERAL = re.compile(r'[A-Z][AEIOUX][A-Z]{2}[0-9]{6}[A-Z]{6}[A-Z0-9][0-9]')


def _fecha(texto, siglo=2000):
    return date(siglo + int(texto[:2]), int(texto[2:4]), int(texto[4:6]))


def revisar_identidad(rfc, curp=None):
    rfc = rfc.strip().upper()
    curp = curp.strip().upper() if curp else ''
    checks = []
    try:
        rfc_ok = bool(RFC_FISICA.fullmatch(rfc))
        if rfc_ok:
            _fecha(rfc[4:10])
    except ValueError:
        rfc_ok = False
    checks.append({'campo': 'RFC', 'correcto': rfc_ok,
                   'detalle': 'Estructura general de 13 posiciones y fecha posible.' if rfc_ok
                   else 'Se requiere un RFC de persona física: 4 letras, 6 dígitos de fecha y 3 de homoclave.'})
    estado = 'formato_correcto' if rfc_ok else 'formato_invalido'
    mensaje = 'Formato general compatible. La homoclave y la inscripción solo se confirman en el SAT.'
    if curp:
        try:
            curp_ok = bool(CURP_GENERAL.fullmatch(curp))
            if curp_ok:
                nacimiento = _fecha(curp[4:10], 1900 if curp[16].isdigit() else 2000)
                curp_ok = nacimiento <= datetime.now(timezone.utc).date()
        except ValueError:
            curp_ok = False
        checks.append({'campo': 'CURP', 'correcto': curp_ok,
                       'detalle': 'Estructura general de 18 posiciones y fecha posible; no certificada por RENAPO.' if curp_ok
                       else 'Revisa las 18 posiciones y la fecha de nacimiento de la CURP.'})
        if not curp_ok or not rfc_ok:
            estado = 'formato_invalido'
        else:
            coincide = rfc[4:10] == curp[4:10]
            checks.append({'campo': 'Fecha', 'correcto': coincide,
                           'detalle': 'La fecha incluida en RFC y CURP coincide.' if coincide
                           else 'La fecha de nacimiento del RFC y la CURP no coincide.'})
            estado = 'coherencia_basica' if coincide else 'no_coincide'
            mensaje = ('Coincide la fecha y ambos formatos generales. Esto no confirma que pertenezcan a la misma persona: consulta el SAT.'
                       if coincide else 'Hay una diferencia de fecha. Revisa los datos y consulta el RFC asociado a la CURP en el SAT.')
    if estado == 'formato_invalido':
        mensaje = 'Hay datos con formato o fecha no compatibles. Corrígelos antes de consultar el SAT.'
    if rfc in {'XAXX010101000', 'XEXX010101000'}:
        mensaje = 'Es un RFC genérico: no identifica a un solicitante específico. Consulta el RFC personal en el SAT.'
    return {'estado': estado, 'mensaje': mensaje, 'comprobaciones': checks,
            'verificacion_oficial': False, 'fuente_url': SAT_CURP_URL}
