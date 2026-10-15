CREATE TABLE evaluaciones (
    id UUID PRIMARY KEY,
    fecha TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    solicitud JSONB NOT NULL,
    resultado JSONB NOT NULL,
    CONSTRAINT solicitud_objeto CHECK (jsonb_typeof(solicitud) = 'object'),
    CONSTRAINT resultado_objeto CHECK (jsonb_typeof(resultado) = 'object')
);
CREATE INDEX evaluaciones_fecha_idx ON evaluaciones (fecha DESC, id DESC);
