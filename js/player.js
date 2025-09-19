import {
  state,
  setVideoActual,
  setListaVideos,
  indiceActual,
  setCanalActual,
  setFecha,
  setVideoActualDesdeNombre,
  limpiarTranscripciones,
  guardarTranscripcion,
  obtenerTranscripcion,
} from "./state.js";
import {
  obtenerListaVideos,
  concatenarYDescargar,
  descargarArchivoSinRecarga,
  obtenerUrlDescarga,
  obtenerTranscripcionClip,
} from "./api.js";
import { mostrarCargando, mostrarPopup, extraerInfoVideo } from "./utils.js";
import {
  getRefs,
  mostrarControles,
  renderTranscripcionSeleccionadaVideo,
  actualizarContador,
  scrollToPlayer,
  actualizarEstadoDescarga,
  deshabilitarBotonDescarga,
  setTituloPlayer,
  renderClipsRelacionados,
} from "./ui.js";

const MAX_ADICIONALES = 3;

function toggleClipAdyacente(offset, agregar) {
  const lado = offset < 0 ? "atras" : "adelante";
  expandir(agregar ? 1 : -1, lado);
}

function configurarReproductor(nombreArchivo) {
  const { videoElement, videoSrc } = getRefs();
  if (!videoElement || !videoSrc) return;

  videoSrc.src = `./canales/${state.canalActual}/${nombreArchivo}`;
  videoElement.load();

  videoElement.onloadedmetadata = () => {
    videoElement.currentTime = 0;
    videoElement.play().catch(() => {
      // El autoplay puede bloquearse; lo ignoramos.
    });
  };

  setTituloPlayer(nombreArchivo);
}

function actualizarClipsRelacionados() {
  renderClipsRelacionados(state.listaVideos, state.videoActual, seleccionarClipRelacionado, toggleClipAdyacente);
}

async function seleccionarClipRelacionado(nombreArchivo) {
  if (!nombreArchivo || nombreArchivo === state.videoActual) return;

  const infoClip = extraerInfoVideo(nombreArchivo);
  const canal = infoClip.canal && infoClip.canal !== "Desconocido" ? infoClip.canal : state.canalActual;
  const timestampInicio = infoClip.timestamp;
  const timestampFin = infoClip.timestampFin;

  if (!canal || !timestampInicio || !timestampFin) {
    mostrarPopup("No se pudo interpretar el clip seleccionado");
    return;
  }

  mostrarCargando(true);
  try {
    const videos = await obtenerListaVideos(canal, timestampInicio, timestampFin);
    if (!Array.isArray(videos) || !videos.length) {
      mostrarPopup("No se encontraron videos para ese intervalo");
      return;
    }

    const listaOrdenada = videos.includes(nombreArchivo) ? [...videos] : [...videos, nombreArchivo];
    listaOrdenada.sort();

    setCanalActual(canal);
    setVideoActualDesdeNombre(nombreArchivo);
    setFecha(timestampInicio);
    setListaVideos(listaOrdenada);

    configurarReproductor(nombreArchivo);

    let transcripcion = obtenerTranscripcion(nombreArchivo);
    if (!transcripcion) {
      try {
        transcripcion = await obtenerTranscripcionClip(canal, timestampInicio, timestampFin);
        if (transcripcion) {
          guardarTranscripcion(nombreArchivo, transcripcion);
        }
      } catch (error) {
        console.error("No se pudo obtener la transcripcion del clip", error);
      }
    }

    const datosTranscripcion = transcripcion || {
      texto: `Clip seleccionado: ${infoClip.nombreCorto}`,
      start_timestamp: timestampInicio,
      end_timestamp: timestampFin,
      canal,
    };

    renderTranscripcionSeleccionadaVideo(datosTranscripcion);
    actualizarClipsRelacionados();
    actualizarContador();
    mostrarPopup("Clip central actualizado");
  } catch (error) {
    console.error("Error al actualizar clip", error);
    mostrarPopup("No se pudo actualizar el clip seleccionado");
  } finally {
    mostrarCargando(false);
  }
}

