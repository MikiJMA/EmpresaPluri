CREATE SCHEMA IF NOT EXISTS reportes;
CREATE OR REPLACE VIEW reportes.evaluaciones_powerbi AS
SELECT e.id AS evaluacion_id,
       e.fecha AT TIME ZONE 'UTC' AS fecha_utc,
       (e.solicitud->>'ingresos_mensuales')::numeric AS ingresos_mensuales,
       (e.solicitud->>'gastos_mensuales')::numeric AS gastos_mensuales,
       (e.solicitud->>'deuda_actual')::numeric AS deuda_actual,
       (e.solicitud->>'pagos_mensuales_creditos')::numeric AS pagos_mensuales_creditos,
       (e.solicitud->>'dias_atraso_actual')::integer AS dias_atraso_actual,
       (e.solicitud->>'score_buro_actual')::integer AS score_capturado,
       (e.resultado->>'margen_libre')::numeric AS margen_libre,
       e.resultado->>'nivel_riesgo_preliminar' AS riesgo_demo,
       e.resultado->>'version_modelo' AS version_modelo,
       coalesce(r.estado, 'Pendiente') AS estado_revision
FROM public.evaluaciones e
LEFT JOIN LATERAL (
    SELECT estado FROM public.revisiones WHERE evaluacion_id = e.id ORDER BY version DESC LIMIT 1
) r ON true;
REVOKE ALL ON SCHEMA reportes FROM PUBLIC;
REVOKE ALL ON reportes.evaluaciones_powerbi FROM PUBLIC;
GRANT CONNECT ON DATABASE pluri_credito TO pluri_powerbi;
GRANT USAGE ON SCHEMA reportes TO pluri_powerbi;
GRANT SELECT ON reportes.evaluaciones_powerbi TO pluri_powerbi;
