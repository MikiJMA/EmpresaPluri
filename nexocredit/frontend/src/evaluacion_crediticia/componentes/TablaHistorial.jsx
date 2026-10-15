import { esFilaHistorial } from '../servicios/contratos.mjs'
import { formatearPesos } from '../../interfaz/moneda.mjs'
const riesgoClasses = { Bajo: 'risk-low', Medio: 'risk-medium', Alto: 'risk-high' }

export default function TablaHistorial({ items, selected, onSelected }) {
  if (!Array.isArray(items) || !items.every(esFilaHistorial)) return <p role="alert" className="error">El historial contiene datos de formato inválido. Actualiza para volver a consultarlo.</p>
  return <div className="history-scroll"><table>
    <caption className="sr-history">Evaluaciones guardadas en PostgreSQL</caption>
    <thead><tr><th>Fecha</th><th>Solicitante</th><th>Margen disponible</th><th>Riesgo</th><th>Revisión</th></tr></thead>
    <tbody>{items.map(item => <tr key={item.id}>
      <td>{new Date(item.fecha).toLocaleString('es-MX')}</td><td>{item.rfc}</td>
      <td title={formatearPesos(item.margen_libre, { decimales: 2 })}>{formatearPesos(item.margen_libre)}</td>
      <td><span className={`risk-pill ${riesgoClasses[item.nivel_riesgo_preliminar] || ''}`}>{item.nivel_riesgo_preliminar}</span></td>
      <td><button type="button" disabled={!!selected} onClick={() => onSelected(item.id)}>Ver detalle</button></td>
    </tr>)}</tbody>
  </table><p className="form-footnote">Importes redondeados a pesos. Ver detalle conserva los centavos y la versión original de reglas.</p></div>
}
