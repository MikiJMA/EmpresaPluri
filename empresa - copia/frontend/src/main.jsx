import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import App from './App.jsx'
import Acceso from './autenticacion/Acceso.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode><Acceso><App /></Acceso></StrictMode>,
)
