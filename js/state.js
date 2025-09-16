// Estado centralizado de la app
export const state = {
  listaVideos: [],          // nombres de archivos en /videos
  videoActual: null,        // nombre de archivo seleccionado
  acumuladosAtras: 0,
  acumuladosAdelante: 0,
};

// Helpers
export function resetSeleccion() {
  state.acumuladosAtras = 0;
  state.acumuladosAdelante = 0;
}

export function setVideoActual(nombre) {
  state.videoActual = nombre;
  resetSeleccion();
}

export function setListaVideos(lista) {
  state.listaVideos = lista;
  resetSeleccion();
}

export function indiceActual() {
  return state.listaVideos.indexOf(state.videoActual);
}