export async function mostrarVideo(transcripcionResultado) {
  if (!transcripcionResultado) return;

  const canal = transcripcionResultado.canal;
  const timestampStart = transcripcionResultado.start_timestamp;
  const timestampEnd = transcripcionResultado.end_timestamp;

  try {
    mostrarCargando(true);
    limpiarTranscripciones();

    const videos = await obtenerListaVideos(canal, timestampStart, timestampEnd);
    if (!Array.isArray(videos) || !videos.length) {
      mostrarPopup("No se encontraron videos relacionados");
      return;
    }

    setCanalActual(canal);
    setVideoActual(canal, timestampStart, timestampEnd);
    setFecha(timestampStart);
    setListaVideos(videos);

    if (!state.listaVideos.includes(state.videoActual)) {
      console.error(`Video ${state.videoActual} no existe en servidor`);
      mostrarPopup("El video no existe en el servidor");
      return;
    }

    guardarTranscripcion(state.videoActual, transcripcionResultado);

    const resultadosDiv = document.getElementById("resultados");
    if (resultadosDiv) resultadosDiv.innerHTML = "";

    configurarReproductor(state.videoActual);
    renderTranscripcionSeleccionadaVideo(transcripcionResultado);
    actualizarClipsRelacionados();
    actualizarContador();
    mostrarControles();
    scrollToPlayer();
  } catch (error) {
    console.error("Error al cargar video", error);
    mostrarPopup("No se pudo cargar el clip");
  } finally {
    mostrarCargando(false);
  }
}

export function ajustarClip(segundos) {
  const { videoElement } = getRefs();
  if (!videoElement) return;
  videoElement.currentTime += segundos;
}

export function expandir(direccion, lado) {
  const idx = indiceActual();
  if (idx === -1) {
    mostrarPopup("Error: video no encontrado");
    return;
  }

  const esAtras = lado === "atras";
  const disponiblesAtras = idx;
  const disponiblesAdelante = state.listaVideos.length - idx - 1;

  if (direccion === 1) {
    const seleccionados = esAtras ? state.acumuladosAtras : state.acumuladosAdelante;
    const maximoPosible = Math.min(MAX_ADICIONALES, esAtras ? disponiblesAtras : disponiblesAdelante);

    if (seleccionados < maximoPosible) {
      if (esAtras) state.acumuladosAtras++;
      else state.acumuladosAdelante++;
      mostrarPopup(`Se agrego un video ${lado}`);
    } else if (seleccionados >= MAX_ADICIONALES) {
      mostrarPopup(`Maximo ${MAX_ADICIONALES} videos ${lado}`);
    } else {
      mostrarPopup(`No hay mas videos ${lado}`);
    }
  } else {
    const haySeleccionados = esAtras ? state.acumuladosAtras > 0 : state.acumuladosAdelante > 0;
    if (haySeleccionados) {
      if (esAtras) state.acumuladosAtras--;
      else state.acumuladosAdelante--;
      mostrarPopup(`Se quito un video ${lado}`);
    } else {
      mostrarPopup(`No hay mas videos ${lado}`);
    }
  }

  actualizarContador();
  actualizarClipsRelacionados();
}

export async function descargarConcatenado() {
  if (!state.videoActual) {
    mostrarPopup("No hay video seleccionado");
    return;
  }

  const idx = indiceActual();
  if (idx === -1) {
    mostrarPopup("Video no encontrado en la lista");
    return;
  }

  const inicio = Math.max(0, idx - state.acumuladosAtras);
  const fin = Math.min(state.listaVideos.length - 1, idx + state.acumuladosAdelante);
  const seleccion = state.listaVideos.slice(inicio, fin + 1);

  if (seleccion.length === 0) {
    mostrarPopup("No hay videos para concatenar");
    return;
  }

  mostrarCargando(true);
  actualizarEstadoDescarga("Concatenando videos...", "normal");
  deshabilitarBotonDescarga(true, "Procesando...");
  mostrarPopup(`Procesando ${seleccion.length} videos...`);

  const btn = document.getElementById("btnDescargar");
  const textoOriginal = btn ? btn.textContent : "Descargar";
  let descargaExitosa = false;

  try {
    const nombreArchivo = await concatenarYDescargar(seleccion, state.canalActual);

    actualizarEstadoDescarga("Descargando archivo...", "normal");
    const urlDescarga = `${obtenerUrlDescarga(nombreArchivo)}&ts=${Date.now()}`;
    descargarArchivoSinRecarga(urlDescarga, nombreArchivo);

    mostrarPopup("Descarga iniciada");
    actualizarEstadoDescarga("Descarga completada", "success");
    descargaExitosa = true;
    setTimeout(() => {
      const ds = document.getElementById("download-status");
      if (ds) ds.style.display = "none";
    }, 5000);
  } catch (e) {
    const mensajeError = e instanceof Error ? e.message : "Error en la descarga";
    mostrarPopup(`Error al generar clip: ${mensajeError}`);
    actualizarEstadoDescarga(mensajeError, "error");
    console.error(e);
  } finally {
    mostrarCargando(false);
    deshabilitarBotonDescarga(false, descargaExitosa ? "Procesado" : textoOriginal);
  }
}

