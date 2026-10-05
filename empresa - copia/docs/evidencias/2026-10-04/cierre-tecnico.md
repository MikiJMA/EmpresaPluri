# Cierre técnico local — NexoCredit

Seguimiento del 04/10/2026 (fecha de México), posterior a la prueba integral y al cambio de marca. No es aceptación del asesor ni habilitación para producción. Las comprobaciones anteriores conservan sus fechas y muestras.

| Comprobación realizada | Resultado | Límite |
|---|---|---|
| Backend y PostgreSQL temporal | 69 pruebas aprobadas, 0 omitidas; incluye 5 pruebas PostgreSQL reales | Base temporal sin puertos ni datos de trabajo; proveedores externos simulados |
| Frontend | 48 pruebas aprobadas, 0 omitidas; ESLint y Vite aprobados | No sustituye revisión visual ni aceptación de usuarios |
| Lanzadores PowerShell | docker-url, banxico-config y programacion-aislada aprobados | Mocks sin credenciales ni cambios a servicios |
| Dependencias frontend en imagen limpia | npm audit: 0 vulnerabilidades reportadas en esa comprobación; brace-expansion 5.0.12 | Resultado fechado, no garantía permanente |
| Respaldo y restauración PostgreSQL | 3 tablas conciliadas: filas, huellas, columnas, restricciones y vistas | Restauración en contenedor aislado; no se sobrescribió la base original |
| Metadatos Azure ML, lectura autenticada en Studio | Endpoint y despliegue Correcto; modelo registrado servido plurione-uci-voting-candidato:1; tráfico directo 100 % | No se comparó el binario remoto con el artefacto local ni se acreditó aptitud crediticia |
| Marca y pantalla real | NexoCredit en login, navegación, favicon y mensajes; 2 guías / 14 secciones; total de 7 evaluaciones conservado | Las dos guías demo se adaptan solo en presentación; originales Search e identificadores técnicos sin cambios |

Se aplicaron únicamente las imágenes frontend y backend; PostgreSQL conservó su contenedor, volumen y registros. No se añadieron evaluaciones para comprobar la nueva marca ni se crearon recursos cloud. La consulta del laboratorio ML sigue separada de las reglas del formulario principal.

El ensayo manual utilizó un respaldo privado generado el 04/10/2026. Dump, manifiesto, logs y capturas se conservan bajo `.local/` o como evidencias locales excluidas de Git. El respaldo no está cifrado y no incluye roles globales ni ACL; no acredita recuperación productiva completa, retención automática ni un objetivo de recuperación acordado.

Comandos desde la raíz interior, con Docker Desktop activo e imágenes construidas:

- `Probar programacion.cmd`: suites completas con PostgreSQL efímero aislado; no usar la base de trabajo para estas pruebas.
- `Respaldar PostgreSQL.cmd`: respaldo manual privado de la base Docker de demostración.
- `Probar restauracion PostgreSQL.cmd`: crea un respaldo nuevo y verifica su restauración en un contenedor temporal, nunca en la base original. Para ensayar uno existente: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\respaldo-postgresql.ps1 -Accion probar -Respaldo '<carpeta privada del respaldo>'`.

Seguimiento posterior: [publicación y CI remota del commit de código](github-actions.md), ambos trabajos aprobados con conteos 69/48. Pasar estas pruebas no completa Scrum, capacitación, aceptación, validación crediticia ni operación de producción.
