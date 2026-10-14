-- Ampliación aditiva: no modifica evaluaciones, revisiones, usuarios ni contraseñas.
ALTER TABLE auth_intentos_locales DROP CONSTRAINT auth_intentos_locales_cantidad_check;
ALTER TABLE auth_intentos_locales ALTER COLUMN cantidad SET DEFAULT 0;
ALTER TABLE auth_intentos_locales ADD CONSTRAINT auth_intentos_locales_cantidad_check CHECK (cantidad >= 0);
ALTER TABLE auth_intentos_locales ADD COLUMN cantidad_total INTEGER NOT NULL DEFAULT 0 CHECK (cantidad_total >= 0);
ALTER TABLE auth_intentos_locales ADD COLUMN inicio_total TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE cache_explicaciones (
 evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id),
 clave CHAR(64) NOT NULL,
 respuesta JSONB,
 error_http INTEGER CHECK (error_http BETWEEN 400 AND 599),
 error_detalle TEXT,
 vence TIMESTAMPTZ NOT NULL,
 PRIMARY KEY(evaluacion_id,clave),
 CHECK ((respuesta IS NOT NULL AND error_http IS NULL AND error_detalle IS NULL)
     OR (respuesta IS NULL AND error_http IS NOT NULL AND error_detalle IS NOT NULL))
);
CREATE TABLE cuotas_explicaciones (
 usuario_hash CHAR(64) PRIMARY KEY,
 inicio TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 cantidad INTEGER NOT NULL CHECK (cantidad > 0)
);
REVOKE ALL ON cache_explicaciones, cuotas_explicaciones FROM PUBLIC;
