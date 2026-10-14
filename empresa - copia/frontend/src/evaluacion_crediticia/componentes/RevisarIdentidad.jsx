import { useEffect, useRef, useState } from 'react'
import { fetchAutenticado } from '../../autenticacion/cliente'
import { crearRevisionIdentidad } from '../servicios/identidad.mjs'
import PanelIdentidad from './PanelIdentidad'

const servicio = crearRevisionIdentidad(fetchAutenticado, import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000')

export default function RevisarIdentidad({ rfc, bloqueado }) {
  const [curp, setCurp] = useState('')
  const [consulta, setConsulta] = useState(null)
  const controller = useRef(null)
  const intento = useRef(0)
  useEffect(() => () => controller.current?.abort(), [])
  const visible = consulta?.rfc === rfc && consulta?.curp === curp ? consulta : null
  async function revisar() {
    controller.current?.abort()
    const solicitud = new AbortController()
    controller.current = solicitud
    const actual = ++intento.current
    setConsulta({ rfc, curp, busy: true })
    try {
      const data = await servicio(rfc, curp, AbortSignal.any([solicitud.signal, AbortSignal.timeout(15000)]))
      if (!solicitud.signal.aborted && intento.current === actual) setConsulta({ rfc, curp, busy: false, data })
    } catch (error) {
      if (!solicitud.signal.aborted && intento.current === actual) setConsulta({ rfc, curp, busy: false, error: error.message })
    }
  }
  function change(event) {
    controller.current?.abort()
    intento.current += 1
    setCurp(event.target.value.toUpperCase())
    setConsulta(null)
  }
  return <PanelIdentidad curp={curp} change={change} revisar={revisar} busy={Boolean(visible?.busy)}
    disabled={bloqueado} puedeRevisar={Boolean(rfc.trim())} data={visible?.data} error={visible?.error} />
}
