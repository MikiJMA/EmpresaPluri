import { fetchAutenticado } from '../../autenticacion/cliente'
import { crearServicioValoracion } from './valoracionIA.mjs'

export const servicioValoracion = crearServicioValoracion(fetchAutenticado, import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000')
