// Una promesa por evaluación durante la sesión de la pantalla, incluso si falla.
// No se llama desde el render ni se persiste información en el navegador.
export function crearGeneradorExplicaciones(solicitar) {
  const intentos = new Map()
  return identificador => {
    if (!identificador) return Promise.reject(new Error('Falta la evaluación guardada.'))
    if (!intentos.has(identificador)) {
      intentos.set(identificador, Promise.resolve().then(() => solicitar(identificador)))
    }
    return intentos.get(identificador)
  }
}
