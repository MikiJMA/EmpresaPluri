export const SECCIONES = [
  ['seguimiento', 'Resumen', 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'],
  ['evaluacion', 'Evaluaciones', 'M4 20V10M12 20V4M20 20v-7'],
  ['historial', 'Historial', 'M6 3h9l4 4v14H6zM9 12h6M9 16h6'],
  ['creditos', 'Créditos y pagos', 'M3 5h18v14H3zM3 9h18M7 14h4'],
  ['laboratorio', 'Laboratorio IA', 'M9 3h6M10 3v6L4 19v2h16v-2L14 9V3M8 15h8'],
  ['indicadores', 'Indicadores financieros', 'M3 17l6-6 4 4 8-10M16 5h5v5M3 21h18'],
  ['documentos', 'Documentos', 'M4 5h6l2 2h8v14H4zM8 12h8M8 16h5'],
]

export function seccionDesdeHash(hash) {
  return SECCIONES.find(([id]) => hash === `#${id}`)?.[0] || null
}
