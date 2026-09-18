"""Extracción selectiva del ZIP oficial usando rangos HTTP y la descarga parcial."""
import io
from pathlib import Path
import urllib.request
import zipfile

root = Path(__file__).resolve().parents[1] / 'empresa - copia' / '.local' / 'postgresql'
size = 341325378
directory = (root / 'zip-directory.bin').read_bytes()
prefix = (root / 'postgresql.zip').open('rb')
prefix_size = (root / 'postgresql.zip').stat().st_size
url = 'https://get.enterprisedb.com/postgresql/postgresql-17.11-3-windows-x64-binaries.zip'

class Archive(io.RawIOBase):
    def __init__(self): self.pos = 0; self.cache = {}
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else size + offset
        return self.pos
    def read(self, n=-1):
        if n < 0: n = size - self.pos
        n = min(n, size - self.pos)
        chunks = []
        while n > 0:
            if self.pos >= size - len(directory):
                block = directory[self.pos - (size - len(directory)):][:n]
            elif self.pos < prefix_size:
                prefix.seek(self.pos)
                block = prefix.read(min(n, prefix_size - self.pos))
            else:
                unit = 4 * 1024 * 1024
                start = self.pos // unit * unit
                if start not in self.cache:
                    end = min(size - 1, start + unit - 1)
                    req = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
                    with urllib.request.urlopen(req, timeout=90) as response:
                        if response.status != 206: raise RuntimeError('Servidor no admite rangos')
                        self.cache[start] = response.read()
                    print('Descargado bloque requerido', start, flush=True)
                block = self.cache[start][self.pos-start:self.pos-start+n]
            if not block: raise RuntimeError('Lectura incompleta')
            chunks.append(block); self.pos += len(block); n -= len(block)
        return b''.join(chunks)

with zipfile.ZipFile(Archive()) as archive:
    selected = [x for x in archive.infolist() if x.filename.startswith(('pgsql/bin/', 'pgsql/lib/', 'pgsql/share/'))]
    print('Archivos del servidor:', len(selected), flush=True)
    for entry in selected:
        target = (root / entry.filename).resolve()
        if not target.is_relative_to(root.resolve()): raise RuntimeError('Ruta no válida')
        archive.extract(entry, root)
print('Servidor PostgreSQL extraído y CRC verificados.')
