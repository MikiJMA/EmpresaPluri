"""Pruebas sin Docker, secretos ni base real del mecanismo de recuperacion."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from scripts import respaldo_postgresql as backup

IDENTITY = {'container': 'a' * 64, 'image': 'sha256:' + 'b' * 64}
FINGERPRINTS = {'inventario': [['public', 'evaluaciones']],
                'datos': [{'nombre': 'public.evaluaciones', 'filas': 7, 'huella': 'ficticia'}],
                'columnas': [], 'restricciones': [], 'vistas': []}


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / 'respaldos'
        self.base.mkdir()
        self.folder = self.base / 'prueba'
        self.folder.mkdir()
        self.archive = self.folder / 'base.dump'
        self.archive.write_bytes(b'PGDMPdatos-ficticios')
        self.manifest = {'format': 1, 'database': backup.DATABASE, 'archive': 'base.dump',
                         'source': IDENTITY, 'sha256': hashlib.sha256(self.archive.read_bytes()).hexdigest(),
                         'fingerprints': FINGERPRINTS}
        self.save_manifest()
        self.env = patch.object(backup, 'BACKUPS', self.base)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def save_manifest(self):
        (self.folder / 'manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_archivo_integro_y_manifiesto(self):
        path, data = backup.read_backup(self.folder)
        self.assertEqual(path, self.folder.resolve())
        self.assertEqual(data['fingerprints'], FINGERPRINTS)

    def test_rechaza_manipulacion_antes_de_docker(self):
        self.archive.write_bytes(b'PGDMPdatos-distintos')
        with patch.object(backup, 'run') as command, self.assertRaises(backup.BackupError):
            backup.restore_test('docker-ficticio', self.folder)
        command.assert_not_called()

    def test_rechaza_destino_fuera_de_carpeta_privada(self):
        for path in [self.base, self.base.parent, self.base / '..' / 'ajeno', self.folder / 'anidado']:
            with self.assertRaises(backup.BackupError):
                backup.validate_backup_path(path)

    def test_rechaza_manifiestos_ajenos_o_incompletos(self):
        for field, bad in [('database', 'otra'), ('format', 2), ('archive', '../secreto'), ('sha256', 'incorrecto')]:
            data = dict(self.manifest)
            data[field] = bad
            with patch.object(backup.json, 'loads', return_value=data), self.assertRaises(backup.BackupError):
                backup.read_backup(self.folder)
        (self.folder / 'manifest.json').unlink()
        with self.assertRaises(backup.BackupError):
            backup.read_backup(self.folder)

    def test_escape_de_identificadores_y_literales(self):
        query = backup.fingerprint_query([('esquema"raro', "tabla'; DROP DATABASE principal; --")])
        self.assertIn('"esquema""raro"', query)
        self.assertIn("tabla''; DROP DATABASE principal; --", query)
        self.assertIn('FROM ONLY "esquema""raro"."tabla\'; DROP DATABASE principal; --"', query)
        self.assertNotIn('DROP DATABASE principal; --\n', query)

    def test_no_expone_stderr_privado(self):
        failed = subprocess.CompletedProcess(['ficticio'], 1, b'', b'password=secreto')
        with patch.object(backup.subprocess, 'run', return_value=failed), self.assertRaises(backup.BackupError) as error:
            backup.run(['ficticio'])
        self.assertNotIn('secreto', str(error.exception))

    def test_no_sobrescribe_manifiestos(self):
        with self.assertRaises(FileExistsError):
            backup.write_json_new(self.folder / 'manifest.json', {'otro': True})
        self.assertEqual(json.loads((self.folder / 'manifest.json').read_text()), self.manifest)

    def test_cleanup_nunca_elimina_origen_ni_contenedor_ajeno(self):
        with patch.object(backup, 'run') as command:
            with self.assertRaises(backup.BackupError):
                backup.cleanup_test_container('docker', IDENTITY['container'], 'marca', IDENTITY['container'])
            with patch.object(backup, 'inspect_value', return_value='otra-marca'), self.assertRaises(backup.BackupError):
                backup.cleanup_test_container('docker', 'c' * 64, 'marca', IDENTITY['container'])
            command.assert_not_called()

    def test_restauracion_solo_temporal_sin_red_y_con_limpieza(self):
        calls = []
        def fake_run(args, **kwargs):
            calls.append(args)
            output = ('c' * 64).encode() if 'run' in args else json.dumps(FINGERPRINTS).encode() if 'psql' in args else b''
            if 'pg_restore' in args:
                self.assertNotIn(backup.SOURCE, args)
                self.assertIn('--single-transaction', args)
                self.assertNotIn('--clean', args)
                self.assertNotIn('--create', args)
            return subprocess.CompletedProcess(args, 0, output, b'')
        def inspect(_docker, _container, template):
            return 'none' if 'NetworkMode' in template else 'null' if 'Binds' in template else '{}'
        with patch.object(backup, 'run', side_effect=fake_run), patch.object(backup, 'source_identity', return_value=IDENTITY), \
                patch.object(backup, 'inspect_value', side_effect=inspect), patch.object(backup, 'cleanup_test_container') as cleanup:
            report = backup.restore_test('docker', self.folder)
        self.assertTrue(report['success'])
        self.assertIn('--network=none', calls[0])
        self.assertIn('--pull=never', calls[0])
        cleanup.assert_called_once()
        self.assertEqual(cleanup.call_args.args[1], 'c' * 64)
        self.assertTrue(list(self.folder.glob('restauracion-*.json')))

    def test_fallo_comparacion_no_acredita_exito_y_limpia(self):
        with patch.object(backup, 'run', side_effect=[subprocess.CompletedProcess([], 0, ('c' * 64).encode()),
                subprocess.CompletedProcess([], 0, b''), subprocess.CompletedProcess([], 0, b''),
                subprocess.CompletedProcess([], 0, b'{}')]), \
                patch.object(backup, 'source_identity', return_value=IDENTITY), \
                patch.object(backup, 'inspect_value', side_effect=['none', '{}', 'null']), \
                patch.object(backup, 'cleanup_test_container') as cleanup, self.assertRaises(backup.BackupError):
            backup.restore_test('docker', self.folder)
        cleanup.assert_called_once()
        self.assertFalse(list(self.folder.glob('restauracion-*.json')))

    def test_respaldo_compartido_con_instantanea_y_transaccion_solo_lectura(self):
        connection = MagicMock()
        def query_result(query):
            result = MagicMock()
            if query == 'SELECT pg_export_snapshot()': result.fetchone.return_value = ['instantanea-ficticia']
            elif query == backup.CATALOG_SQL: result.fetchall.return_value = FINGERPRINTS['inventario']
            else: result.fetchone.return_value = [FINGERPRINTS]
            return result
        connection.execute.side_effect = query_result
        connection.__enter__.return_value = connection
        def fake_run(args, **kwargs):
            if 'pg_dump' in args:
                self.assertIn('--snapshot=instantanea-ficticia', args)
                self.assertNotIn('--clean', args)
                kwargs['stdout'].write(b'PGDMPficticio')
            return subprocess.CompletedProcess(args, 0, b'', b'')
        with patch.object(backup, 'source_identity', return_value=IDENTITY), \
                patch.object(backup, 'private_directory', side_effect=lambda path: path.mkdir(parents=True, exist_ok=True)), \
                patch.object(backup, 'dotenv_values', return_value={'POSTGRES_ADMIN_PASSWORD': 'clave-ficticia'}), \
                patch.object(backup.psycopg, 'connect', return_value=connection), patch.object(backup, 'run', side_effect=fake_run):
            folder, manifest = backup.create_backup('docker-ficticio')
        self.assertTrue((folder / 'manifest.json').is_file())
        self.assertEqual(manifest['fingerprints'], FINGERPRINTS)
        self.assertIn('READ ONLY', connection.execute.call_args_list[0].args[0])
        connection.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
