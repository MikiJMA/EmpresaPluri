import { useEffect, useRef, useState } from 'react'
import { fetchAutenticado } from '../../autenticacion/cliente'
import { crearServicioSegundaOpinion } from '../servicios/segundaOpinion.mjs'
import { crearControlSegundaOpinion, vistaInicialSegundaOpinion } from '../servicios/controlSegundaOpinion.mjs'
import PanelSegundaOpinion from './PanelSegundaOpinion'

const servicio = crearServicioSegundaOpinion(fetchAutenticado, import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000')

export default function SegundaOpinionModelo({ evaluacion }) {
  const [vista, setVista] = useState(vistaInicialSegundaOpinion)
  const control = useRef(null)
  useEffect(() => {
    const instancia = crearControlSegundaOpinion({ evaluacion, servicio, emitir: setVista })
    control.current = instancia
    instancia.iniciar()
    return () => { instancia.cerrar(); if (control.current === instancia) control.current = null }
  }, [evaluacion])
  return <PanelSegundaOpinion evaluacion={evaluacion} vista={vista}
    cambiar={(name, value) => control.current?.cambiar(name, value)} cargarEjemplo={() => control.current?.cargarEjemplo()}
    consultar={() => control.current?.consultar()} comprobar={() => control.current?.comprobar()} />
}
