import { useEffect, useRef, useState } from 'react'
import { crearControlValoracion, vistaInicialValoracion } from '../servicios/valoracionIA.mjs'
import { servicioValoracion } from '../servicios/valoracionIACliente'
import PanelValoracionIA from './PanelValoracionIA'

export default function ValoracionIASolicitud({ evaluacion, captura, generar }) {
  const [vista, setVista] = useState(vistaInicialValoracion)
  const control = useRef(null)
  useEffect(() => {
    const instancia = crearControlValoracion({ evaluacion, captura, generar, servicio: servicioValoracion, emitir: setVista })
    control.current = instancia
    instancia.iniciar()
    return () => { instancia.cerrar(); if (control.current === instancia) control.current = null }
  }, [evaluacion, captura, generar])
  return <PanelValoracionIA evaluacion={evaluacion} vista={vista} reintentar={() => control.current?.reintentar()} />
}
