"""Crear/resetear una cuenta local sin password en argumentos ni salida.

Dentro del backend: python scripts/crear_usuario_local.py --usuario asesor --nombre "Asesor demo"
--actualizar cambia password/roles y revoca sesiones anteriores. --desactivar revoca la cuenta.
"""
import argparse
from getpass import getpass, GetPassWarning
from pathlib import Path
import sys
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg
from backend.app.autenticacion_local.contrasenas import MIN_CARACTERES_PASSWORD, MAX_CARACTERES_PASSWORD
from backend.app.autenticacion_local.repositorio import RepositorioUsuarios
from backend.app.persistencia_postgresql.conexion import database_url


def main(argv=None):
    parser = argparse.ArgumentParser(description='Administrar una cuenta NexoCredit local. No hay contraseñas por defecto.')
    parser.add_argument('--usuario', required=True)
    parser.add_argument('--nombre')
    parser.add_argument('--rol', choices=['Analista', 'Administrador'], default='Analista')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--actualizar', action='store_true', help='Autoriza expresamente el cambio y revoca sesiones previas.')
    mode.add_argument('--desactivar', action='store_true', help='Bloquea la cuenta y revoca sesiones previas.')
    args = parser.parse_args(argv)
    if not database_url():
        parser.error('Configura DATABASE_URL privada y aplica las migraciones antes de continuar.')
    try:
        repo = RepositorioUsuarios()
        if args.desactivar:
            repo.desactivar(args.usuario)
            print('Cuenta local desactivada y sesiones revocadas.')
            return 0
        if not args.nombre:
            parser.error('--nombre es obligatorio para crear o actualizar una cuenta.')
        with warnings.catch_warnings():
            # No permitir el fallback de getpass que haría visible la contraseña.
            warnings.simplefilter('error', GetPassWarning)
            password = getpass(f'Contraseña nueva ({MIN_CARACTERES_PASSWORD}–{MAX_CARACTERES_PASSWORD} caracteres; entrada oculta): ')
            confirmar = getpass('Confirma la contraseña (entrada oculta): ')
        if password != confirmar:
            raise ValueError('Las contraseñas no coinciden. No se cambió la cuenta.')
        repo.guardar(args.usuario, args.nombre, password, [args.rol], actualizar=args.actualizar)
        print('Cuenta local actualizada; sesiones anteriores revocadas.' if args.actualizar else 'Cuenta local creada correctamente.')
        print('No compartas la contraseña ni los archivos privados de configuración.')
        return 0
    except ValueError as error:
        print(str(error), file=sys.stderr)
    except psycopg.Error:
        print('No se pudo administrar la cuenta. Verifica PostgreSQL y la migración 003; no se muestran datos privados.', file=sys.stderr)
    except GetPassWarning:
        print('Se requiere una consola interactiva con entrada oculta (docker exec -it). No se leyó la contraseña.', file=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        print('Operación cancelada; no se guardó una contraseña nueva.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
