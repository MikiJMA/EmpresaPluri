"""Referencia de indicadores SQL para conciliar Power BI; estrictamente solo lectura."""
import json
from pathlib import Path
import sys

import psycopg

PRIVATE = Path(__file__).resolve().parents[1] / '.local/powerbi/.env'
AGGREGATE = """
SELECT count(*) AS total_evaluaciones,
       avg(margen_libre) AS margen_promedio,
       avg(ingresos_mensuales) AS ingresos_promedio,
       avg(deuda_actual) AS deuda_promedio,
       count(deuda_actual) AS evaluaciones_con_deuda,
       count(deuda_actual)::numeric / nullif(count(*), 0) AS cobertura_deuda
FROM reportes.evaluaciones_powerbi
"""


def indicadores(conn, riesgo=None, estado=None):
    filters = []
    params = []
    for column, value in (('riesgo_demo', riesgo), ('estado_revision', estado)):
        if value is not None:
            filters.append(f'{column} = %s')
            params.append(value)
    query = AGGREGATE + (' WHERE ' + ' AND '.join(filters) if filters else '')
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        values = cursor.fetchone()
        return {column.name: value for column, value in zip(cursor.description, values)}


def verificar():
    # Lee la credencial privada sin copiarla a informes, argumentos ni registros.
    config = dict(line.split('=', 1) for line in PRIVATE.read_text(encoding='utf-8').splitlines() if '=' in line)
    if config.get('SERVER') != '127.0.0.1:55433' or config.get('DATABASE') != 'pluri_credito' or config.get('USER') != 'pluri_powerbi':
        raise ValueError('Configuración fuera del lector local esperado.')
    with psycopg.connect(host='127.0.0.1', port=55433, dbname='pluri_credito', user='pluri_powerbi',
                          password=config['PASSWORD'], connect_timeout=10,
                          options='-c default_transaction_read_only=on -c statement_timeout=10000') as conn:
        if conn.execute('SHOW transaction_read_only').fetchone()[0] != 'on':
            raise ValueError('Se requiere una conexión de solo lectura.')
        result = {'sin_filtros': indicadores(conn), 'por_riesgo': {}, 'por_revision': {}, 'filtros_combinados': []}
        for riesgo in ('Bajo', 'Medio', 'Alto'):
            result['por_riesgo'][riesgo] = indicadores(conn, riesgo=riesgo)
        for estado in ('Pendiente', 'Aprobada', 'Rechazada'):
            result['por_revision'][estado] = indicadores(conn, estado=estado)
        for riesgo in ('Bajo', 'Medio', 'Alto'):
            for estado in ('Pendiente', 'Aprobada', 'Rechazada'):
                result['filtros_combinados'].append({'riesgo': riesgo, 'revision': estado, **indicadores(conn, riesgo, estado)})
        for group in ('por_riesgo', 'por_revision'):
            if sum(item['total_evaluaciones'] for item in result[group].values()) != result['sin_filtros']['total_evaluaciones']:
                raise ValueError('Hay valores de riesgo o revisión fuera de los esperados.')
        for query in ('SELECT * FROM public.evaluaciones LIMIT 0', 'SELECT * FROM public.revisiones LIMIT 0'):
            try:
                with conn.transaction():
                    conn.execute(query)
            except psycopg.errors.InsufficientPrivilege:
                pass
            else:
                raise ValueError('El lector tiene acceso indebido a tablas originales.')
        result['nota'] = ('Cifras SQL reales para comparación manual en Power BI después de Actualizar. '
                          'No acreditan por sí solas que Power BI haya ejecutado DAX ni actualizado su caché.')
        return result


if __name__ == '__main__':
    try:
        print(json.dumps(verificar(), ensure_ascii=False, indent=2, default=str))
    except Exception:
        print('No se completó la verificación. Revisa PostgreSQL y la configuración privada del lector; no se muestran credenciales ni detalles internos.', file=sys.stderr)
        sys.exit(1)
