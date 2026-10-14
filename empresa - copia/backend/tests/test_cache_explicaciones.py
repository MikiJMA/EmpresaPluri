"""Caché/cuotas con PostgreSQL temporal real y proveedores simulados."""
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import Mock, patch
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from fastapi import HTTPException
from backend.app.persistencia_postgresql.conexion import conectar, database_url
from backend.app.persistencia_postgresql.migrar import migrar
from backend.app.persistencia_postgresql.repositorio import RepositorioEvaluaciones
from backend.app.persistencia_postgresql.explicaciones import CacheExplicaciones
from backend.app.integraciones.cache_explicaciones import clave_explicacion

PAYLOAD = dict(rfc='DEMO-CACHE', ingresos_mensuales=30000, gastos_mensuales=10000, score_buro_actual=700)
RESULTADO = dict(version_modelo='reglas-demo-v1', margen_libre=20000, nivel_riesgo_preliminar='Bajo')


class ClaveCacheTests(unittest.TestCase):
    def test_clave_cambia_proveedor_modelo_y_no_usa_credenciales_ni_identidad(self):
        with patch.dict(os.environ, {'EXPLICACIONES_PROVEEDOR':'ollama','DOCUMENTOS_PROVEEDOR':'local','OLLAMA_MODEL':'llama3.1:8b'}):
            first = clave_explicacion(RESULTADO)
            with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY':'NO-USAR', 'AZURE_SEARCH_QUERY_KEY':'NO-USAR'}):
                self.assertEqual(first, clave_explicacion({**RESULTADO, 'rfc':'NO-USAR'}))
            with patch.dict(os.environ, {'OLLAMA_MODEL':'otro:8b'}):
                self.assertNotEqual(first, clave_explicacion(RESULTADO))
        self.assertEqual(len(first), 64)


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS') == '1', 'Requiere PostgreSQL temporal de la suite.')
class CachePostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.url = database_url()
        self.schema = 'test_cache_'+uuid4().hex
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.env = patch.dict(os.environ, {'DATABASE_URL':make_conninfo(self.url, options='-c search_path='+self.schema)})
        self.env.start()
        migrar(); migrar()
        self.repo = RepositorioEvaluaciones()
        self.cache = CacheExplicaciones()
        self.user = str(uuid4())
        self.key = 'a'*64
        self.generar = Mock(return_value={'explicacion':'Contenido sintético sin identidad', 'fuentes':[]})

    def tearDown(self):
        self.env.stop()
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def evaluacion(self):
        ident = uuid4()
        self.repo.guardar(ident, PAYLOAD, RESULTADO)
        return ident

    def test_repetir_con_otro_objeto_cache_o_usuario_no_genera_otra_vez(self):
        ident = self.evaluacion()
        first = self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        self.assertEqual(first, CacheExplicaciones().obtener_o_generar(ident, self.key, str(uuid4()), self.generar))
        self.generar.assert_called_once()
        with conectar() as conn:
            row = conn.execute('SELECT respuesta FROM cache_explicaciones').fetchone()['respuesta']
            self.assertNotIn('DEMO-CACHE', str(row))
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)

    def test_10_generaciones_por_hora_cache_no_consume_y_otra_cuenta_es_independiente(self):
        first = None
        for _ in range(10):
            ident = self.evaluacion()
            first = first or ident
            self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        self.cache.obtener_o_generar(first, self.key, self.user, self.generar)
        with self.assertRaises(HTTPException) as error:
            self.cache.obtener_o_generar(self.evaluacion(), self.key, self.user, self.generar)
        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(self.generar.call_count, 10)
        self.cache.obtener_o_generar(self.evaluacion(), self.key, str(uuid4()), self.generar)
        with conectar() as conn:
            conn.execute("UPDATE cuotas_explicaciones SET inicio=CURRENT_TIMESTAMP-INTERVAL '2 hours'")
        self.cache.obtener_o_generar(self.evaluacion(), self.key, self.user, self.generar)
        self.assertEqual(self.generar.call_count, 12)

    def test_error_se_conserva_y_cuenta_intento_antes_de_responder(self):
        ident = self.evaluacion()
        self.generar.side_effect = HTTPException(504, 'El proveedor tardó demasiado.')
        for _ in range(2):
            with self.assertRaises(HTTPException) as error:
                self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
            self.assertEqual(error.exception.status_code, 504)
        self.generar.assert_called_once()
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)
            conn.execute("UPDATE cache_explicaciones SET vence=CURRENT_TIMESTAMP-INTERVAL '1 minute'")
        with self.assertRaises(HTTPException):
            self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        self.assertEqual(self.generar.call_count, 2)

    def test_reserva_visible_antes_de_invocar_proveedor(self):
        def verificar_reserva():
            # Otra conexión ve el commit antes de cualquier llamada externa.
            with conectar() as conn:
                self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)
            return {'explicacion':'Fixture', 'fuentes':[]}
        self.cache.obtener_o_generar(self.evaluacion(), self.key, self.user, verificar_reserva)

    def test_error_inesperado_saneado_cacheado_y_contabilizado(self):
        ident = self.evaluacion()
        self.generar.side_effect = RecursionError('MARCADOR_PRIVADO_SINTETICO')
        for _ in range(3):
            with self.assertRaises(HTTPException) as error:
                self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
            self.assertEqual(error.exception.status_code, 503)
            self.assertNotIn('MARCADOR_PRIVADO_SINTETICO', str(error.exception.detail))
        self.generar.assert_called_once()
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)
        for _ in range(2):
            with conectar() as conn:
                conn.execute("UPDATE cache_explicaciones SET vence=CURRENT_TIMESTAMP-INTERVAL '1 minute'")
            with self.assertRaises(HTTPException):
                self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 3)
        self.assertEqual(self.generar.call_count, 3)

    def test_interrupcion_no_revierte_reserva_y_libera_locks(self):
        ident = self.evaluacion()
        self.generar.side_effect = SystemExit('Interrupción simulada; no termina el proceso de pruebas')
        with self.assertRaises(SystemExit):
            self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)
        self.generar.side_effect = None
        self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 2)

    def test_error_al_escribir_cache_no_revierte_cuota_y_libera_locks(self):
        ident = self.evaluacion()
        with patch('backend.app.persistencia_postgresql.explicaciones.Jsonb', side_effect=RuntimeError('Fallo sintético de almacenamiento')):
            with self.assertRaises(RuntimeError):
                self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 1)
            self.assertEqual(conn.execute('SELECT count(*) AS n FROM cache_explicaciones').fetchone()['n'], 0)
        self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 2)

    def test_fallos_inesperados_no_permiten_evitar_limite_de_diez(self):
        self.generar.side_effect = RuntimeError('Fixture')
        for _ in range(10):
            with self.assertRaises(HTTPException) as error:
                self.cache.obtener_o_generar(self.evaluacion(), self.key, self.user, self.generar)
            self.assertEqual(error.exception.status_code, 503)
        for _ in range(3):
            with self.assertRaises(HTTPException) as error:
                self.cache.obtener_o_generar(self.evaluacion(), self.key, self.user, self.generar)
            self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(self.generar.call_count, 10)
        with conectar() as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM cuotas_explicaciones').fetchone()['cantidad'], 10)

    def test_expiracion_o_clave_distinta_permiten_actualizacion_controlada(self):
        ident = self.evaluacion()
        self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        self.cache.obtener_o_generar(ident, 'b'*64, self.user, self.generar)
        with conectar() as conn:
            conn.execute("UPDATE cache_explicaciones SET vence=CURRENT_TIMESTAMP-INTERVAL '1 minute'")
        self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
        self.assertEqual(self.generar.call_count, 3)

    def test_concurrencia_misma_evaluacion_y_por_cuenta_no_duplica(self):
        first, other = self.evaluacion(), self.evaluacion()
        started, release = Event(), Event()
        def generar_lento():
            started.set()
            if not release.wait(5):
                raise RuntimeError('Fixture sin liberar')
            return {'explicacion':'Sintética', 'fuentes':[]}
        with ThreadPoolExecutor(max_workers=2) as executor:
            pending = executor.submit(self.cache.obtener_o_generar, first, self.key, self.user, generar_lento)
            try:
                self.assertTrue(started.wait(3))
                for ident in (first, other):
                    with self.assertRaises(HTTPException) as error:
                        self.cache.obtener_o_generar(ident, self.key, self.user, self.generar)
                    self.assertEqual(error.exception.status_code, 429)
                self.generar.assert_not_called()
            finally:
                release.set()
            self.assertEqual(pending.result(timeout=5)['explicacion'], 'Sintética')
        self.assertEqual(self.cache.obtener_o_generar(first, self.key, self.user, self.generar)['explicacion'], 'Sintética')
        self.generar.assert_not_called()
