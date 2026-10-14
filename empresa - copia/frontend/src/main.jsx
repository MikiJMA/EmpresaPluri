import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import App from './App.jsx'
import Acceso from './autenticacion/Acceso.jsx'
import ErrorRecuperable from './interfaz/ErrorRecuperable.jsx'
import './styles/EsquinasRectas.css'

createRoot(document.getElementById('root')).render(
  <StrictMode><ErrorRecuperable><Acceso><App /></Acceso></ErrorRecuperable></StrictMode>,
)
