-- Solo se ejecuta al crear el volumen por primera vez.
\getenv app_password PLURI_APP_PASSWORD
CREATE ROLE pluri_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'app_password';
ALTER DATABASE pluri_credito OWNER TO pluri_app;
\connect pluri_credito
GRANT USAGE, CREATE ON SCHEMA public TO pluri_app;
