// Estado centralizado de la app
import { formatTs } from './utils.js';

export const state = {
  listaVideos: [],          // nombres de archivos en /videos
  videoActual: null,        // nombre de archivo seleccionado
  canalActual: null,        // canal del video seleccionado
  fecha: null,              // fecha del video seleccionado
  acumuladosAtras: 0,
  acumuladosAdelante: 0,
  transcripcionesPorVideo: new Map(),
};

// Helpers
export function resetSeleccion() {
  state.acumuladosAtras = 0;
  state.acumuladosAdelante = 0;
}


export function limpiarTranscripciones() {
  state.transcripcionesPorVideo.clear();
}

export function guardarTranscripcion(nombreArchivo, data) {
  if (!nombreArchivo || !data) return;
  state.transcripcionesPorVideo.set(nombreArchivo, data);
}

export function obtenerTranscripcion(nombreArchivo) {
  if (!nombreArchivo) return null;
  return state.transcripcionesPorVideo.get(nombreArchivo) || null;
}

export function setVideoActual(canal, timestamp) {
  const stTm = formatearTimestamp(timestamp);
  const nombreArchivo = `${canal}_${stTm}.ts`;
  console.log("Seteando video actual a:", nombreArchivo);
  state.videoActual = nombreArchivo;
  resetSeleccion();
}

export function setVideoActualDesdeNombre(nombreArchivo) {
  if (!nombreArchivo) return;
  state.videoActual = nombreArchivo;
  resetSeleccion();
}

export function setCanalActual(canal) {
  state.canalActual = canal;
  resetSeleccion();
}

export function setListaVideos(lista) {
  state.listaVideos = Array.isArray(lista) ? lista : [];
  resetSeleccion();
}

export function setFecha(ts) {
  state.fecha = formatTs(ts);
  resetSeleccion();
}

export function indiceActual() {
  return state.listaVideos.indexOf(state.videoActual);
}

function formatearTimestamp(ts) {
  if (typeof ts !== "string") return "";
  const limpio = ts.replace('Z', '');
  const [fecha, hora] = limpio.split('T');
  if (!fecha || !hora) return limpio;
  const fechaSinGuiones = fecha.replace(/-/g, '');
  const horaSinPuntos = hora.replace(/:/g, '');
  return `${fechaSinGuiones}_${horaSinPuntos}`;
}

// Ejemplo simple para validar formato
const ejemploTs = "2025-09-12T12:07:30Z";
console.log(formatearTimestamp(ejemploTs)); // "20250912_120730"
