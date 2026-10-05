const riesgoClasses = { Bajo: 'risk-low', Medio: 'risk-medium', Alto: 'risk-high' }
const pesos = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })

export default function TablaHistorial({ items, selected, onSelected }) {
  return <div className="history-scroll"><table>
    <caption className="sr-history">Evaluaciones guardadas en PostgreSQL</caption>
    <thead><tr><th>Fecha</th><th>Solicitante</th><th>Margen disponible</th><th>Riesgo</th><th>Revisión</th></tr></thead>
    <tbody>{items.map(item => <tr key={item.id}>
      <td>{new Date(item.fecha).toLocaleString('es-MX')}</td><td>{item.rfc}</td>
      <td>{pesos.format(item.margen_libre)}</td>
      <td><span className={`risk-pill ${riesgoClasses[item.nivel_riesgo_preliminar] || ''}`}>{item.nivel_riesgo_preliminar}</span></td>
      <td><button type="button" disabled={!!selected} onClick={() => onSelected(item.id)}>Ver detalle</button></td>
    </tr>)}</tbody>
  </table></div>
}
