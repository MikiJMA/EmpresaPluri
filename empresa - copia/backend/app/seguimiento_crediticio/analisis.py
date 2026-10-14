"""Cálculos descriptivos exactos; no crean un score ni una recomendación de crédito."""
from decimal import Decimal, ROUND_HALF_UP, localcontext


def importe(value):
    return format(value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP), '.2f')


def ratio(numerador, denominador, porcentaje=False):
    if numerador is None or denominador is None or denominador <= 0:
        return None
    # Los datos históricos admiten ingresos positivos inferiores a un centavo.
    # Acotar la precisión, sin overflow ni convertir un ratio extremo en cero.
    with localcontext() as context:
        context.prec = 360
        return importe(numerador / denominador * (100 if porcentaje else 1))


def indicadores(solicitud):
    def dato(key):
        value = solicitud.get(key)
        if value is None:
            return None
        result = Decimal(str(value))
        if isinstance(value, bool) or not result.is_finite() or not 0 <= result <= 1_000_000_000:
            raise ValueError('Datos guardados fuera del contrato.')
        return result
    ingresos, gastos = dato('ingresos_mensuales'), dato('gastos_mensuales')
    pagos, deuda = dato('pagos_mensuales_creditos'), dato('deuda_actual')
    return {
        'margen_capturado': importe(ingresos-gastos) if ingresos is not None and gastos is not None else None,
        'pagos_sobre_ingresos_pct': ratio(pagos, ingresos, True),
        'gastos_sobre_ingresos_pct': ratio(gastos, ingresos, True),
        'deuda_sobre_ingreso_mensual_veces': ratio(deuda, ingresos),
        'aviso': 'Indicadores descriptivos de datos capturados, no verificados. No cambian el riesgo demo ni establecen umbrales de aprobación.',
    }


def calcular(credito, cuotas, pagos, corte):
    total_pagado = Decimal(0)
    vencido = Decimal(0)
    max_atraso = 0
    vencidas, completas, puntuales = 0, 0, 0
    detalle = []
    for cuota in cuotas:
        movimientos = [p for p in pagos if p['cuota_id'] == cuota['id'] and p['fecha_pago'] <= corte]
        pagado = sum((p['importe'] for p in movimientos), Decimal(0))
        saldo = cuota['importe'] - pagado
        if saldo < 0:
            raise ValueError('Los pagos superan el importe pactado.')
        total_pagado += pagado
        atraso = (corte-cuota['vencimiento']).days if saldo > 0 and cuota['vencimiento'] < corte else 0
        max_atraso = max(max_atraso, atraso)
        if atraso:
            vencido += saldo
        if cuota['vencimiento'] < corte:
            vencidas += 1
            completas += saldo == 0
            puntuales += sum((p['importe'] for p in movimientos if p['fecha_pago'] <= cuota['vencimiento']), Decimal(0)) == cuota['importe']
        detalle.append({'id': str(cuota['id']), 'vencimiento': cuota['vencimiento'].isoformat(),
                        'importe': importe(cuota['importe']), 'pagado': importe(pagado), 'saldo': importe(saldo),
                        'dias_atraso': atraso, 'estado': 'Pagada' if saldo == 0 else 'Vencida' if atraso else 'Pendiente'})
    saldo_total = credito['monto_total_pactado'] - total_pagado
    acciones = (['Revisar las cuotas vencidas y registrar únicamente los pagos efectivamente recibidos.'] if vencido else
                ['Consultar las próximas fechas de vencimiento.'] if saldo_total else ['No hay saldo pendiente en el plan registrado.'])
    return {'fecha_corte': corte.isoformat(), 'moneda': 'MXN', 'total_pactado': importe(credito['monto_total_pactado']),
            'total_pagado': importe(total_pagado), 'saldo_pendiente': importe(saldo_total), 'saldo_vencido': importe(vencido),
            'dias_atraso_maximo': max_atraso, 'cuotas_vencidas': vencidas, 'cuotas_completas_vencidas': completas,
            'cuotas_pagadas_a_tiempo': puntuales, 'cumplimiento_cuotas_vencidas_pct': ratio(Decimal(completas), Decimal(vencidas), True),
            'puntualidad_cuotas_vencidas_pct': ratio(Decimal(puntuales), Decimal(vencidas), True),
            'cuotas': detalle, 'acciones_seguimiento': acciones,
            'aviso': 'Historial interno ficticio de obligaciones y pagos declarados. No consulta Buró ni verifica pagos bancarios. No predice incumplimientos ni autoriza créditos.'}
