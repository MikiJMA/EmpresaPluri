-- Ampliación aditiva: no altera ni rellena registros históricos.
CREATE TABLE creditos_demo (
 id UUID PRIMARY KEY,
 evaluacion_id UUID NOT NULL UNIQUE REFERENCES evaluaciones(id),
 concepto TEXT NOT NULL CHECK (length(concepto) BETWEEN 1 AND 100),
 fecha_apertura DATE NOT NULL,
 monto_total_pactado NUMERIC(12,2) NOT NULL CHECK (monto_total_pactado > 0 AND monto_total_pactado <= 1000000000),
 plan JSONB NOT NULL CHECK (jsonb_typeof(plan)='object'),
 creado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 alertas_revisadas DATE
);
CREATE TABLE cuotas_demo (
 id UUID PRIMARY KEY,
 credito_id UUID NOT NULL REFERENCES creditos_demo(id),
 vencimiento DATE NOT NULL,
 importe NUMERIC(12,2) NOT NULL CHECK (importe > 0 AND importe <= 1000000000),
 UNIQUE(credito_id,vencimiento), UNIQUE(id,credito_id)
);
CREATE TABLE pagos_demo (
 id UUID PRIMARY KEY,
 credito_id UUID NOT NULL REFERENCES creditos_demo(id),
 cuota_id UUID NOT NULL,
 fecha_pago DATE NOT NULL,
 importe NUMERIC(12,2) NOT NULL CHECK (importe > 0 AND importe <= 1000000000),
 registrado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(cuota_id,credito_id) REFERENCES cuotas_demo(id,credito_id)
);
CREATE INDEX pagos_demo_credito_idx ON pagos_demo(credito_id,fecha_pago,id);
CREATE TABLE alertas_credito_demo (
 id UUID PRIMARY KEY,
 credito_id UUID NOT NULL REFERENCES creditos_demo(id),
 cuota_id UUID NOT NULL UNIQUE REFERENCES cuotas_demo(id),
 tipo TEXT NOT NULL CHECK (tipo='CUOTA_VENCIDA'),
 estado TEXT NOT NULL CHECK (estado IN ('Pendiente','Atendida','Resuelta')),
 saldo NUMERIC(12,2) NOT NULL CHECK(saldo >= 0),
 dias_atraso INTEGER NOT NULL CHECK(dias_atraso >= 0),
 version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
 observaciones TEXT NOT NULL DEFAULT '',
 detectada TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 actualizada TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE eventos_seguimiento_demo (
 id UUID PRIMARY KEY,
 credito_id UUID NOT NULL REFERENCES creditos_demo(id),
 accion TEXT NOT NULL,
 actor_hash CHAR(64) NOT NULL,
 responsable TEXT NOT NULL,
 datos JSONB NOT NULL CHECK(jsonb_typeof(datos)='object'),
 fecha TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX eventos_seguimiento_credito_idx ON eventos_seguimiento_demo(credito_id,fecha,id);
REVOKE ALL ON creditos_demo,cuotas_demo,pagos_demo,alertas_credito_demo,eventos_seguimiento_demo FROM PUBLIC;
