"""Paquete público: fixtures temporales, sin PostgreSQL, Docker o red."""
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import stat
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from scripts import preparar_entrega as paquete


class PaqueteEntregaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nexocredit-paquete-test-')
        self.addCleanup(self.temp.cleanup)
        self.outer = Path(self.temp.name)
        self.project = self.outer / paquete.PROJECT_DIR
        self.project.mkdir()
        for relative in paquete.REQUIRED_PROJECT:
            self.write(relative, b'contenido publico\n')
        self.write(paquete.PLAN, ('# Plan\n\n## Identificación\n\n'
                                'PERSONAL_SENTINEL\n\n## Tecnologías obligatorias\n\n'
                                'Python y FastAPI\n').encode('utf-8'))
        self.write(paquete.BACKGROUND, b'PNG-ficticio-no-una-captura')
        self.write('backend/app/integraciones/prediccion_local/artefactos/modelo.json', b'{"pesos":[1]}')
        self.write('backend/app/integraciones/prediccion_local/artefactos/entrenamiento.json', b'{"semilla":12}')
        self.github = self.outer / '.github' / 'workflows'
        self.github.mkdir(parents=True)
        (self.github / 'ci.yml').write_text('jobs:\n  backend:\n    working-directory: empresa - copia\n'
                                          '  frontend:\n    working-directory: empresa - copia/frontend\n', encoding='utf-8')
        (self.outer / 'NexoCredit.code-workspace').write_text(json.dumps({
            'folders': [{'path': paquete.PROJECT_DIR}, {'path': '.github'}]}), encoding='utf-8')
        self.git = patch.object(paquete, 'referencia_git', return_value='a' * 40)
        self.git.start()
        self.addCleanup(self.git.stop)

    def write(self, relative, data=b'PRIVATE_SENTINEL'):
        path = self.project / Path(str(relative))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    @contextmanager
    def enlace_de_directorio(self, link, target):
        """Enlace real si se permite; equivalente lstat si Windows exige privilegios."""
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            link.mkdir()
            real_lstat = os.lstat
            fake = type('StatSymlink', (), {'st_mode': stat.S_IFLNK | 0o755,
                                          'st_file_attributes': paquete.REPARSE_POINT})()

            def simulated_lstat(path, *args, **kwargs):
                return fake if Path(path) == link else real_lstat(path, *args, **kwargs)

            with patch.object(paquete.os, 'lstat', side_effect=simulated_lstat):
                yield
        else:
            yield

    def test_nombre_cli_no_admite_paths_extensiones_o_dispositivos(self):
        self.assertEqual(paquete.validar_nombre('NexoCredit_Entrega_2026-10-14'), 'NexoCredit_Entrega_2026-10-14')
        for invalid in ('../escape', 'C:\\otro', '/tmp/a', 'demo.zip', '', 'CON', 'LPT1', 'a' * 81, 'a b'):
            with self.subTest(invalid=invalid), self.assertRaises(paquete.EntregaError):
                paquete.validar_nombre(invalid)

    def test_allowlist_excluye_privados_binarios_datasets_y_capturas(self):
        included = ('backend/app/main.py', 'frontend/src/App.jsx', 'docs/manuales/OPERACION.md',
                    'frontend/package-lock.json', 'infraestructura/frontend.Dockerfile',
                    'infraestructura/.env.example', '.gitignore', 'modelo/modelo.json',
                    'modelo/entrenamiento.json', 'analitica/reporte.pbix.pbip',
                    'analitica/reporte.pbix.SemanticModel/definition/model.tmdl',
                    'infraestructura/contenedores_docker/inicializar_postgresql.sql',
                    'backend/app/persistencia_postgresql/migraciones/001_evaluaciones.sql',
                    str(paquete.BACKGROUND), 'frontend/public/favicon.svg')
        excluded = ('.env', '.env.privado', '.env.local', '.env.example.backup',
                    'infraestructura/.ENV', 'docs/estadia/ALUMNO.md', 'docs/privado/datos.json',
                    '.local/datos.json', '.tmp/datos.py', '.venv-roto/archivo.py',
                    '.vscode/settings.json', '.git/config', 'node_modules/index.js',
                    'frontend/dist/index.html', 'analitica/.pbi/cache.json',
                    'analitica/.pbi-respaldo/settings.json', 'modelo/model.pkl',
                    'modelo/modelo.pickle', 'base.dump', 'base.sql.gz', 'datos/prueba.csv',
                    'datos/dump.sql', 'backend/backup.sql', 'db.sql',
                    'reporte.pbix', 'reporte.abf', 'docs/evidencias/dashboard.jpg',
                    'docs/evidencias/dashboard.png', 'frontend/public/captura.png')
        for path in included:
            with self.subTest(path=path):
                self.assertTrue(paquete.permitir_archivo(path))
        for path in excluded:
            with self.subTest(path=path):
                self.assertFalse(paquete.permitir_archivo(path))

    def test_rutas_zip_rechazan_traversal_ads_y_aliases_windows(self):
        for path in ('../a.py', '/a.py', 'a\\b.py', 'a:secret.py', 'a./b.py', 'AUX/file.py', 'a /b.py'):
            with self.subTest(path=path), self.assertRaises(paquete.EntregaError):
                paquete.permitir_archivo(path)

    def test_redaccion_solo_copia_y_delimitadores_fallan_cerrado(self):
        source = self.project / Path(str(paquete.PLAN))
        before = source.read_bytes()
        copied = paquete.redactar_plan(before)
        self.assertNotIn(b'PERSONAL_SENTINEL', copied)
        self.assertIn('## Tecnologías obligatorias'.encode(), copied)
        self.assertEqual(source.read_bytes(), before)
        for invalid in (b'# Sin limites', before.replace('## Identificación'.encode(), b'## Otra'),
                        before + '\n## Identificación\n'.encode()):
            with self.subTest(invalid=invalid), self.assertRaises(paquete.EntregaError):
                paquete.redactar_plan(invalid)

    def test_env_estadia_y_carpetas_privadas_no_se_abren_ni_recorren(self):
        forbidden_files = {
            self.write('.env'), self.write('infraestructura/contenedores_docker/.env'),
            self.write('docs/estadia/ALUMNO.md'), self.write('.local/prohibido.json'),
            self.write('frontend/node_modules/prohibido.js'),
            self.write('docs/privado/prohibido.md'), self.write('analitica/.pbi/prohibido.json'),
        }
        private_dirs = {self.project / '.local', self.project / 'frontend/node_modules',
                        self.project / 'docs/estadia', self.project / 'docs/privado',
                        self.project / 'analitica/.pbi'}
        real_open, real_scandir = os.open, os.scandir
        opened, walked = [], []

        def guarded_open(path, *args, **kwargs):
            candidate = Path(path)
            self.assertNotIn(candidate, forbidden_files)
            opened.append(candidate)
            return real_open(path, *args, **kwargs)

        def guarded_scandir(path):
            candidate = Path(path)
            self.assertNotIn(candidate, private_dirs)
            walked.append(candidate)
            return real_scandir(path)

        with patch.object(paquete.os, 'open', side_effect=guarded_open), \
                patch.object(paquete.os, 'scandir', side_effect=guarded_scandir):
            files = paquete.recopilar_archivos(self.outer, self.project)
        self.assertTrue(opened)
        self.assertTrue(walked)
        self.assertFalse(any(b'PRIVATE_SENTINEL' in record.contenido for record in files))
        alumno = next(record for record in files if record.ruta.endswith('/docs/estadia/ALUMNO.md'))
        self.assertEqual(alumno.origen, 'marcador-generado')
        self.assertIn(b'marcador', alumno.contenido)

    def test_dotfiles_publicos_incluidos_pero_directorios_homonimos_no_se_recorren(self):
        self.write('.gitignore', b'public-gitignore')
        self.write('.dockerignore', b'public-dockerignore')
        self.write('plantillas/.env.example', b'PUBLIC_TEMPLATE')
        self.write('privados-en-dotfile/.env.example/no_leer.py')
        self.write('privados-en-dotfile/.gitignore/no_leer.py')
        self.write('privados-en-dotfile/.dockerignore/no_leer.py')
        records = paquete.recopilar_archivos(self.outer, self.project)
        names = {record.ruta for record in records}
        for relative in ('.gitignore', '.dockerignore', 'plantillas/.env.example',
                         'infraestructura/contenedores_docker/.env.example'):
            self.assertIn(f'NexoCredit/empresa - copia/{relative}', names)
        self.assertFalse(any('no_leer.py' in name for name in names))

    def test_zip_wrapper_manifiesto_huellas_y_modelo_incluido(self):
        result = paquete.crear_paquete(self.outer, self.project, 'NexoCredit_Entrega_test')
        self.assertEqual(result['zip'].parent, self.outer / 'output/entregas')
        manifest = json.loads(result['manifiesto'].read_text(encoding='utf-8'))
        self.assertEqual(manifest['git_sha'], 'a' * 40)
        self.assertEqual(manifest['sha256_zip'], hashlib.sha256(result['zip'].read_bytes()).hexdigest())
        with ZipFile(result['zip']) as archive:
            self.assertIsNone(archive.testzip())
            names = archive.namelist()
            self.assertEqual(len(names), manifest['numero_archivos'])
            self.assertEqual(set(names), {record['ruta'] for record in manifest['archivos']})
            self.assertIn('NexoCredit/.github/workflows/ci.yml', names)
            self.assertIn('NexoCredit/NexoCredit.code-workspace', names)
            self.assertIn('NexoCredit/LEEME_PRIMERO.md', names)
            for file in manifest['archivos']:
                data = archive.read(file['ruta'])
                self.assertEqual(file['sha256'], hashlib.sha256(data).hexdigest())
                self.assertEqual(file['tamano_bytes'], len(data))
                self.assertTrue(file['ruta'].startswith('NexoCredit/'))
                self.assertNotIn('..', PurePosixPath(file['ruta']).parts)
            for basename in ('modelo.json', 'entrenamiento.json'):
                self.assertTrue(any(name.endswith('/artefactos/' + basename) for name in names))
            plan = archive.read('NexoCredit/empresa - copia/' + str(paquete.PLAN))
            self.assertNotIn(b'PERSONAL_SENTINEL', plan)
            checklist = archive.read('NexoCredit/LEEME_PRIMERO.md').decode()
            self.assertIn('NO IA generativa', checklist)
            self.assertIn('docker.ps1 iniciar', checklist)
            self.assertIn('modo-local.ps1 -Accion usuario', checklist)

    def test_no_sobrescribir_zip_o_manifiesto_existentes(self):
        destination = self.outer / 'output/entregas'
        destination.mkdir(parents=True)
        for suffix in ('.zip', '.manifest.json'):
            with self.subTest(suffix=suffix):
                existing = destination / ('ocupado' + suffix)
                existing.write_bytes(b'NO_CAMBIAR')
                with self.assertRaises(paquete.EntregaError):
                    paquete.crear_paquete(self.outer, self.project, 'ocupado')
                self.assertEqual(existing.read_bytes(), b'NO_CAMBIAR')
                existing.unlink()

    def test_validacion_estructura_no_produce_archivos_si_falta_modelo(self):
        (self.project / 'backend/app/integraciones/prediccion_local/artefactos/modelo.json').unlink()
        with self.assertRaises(paquete.EntregaError):
            paquete.crear_paquete(self.outer, self.project, 'incompleto')
        self.assertFalse((self.outer / 'output').exists())

    def test_workspace_ci_y_raiz_activa_deben_ser_relativos(self):
        workspace = self.outer / 'NexoCredit.code-workspace'
        workspace.write_text('{"folders":[{"path":"C:/otro"}]}', encoding='utf-8')
        with self.assertRaises(paquete.EntregaError):
            paquete.recopilar_archivos(self.outer, self.project)
        with self.assertRaises(paquete.EntregaError):
            paquete.recopilar_archivos(self.outer, self.outer)

    def test_rechazar_junction_mediante_atributo_sin_leer_destino(self):
        fake = type('StatJunction', (), {'st_mode': stat.S_IFDIR | 0o755,
                                        'st_file_attributes': paquete.REPARSE_POINT})()
        with patch.object(paquete.os, 'lstat', return_value=fake), self.assertRaises(paquete.EntregaError):
            paquete._sin_enlace(self.project / 'junction')

    def test_archivo_fuera_raiz_y_enlace_fisico_se_rechazan(self):
        outside = self.outer / 'fuera.py'
        outside.write_bytes(b'FUERA_NO_LEER')
        with self.assertRaises(paquete.EntregaError):
            paquete.leer_publico(outside, self.project)
        linked = self.project / 'backend/duro.py'
        try:
            os.link(outside, linked)
        except (OSError, NotImplementedError):
            fake = type('StatHardlink', (), {'st_mode': stat.S_IFREG | 0o644, 'st_nlink': 2,
                                            'st_file_attributes': 0, 'st_size': 10})()
            with self.assertRaises(paquete.EntregaError):
                paquete._regular(fake)
        else:
            with self.assertRaises(paquete.EntregaError):
                paquete.recopilar_archivos(self.outer, self.project)

    def test_symlink_de_archivo_o_carpeta_no_se_sigue(self):
        outside = self.outer / 'outside'
        outside.mkdir()
        (outside / 'publico.py').write_bytes(b'FUERA_NO_LEER')
        link = self.project / 'backend/enlace'
        with self.enlace_de_directorio(link, outside), self.assertRaises(paquete.EntregaError):
            paquete.recopilar_archivos(self.outer, self.project)

    def test_destino_junction_se_rechaza_y_no_escribe_fuera_output(self):
        output = self.outer / 'output'
        outside = self.outer / 'ajeno'
        outside.mkdir()
        with self.enlace_de_directorio(output, outside), self.assertRaises(paquete.EntregaError):
            paquete.crear_paquete(self.outer, self.project, 'escapa')
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
