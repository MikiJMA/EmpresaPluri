from hashlib import sha256
from uuid import UUID, uuid4, uuid5
from decimal import Decimal
from fastapi import HTTPException
from psycopg.types.json import Jsonb
from backend.app.persistencia_postgresql.conexion import conectar, database_url
from .analisis import calcular, indicadores, importe
from .modelos import hoy_utc


class RepositorioSeguimiento:
    def _actor(self, user):
        return sha256(user['id'].encode()).hexdigest()

    def _repetido(self, conn, ident, credito_id, accion, datos, user):
        event = conn.execute('SELECT * FROM eventos_seguimiento_demo WHERE id=%s', (ident,)).fetchone()
        if event is None:
            return False
        if (event['credito_id'] != credito_id or event['accion'] != accion or event['datos'] != datos
                or event['actor_hash'] != self._actor(user)):
            raise HTTPException(409, 'La clave de reintento ya corresponde a otra operación o cuenta.')
        return True

    def _evento(self, conn, ident, credito_id, accion, datos, user):
        conn.execute('INSERT INTO eventos_seguimiento_demo(id,credito_id,accion,actor_hash,responsable,datos) VALUES(%s,%s,%s,%s,%s,%s)',
                     (ident, credito_id, accion, self._actor(user), user['responsable'], Jsonb(datos)))

    def _credito(self, conn, ident, bloquear=False):
        row = conn.execute('SELECT * FROM creditos_demo WHERE id=%s'+(' FOR UPDATE' if bloquear else ''), (ident,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Crédito ficticio no encontrado.')
        return row

    def _detalle(self, conn, row):
        cuotas = conn.execute('SELECT * FROM cuotas_demo WHERE credito_id=%s ORDER BY vencimiento', (row['id'],)).fetchall()
        pagos = conn.execute('SELECT * FROM pagos_demo WHERE credito_id=%s ORDER BY fecha_pago,id', (row['id'],)).fetchall()
        solicitud = conn.execute('SELECT solicitud FROM evaluaciones WHERE id=%s', (row['evaluacion_id'],)).fetchone()['solicitud']
        return {'id': str(row['id']), 'evaluacion_id': str(row['evaluacion_id']), 'concepto': row['concepto'],
                'fecha_apertura': row['fecha_apertura'].isoformat(), 'alertas_revisadas': row['alertas_revisadas'],
                'resumen': calcular(row, cuotas, pagos, hoy_utc()), 'indicadores': indicadores(solicitud),
                'pagos': [{**p, 'importe': importe(p['importe'])} for p in pagos],
                'alertas': [{**a, 'saldo': importe(a['saldo'])} for a in conn.execute('SELECT * FROM alertas_credito_demo WHERE credito_id=%s ORDER BY detectada,id', (row['id'],)).fetchall()]}

    def _alertas(self, conn, row, user):
        resumen = self._detalle(conn, row)['resumen']
        for cuota in resumen['cuotas']:
            ident = UUID(cuota['id'])
            anterior = conn.execute('SELECT * FROM alertas_credito_demo WHERE cuota_id=%s', (ident,)).fetchone()
            vencida = cuota['dias_atraso'] > 0
            if anterior is None and not vencida:
                continue
            estado = (anterior['estado'] if anterior and anterior['estado'] != 'Resuelta' else 'Pendiente') if vencida else 'Resuelta'
            if anterior and (anterior['estado'], anterior['saldo'], anterior['dias_atraso']) == (estado, Decimal(cuota['saldo']), cuota['dias_atraso']):
                continue
            alerta_id = uuid5(ident, 'CUOTA_VENCIDA')
            conn.execute('''INSERT INTO alertas_credito_demo(id,credito_id,cuota_id,tipo,estado,saldo,dias_atraso)
                VALUES(%s,%s,%s,'CUOTA_VENCIDA',%s,%s,%s) ON CONFLICT(cuota_id) DO UPDATE SET
                estado=EXCLUDED.estado,saldo=EXCLUDED.saldo,dias_atraso=EXCLUDED.dias_atraso,
                version=alertas_credito_demo.version+1,actualizada=CURRENT_TIMESTAMP''',
                (alerta_id, row['id'], ident, estado, cuota['saldo'], cuota['dias_atraso']))
            self._evento(conn, uuid4(), row['id'], 'alerta_recalculada',
                         {'alerta_id': str(alerta_id), 'estado': estado, 'saldo': cuota['saldo'], 'dias_atraso': cuota['dias_atraso']}, user)
        conn.execute('UPDATE creditos_demo SET alertas_revisadas=%s WHERE id=%s', (hoy_utc(), row['id']))

    def crear(self, payload, user):
        datos = payload.model_dump(mode='json')
        with conectar() as conn:
            # Orden fijo por evaluación; evita dos planes simultáneos para la misma captura.
            if not conn.execute('SELECT id FROM evaluaciones WHERE id=%s FOR UPDATE', (payload.evaluacion_id,)).fetchone():
                raise HTTPException(404, 'La evaluación guardada no existe.')
            old = conn.execute('SELECT * FROM creditos_demo WHERE id=%s OR evaluacion_id=%s', (payload.id, payload.evaluacion_id)).fetchone()
            if old:
                if old['id'] != payload.id or not self._repetido(conn, payload.id, payload.id, 'credito_creado', datos, user):
                    raise HTTPException(409, 'Esta evaluación o clave ya tiene un plan de crédito. No se duplicó.')
                return self._detalle(conn, self._credito(conn, payload.id, True))
            conn.execute('INSERT INTO creditos_demo(id,evaluacion_id,concepto,fecha_apertura,monto_total_pactado,plan) VALUES(%s,%s,%s,%s,%s,%s)',
                         (payload.id, payload.evaluacion_id, payload.concepto, payload.fecha_apertura, payload.monto_total_pactado, Jsonb(datos)))
            for n, cuota in enumerate(payload.cuotas):
                conn.execute('INSERT INTO cuotas_demo(id,credito_id,vencimiento,importe) VALUES(%s,%s,%s,%s)',
                             (uuid5(payload.id, str(n)), payload.id, cuota.vencimiento, cuota.importe))
            self._evento(conn, payload.id, payload.id, 'credito_creado', datos, user)
            row = self._credito(conn, payload.id)
            self._alertas(conn, row, user)
            return self._detalle(conn, self._credito(conn, payload.id))

    def pagar(self, ident, payload, user):
        datos = payload.model_dump(mode='json')
        with conectar() as conn:
            row = self._credito(conn, ident, True)
            if self._repetido(conn, payload.id, ident, 'pago_registrado', datos, user):
                return self._detalle(conn, row)
            cuota = conn.execute('SELECT * FROM cuotas_demo WHERE id=%s AND credito_id=%s', (payload.cuota_id, ident)).fetchone()
            if not cuota:
                raise HTTPException(404, 'Cuota no encontrada en este crédito.')
            if payload.fecha_pago < row['fecha_apertura']:
                raise HTTPException(422, 'El pago no puede ser anterior a la apertura.')
            saldo = cuota['importe'] - conn.execute('SELECT coalesce(sum(importe),0) AS n FROM pagos_demo WHERE cuota_id=%s', (payload.cuota_id,)).fetchone()['n']
            if payload.importe > saldo:
                raise HTTPException(409, 'El pago supera el saldo pendiente de la cuota. Actualiza el detalle.')
            if conn.execute('SELECT count(*) AS n FROM pagos_demo WHERE credito_id=%s', (ident,)).fetchone()['n'] >= 500:
                raise HTTPException(409, 'Se alcanzó el límite de 500 movimientos por crédito de la demo.')
            conn.execute('INSERT INTO pagos_demo(id,credito_id,cuota_id,fecha_pago,importe) VALUES(%s,%s,%s,%s,%s)',
                         (payload.id, ident, payload.cuota_id, payload.fecha_pago, payload.importe))
            self._evento(conn, payload.id, ident, 'pago_registrado', datos, user)
            self._alertas(conn, row, user)
            return self._detalle(conn, self._credito(conn, ident))

    def listar(self, limite, offset):
        with conectar() as conn:
            rows = conn.execute('SELECT * FROM creditos_demo ORDER BY creado DESC,id DESC LIMIT %s OFFSET %s', (limite+1, offset)).fetchall()
            return {'items': [{'id': str(r['id']), 'evaluacion_id': str(r['evaluacion_id']), 'concepto': r['concepto'],
                               'monto_total_pactado': importe(r['monto_total_pactado']), 'fecha_apertura': r['fecha_apertura']} for r in rows[:limite]],
                    'hay_mas': len(rows)>limite, 'limite': limite, 'offset': offset}

    def obtener(self, ident):
        with conectar() as conn:
            # Snapshot consistente entre cuotas, pagos y alertas durante una lectura.
            conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            return self._detalle(conn, self._credito(conn, ident))

    def actualizar_alertas(self, ident, user):
        with conectar() as conn:
            row = self._credito(conn, ident, True)
            self._alertas(conn, row, user)
            return self._detalle(conn, self._credito(conn, ident))

    def atender(self, ident, payload, user):
        datos = {'alerta_id': str(ident), **payload.model_dump(mode='json')}
        with conectar() as conn:
            alert = conn.execute('SELECT credito_id FROM alertas_credito_demo WHERE id=%s', (ident,)).fetchone()
            if not alert:
                raise HTTPException(404, 'Alerta no encontrada.')
            row = self._credito(conn, alert['credito_id'], True)
            if self._repetido(conn, payload.id, row['id'], 'alerta_atendida', datos, user):
                return self._detalle(conn, row)
            alert = conn.execute('SELECT * FROM alertas_credito_demo WHERE id=%s', (ident,)).fetchone()
            if alert['version'] != payload.version_anterior or alert['estado'] == 'Resuelta':
                raise HTTPException(409, 'La alerta cambió o ya fue resuelta. Actualiza el detalle.')
            conn.execute("UPDATE alertas_credito_demo SET estado='Atendida',observaciones=%s,version=version+1,actualizada=CURRENT_TIMESTAMP WHERE id=%s",
                         (payload.observaciones, ident))
            self._evento(conn, payload.id, row['id'], 'alerta_atendida', datos, user)
            return self._detalle(conn, self._credito(conn, row['id']))

    def auditoria(self, limite, offset):
        with conectar() as conn:
            rows = conn.execute('SELECT id,credito_id,accion,responsable,fecha FROM eventos_seguimiento_demo ORDER BY fecha DESC,id DESC LIMIT %s OFFSET %s', (limite+1, offset)).fetchall()
            return {'items': rows[:limite], 'hay_mas': len(rows)>limite, 'limite': limite, 'offset': offset}


def obtener_seguimiento():
    return RepositorioSeguimiento() if database_url() else None
