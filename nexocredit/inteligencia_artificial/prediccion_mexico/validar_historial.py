"""Inspección local de un CSV autorizado; salida agregada sin valores personales ni entrenamiento."""
import argparse
import csv
from datetime import date
import json
from pathlib import Path

from backend.app.validacion_datos.historial_piloto import validar_historial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', required=True, type=Path)
    parser.add_argument('--fecha-corte', required=True, type=date.fromisoformat)
    parser.add_argument('--horizonte-dias', required=True, type=int)
    parser.add_argument('--atraso-umbral-dias', required=True, type=int)
    parser.add_argument('--datos-autorizados', required=True, action='store_true',
                        help='Confirmación del operador; no sustituye verificar autorización y anonimización.')
    args = parser.parse_args()
    try:
        if args.csv.stat().st_size > 25_000_000:
            raise ValueError('Máximo 25 MB por comprobación.')
        with args.csv.open(encoding='utf-8-sig', newline='') as fuente:
            informe = validar_historial(fuente, fecha_corte=args.fecha_corte, horizonte_dias=args.horizonte_dias,
                                       atraso_umbral_dias=args.atraso_umbral_dias)
    except (OSError, ValueError, UnicodeError, csv.Error):
        print(json.dumps({'error': 'No se pudo validar el CSV. Revisar permisos, tamaño, codificación y contrato; no se muestran datos privados.'}))
        return 2
    print(json.dumps(informe, ensure_ascii=False))
    return 0 if informe['contrato_valido'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
