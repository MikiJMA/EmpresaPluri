"""Configuración local sin sobrescribir las variables del proceso."""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

CONFIG = Path(__file__).resolve().parents[2] / '.env.postgresql'


def database_url():
    load_dotenv(CONFIG, override=False)
    return os.getenv('DATABASE_URL', '').strip()


def conectar():
    return psycopg.connect(database_url(), connect_timeout=5, row_factory=dict_row)
