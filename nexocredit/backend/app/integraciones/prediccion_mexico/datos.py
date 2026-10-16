"""Preparación de entrenamiento ENIF. Nunca utilizada para consultar expedientes personales."""
from backend.app.validacion_datos.perfil_enif import PerfilENIF, TIPOS_CREDITO, vectorizar


def preparar(frame):
    import numpy as np
    filas, etiquetas, grupos = [], [], []
    rechazos = {'sin_credito': 0, 'atraso_desconocido': 0, 'perfil_incompleto': 0}
    for row in frame.to_dict('records'):
        indices = [i for i in range(1, 10) if row[f'P6_2_{i}'] == '1']
        if not indices:
            rechazos['sin_credito'] += 1
            continue
        respuestas = [row[f'P6_3_{i}'] for i in indices]
        if any(valor not in ('1', '2') for valor in respuestas):
            rechazos['atraso_desconocido'] += 1
            continue
        try:
            perfil = PerfilENIF(ingreso_laboral=float(row['P3_11A']), periodicidad=int(row['P3_11B']),
                                ingreso_variable=int(row['P3_12']), presupuesto=int(row['P4_1']),
                                gastos_cubiertos=int(row['P4_3']), ahorro_emergencia=int(row['P4_10']),
                                creditos=[TIPOS_CREDITO[i - 1] for i in indices])
        except (ValueError, TypeError):
            rechazos['perfil_incompleto'] += 1
            continue
        filas.append(vectorizar(perfil))
        etiquetas.append(int('1' in respuestas))
        grupos.append(row['UPM_DIS'])
    return np.asarray(filas), np.asarray(etiquetas), np.asarray(grupos), rechazos
