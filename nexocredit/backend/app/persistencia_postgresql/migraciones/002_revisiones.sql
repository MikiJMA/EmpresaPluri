CREATE TABLE revisiones (
 id UUID PRIMARY KEY,
 evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id),
 version INTEGER NOT NULL CHECK (version > 0),
 estado TEXT NOT NULL CHECK (estado IN ('Pendiente', 'Aprobada', 'Rechazada')),
 observaciones TEXT NOT NULL CHECK (length(trim(observaciones)) BETWEEN 1 AND 2000),
 responsable TEXT NOT NULL CHECK (length(trim(responsable)) BETWEEN 1 AND 120),
 fecha TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(evaluacion_id, version)
);
