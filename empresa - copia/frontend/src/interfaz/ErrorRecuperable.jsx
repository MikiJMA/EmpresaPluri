import { Component } from 'react'

// Última defensa ante errores de render; no registra payloads, JWT ni datos capturados.
export default class ErrorRecuperable extends Component {
  state = { fallo: false }
  static getDerivedStateFromError() { return { fallo: true } }
  render() {
    if (this.state.fallo) return <main className="card" role="alert" style={{ margin: '2rem', padding: '2rem' }}>
      <h1>No se pudo mostrar esta pantalla</h1><p>Recarga para recuperar la aplicación. Los datos ya guardados no se eliminan. Tendrás que volver a iniciar sesión; los campos sin guardar se perderán.</p>
      <button type="button" onClick={() => window.location.reload()}>Recargar aplicación</button>
    </main>
    return this.props.children
  }
}
