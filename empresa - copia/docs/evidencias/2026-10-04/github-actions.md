# GitHub Actions — cierre NexoCredit

Ejecución real de la rama `codex/cierre-nexocredit-demo`, disparada manualmente tras publicar el código. Fecha de México: 04/10/2026; finalización backend: 05/10/2026 00:22:11 UTC. No se modificó `main`, no se desplegó la aplicación ni se crearon servicios Azure.

- Commit de código verificado: `19223ae469c91724e9e34c30fe558fc0991aea99`.
- Workflow: `Validacion NexoCredit`, `.github/workflows/ci.yml` en la raíz Git exterior.
- [Ejecución 37247212787](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247212787): `completed / success`, ambos trabajos aprobados.

| Trabajo | Comprobaciones reales en GitHub | Resultado |
|---|---|---|
| [Backend](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247212787/job/111567348085) | Python 3.12, PostgreSQL 17 efímero, migraciones ejecutadas dos veces, unittest, tres archivos de pruebas de lanzadores PowerShell | 69 pruebas, 0 omitidas; migraciones y lanzadores aprobados |
| [Frontend](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247212787/job/111567348189) | Node 24, npm ci desde lockfile, npm audit, unitarios, ESLint y Vite | 48 aprobadas, 0 fallidas/omitidas/canceladas; audit reportó 0 vulnerabilidades; lint y build aprobados |

Conteos comprobados en los logs de los trabajos, no inferidos de pruebas locales. Los proveedores externos están simulados en CI; no se copiaron claves de producción ni se consultó Azure. Esta ejecución prueba el commit indicado, no futuros cambios. La incorporación posterior de este registro constituye un commit documental distinto.

Los `.env`, `.local`, dumps, capturas de evidencia sin depurar, PBIX, caché y preferencias locales de Power BI, y el pickle sin uso en el backend están excluidos del nuevo árbol. Los cuatro archivos Power BI retirados del seguimiento siguen en disco. Retirar seguimiento no borra archivos presentes en commits anteriores; no se reescribió el historial del repositorio público.

C02 del backlog queda cerrado técnicamente para esta versión demo. Scrum, capacitación, aceptación, comparación binaria del modelo y controles productivos continúan con los límites registrados en [backlog](../../../gestion_proyecto/scrum/BACKLOG_CIERRE.md).
