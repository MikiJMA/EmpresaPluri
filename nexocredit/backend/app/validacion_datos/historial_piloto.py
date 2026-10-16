"""Contrato previo al entrenamiento empresarial. No presume anonimización ni suficiencia estadística."""
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from uuid import UUID

COLUMNAS = [
    'credito_id_anonimo', 'persona_id_anonima', 'fecha_otorgamiento', 'fecha_captura_variables',
    'fecha_ultima_observacion', 'ingresos_mensuales_al_otorgar', 'gastos_mensuales_al_otorgar',
    'deuda_previa_al_otorgar', 'cuota_mensual_pactada', 'monto_otorgado', 'plazo_meses',
    'max_dias_atraso_en_horizonte', 'seguimiento_completo',
]
IMPORTES = COLUMNAS[5:10]


def _fecha(valor):
    if len(valor) != 10:
        raise ValueError('fecha')
    fecha = date.fromisoformat(valor)
    if fecha.isoformat() != valor:
        raise ValueError('fecha')
    return fecha


def _uuid(valor):
    if str(UUID(valor)) != valor.lower():
        raise ValueError('uuid')
    return valor.lower()


def validar_historial(fuente, *, fecha_corte, horizonte_dias, atraso_umbral_dias):
    if (type(horizonte_dias) is not int or not 1 <= horizonte_dias <= 3650 or
            type(atraso_umbral_dias) is not int or not 1 <= atraso_umbral_dias <= horizonte_dias or
            type(fecha_corte) is not date):
        raise ValueError('Definir fecha de corte, horizonte y umbral de atraso de forma explícita.')
    lector = csv.DictReader(fuente)
    encabezados = lector.fieldnames or []
    if len(encabezados) != len(COLUMNAS) or set(encabezados) != set(COLUMNAS):
        raise ValueError('Contrato CSV inválido. Usar sólo las columnas permitidas, sin nombres, RFC, CURP o contactos.')
    ids, personas = set(), set()
    errores = []
    totales = {'filas': 0, 'aptas_por_contrato_y_madurez': 0, 'sin_seguimiento_completo': 0,
               'horizonte_no_observado': 0, 'errores': 0, 'con_atraso': 0, 'sin_atraso': 0}
    for numero, row in enumerate(lector, 2):
        totales['filas'] += 1
        if totales['filas'] > 100_000:
            raise ValueError('Máximo 100000 filas por comprobación local.')
        try:
            if None in row or any(v is None or len(v) > 100 for v in row.values()):
                raise ValueError('cantidad_o_longitud_de_campos')
            identificador = _uuid(row['credito_id_anonimo'])
            persona = _uuid(row['persona_id_anonima'])
            if identificador in ids:
                raise ValueError('credito_duplicado')
            ids.add(identificador)
            personas.add(persona)
            otorgamiento = _fecha(row['fecha_otorgamiento'])
            captura = _fecha(row['fecha_captura_variables'])
            observacion = _fecha(row['fecha_ultima_observacion'])
            if not captura <= otorgamiento <= observacion <= fecha_corte:
                raise ValueError('fechas_incompatibles_o_variables_posteriores_al_otorgamiento')
            for campo in IMPORTES:
                valor = Decimal(row[campo])
                if not valor.is_finite() or valor < 0 or valor > 1_000_000_000 or valor.as_tuple().exponent < -2:
                    raise ValueError('importe_invalido')
                if campo in ('ingresos_mensuales_al_otorgar', 'monto_otorgado') and valor <= 0:
                    raise ValueError('importe_positivo_requerido')
            if not row['plazo_meses'].isdigit() or not 1 <= int(row['plazo_meses']) <= 600:
                raise ValueError('plazo_invalido')
            if row['seguimiento_completo'] not in ('si', 'no'):
                raise ValueError('seguimiento_debe_ser_si_o_no')
            if row['seguimiento_completo'] == 'no':
                totales['sin_seguimiento_completo'] += 1
                continue
            fin = otorgamiento + timedelta(days=horizonte_dias)
            if observacion < fin:
                totales['horizonte_no_observado'] += 1
                continue
            atraso = row['max_dias_atraso_en_horizonte']
            if not atraso.isdigit() or not 0 <= int(atraso) <= horizonte_dias:
                raise ValueError('atraso_invalido_o_desconocido')
            totales['aptas_por_contrato_y_madurez'] += 1
            totales['con_atraso' if int(atraso) >= atraso_umbral_dias else 'sin_atraso'] += 1
        except (ValueError, InvalidOperation, OverflowError):
            totales['errores'] += 1
            if len(errores) < 20:
                # Sólo número de fila y código genérico: no reflejar importes/identificadores en logs.
                errores.append({'fila': numero, 'motivo': 'Revisar contrato, fechas, duplicados o valores. No se muestran datos de la fila.'})
    return {'formato': 'nexocredit-historial-piloto-v1', 'fecha_corte': fecha_corte.isoformat(),
            'horizonte_dias': horizonte_dias, 'atraso_umbral_dias': atraso_umbral_dias,
            'conteos': totales, 'personas_distintas_en_archivo': len(personas), 'errores_muestra': errores,
            'contrato_valido': totales['filas'] > 0 and totales['errores'] == 0,
            'ambas_clases_observadas': totales['con_atraso'] > 0 and totales['sin_atraso'] > 0,
            'suficiencia_estadistica_validada': False, 'autorizacion_y_anonimizacion_verificadas': False,
            'decision_crediticia_habilitada': False,
            'limites': 'Comprobación estructural local, no valida el origen, autorización, anonimización o veracidad. '
                       'No entrena ni habilita decisiones. Los horizontes incompletos no se etiquetan como sin atraso. '
                       'Requiere definición del desenlace y política aprobadas, revisión de calidad, '
                       'partición temporal y por persona, validación independiente, calibración y equidad.'}
