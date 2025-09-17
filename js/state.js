// Estado centralizado de la app
export const state = {
  listaVideos: [],          // nombres de archivos en /videos
  videoActual: null,        // nombre de archivo seleccionado
  canalActual: null,       // canal del video seleccionado
  fecha: null,            // fecha del video seleccionado
  acumuladosAtras: 0,
  acumuladosAdelante: 0,
};

// Helpers
export function resetSeleccion() {
  state.acumuladosAtras = 0;
  state.acumuladosAdelante = 0;
}

export function setVideoActual(canal, start_timestamp, end_timestamp) {
  const st_tm = formatearTimestamp(start_timestamp);
  const en_tm = formatearTimestamp(end_timestamp);
  const nombreArchivo = `${canal}_${st_tm}_${en_tm}.ts`;
  console.log("Seteando video actual a:", nombreArchivo);
  state.videoActual = nombreArchivo;
  resetSeleccion();
}

export function setCanalActual(canal) {
  console.log("Seteando canal actual a:", canal);
  state.canalActual = canal;
  resetSeleccion();
}

export function setListaVideos(lista) {
  state.listaVideos = lista;
  resetSeleccion();
}

export function setFecha(ts) {
  const d = new Date(ts);
  const fecha = isNaN(d.getTime()) ? "Desconocida" : d.toLocaleDateString();
  state.fecha = fecha;
  resetSeleccion();
}

export function indiceActual() {
  return state.listaVideos.indexOf(state.videoActual);
}

function formatearTimestamp(ts) {
  ts = ts.replace('Z', '');
  // Divide fecha y hora
  const [fecha, hora] = ts.split('T');
  // Quita los guiones de la fecha
  const fechaSinGuiones = fecha.replace(/-/g, '');
  // Quita los dos puntos de la hora
  const horaSinPuntos = hora.replace(/:/g, '');
  return `${fechaSinGuiones}_${horaSinPuntos}`;
}

// Ejemplo de uso:
const ts = "2025-09-12T12:07:30Z";
console.log(formatearTimestamp(ts)); // "20250912_120730"