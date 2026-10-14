-- Acceso local opcional. No crea usuarios predeterminados ni modifica evaluaciones.
CREATE TABLE usuarios_locales (
 id UUID PRIMARY KEY,
 usuario TEXT NOT NULL UNIQUE CHECK (usuario ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
 nombre TEXT NOT NULL CHECK (length(trim(nombre)) BETWEEN 3 AND 70),
 password_hash TEXT NOT NULL,
 roles TEXT[] NOT NULL CHECK (cardinality(roles) BETWEEN 1 AND 2
                            AND roles <@ ARRAY['Analista', 'Administrador']::TEXT[]),
 activo BOOLEAN NOT NULL DEFAULT TRUE,
 version_sesion INTEGER NOT NULL DEFAULT 1 CHECK (version_sesion > 0),
 intentos_fallidos INTEGER NOT NULL DEFAULT 0 CHECK (intentos_fallidos >= 0),
 inicio_intentos TIMESTAMPTZ,
 bloqueado_hasta TIMESTAMPTZ,
 creado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 actualizado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- HMAC de la IP, no IP en claro. Persistencia compartida entre procesos/reinicios.
CREATE TABLE auth_intentos_locales (
 origen_hash CHAR(64) PRIMARY KEY,
 inicio TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0)
);

REVOKE ALL ON usuarios_locales, auth_intentos_locales FROM PUBLIC;
