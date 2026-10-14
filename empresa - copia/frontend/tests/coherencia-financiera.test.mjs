import test from 'node:test'
import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { erroresFinancieros } from '../src/evaluacion_crediticia/servicios/coherenciaFinanciera.mjs'

const { default: Form } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/EvaluationForm.jsx',import.meta.url))
const form={rfc:'DEMO',ingresos_mensuales:'30000',gastos_mensuales:'10000',score_buro_actual:'700',deuda_actual:'50000',pagos_mensuales_creditos:'2500',dias_atraso_actual:'0'}

test('no interpreta campos vacíos como cero ni inventa inconsistencias',()=>{
  for(const value of ['', '  ', undefined, null]) assert.deepEqual(erroresFinancieros({gastos_mensuales:value,deuda_actual:value,pagos_mensuales_creditos:value,dias_atraso_actual:value}),[])
  assert.deepEqual(erroresFinancieros(form),[])
  assert.deepEqual(erroresFinancieros({...form,pagos_mensuales_creditos:'10000'}),[])
  assert.deepEqual(erroresFinancieros({...form,deuda_actual:'0',dias_atraso_actual:'0'}),[])
})

test('pagos incluidos en gastos y atraso pendiente con deuda cero se señalan sin recalificar riesgo',()=>{
  assert.match(erroresFinancieros({...form,gastos_mensuales:'100'})[0],/deben incluirlos/)
  assert.match(erroresFinancieros({...form,deuda_actual:'0',dias_atraso_actual:'30'})[0],/mayor que cero/)
  assert.equal(erroresFinancieros({...form,gastos_mensuales:'100',deuda_actual:'0',dias_atraso_actual:'30'}).length,2)
})

test('formulario muestra motivos accesibles y no envía una captura contradictoria',()=>{
  let llamadas=0
  const props={form:{...form,gastos_mensuales:'100'},busy:false,change:()=>{},submit:()=>{llamadas++}}
  const html=renderToStaticMarkup(createElement(Form,props))
  assert.match(html,/id="financial-errors" role="alert"/)
  assert.match(html,/<button type="submit" disabled="" aria-describedby="financial-errors"/)
  const tree=Form(props)
  const formulario=tree.props.children.find(child=>child?.type==='form')
  let cancelado=false
  formulario.props.onSubmit({preventDefault:()=>{cancelado=true}})
  assert.equal(cancelado,true)
  assert.equal(llamadas,0)
  const valid=Form({...props,form})
  valid.props.children.find(child=>child?.type==='form').props.onSubmit({preventDefault:()=>{}})
  assert.equal(llamadas,1)
})
