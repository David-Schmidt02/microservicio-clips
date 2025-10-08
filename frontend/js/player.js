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
  obtenerUrlVideo,
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

  const videoUrl = obtenerUrlVideo(state.canalActual, nombreArchivo);
  videoSrc.src = videoUrl;
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
    const videos = await obtenerListaVideos(canal, timestampInicio);
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
        const respuestaAPI = await obtenerTranscripcionClip(canal, timestampInicio);
        if (respuestaAPI && respuestaAPI.texto) {
          // Convertir respuesta de API a formato interno esperado
          transcripcion = {
            texto: respuestaAPI.texto,
            timestamp: timestampInicio,
            canal: canal,
          };
          guardarTranscripcion(nombreArchivo, transcripcion);
        }
      } catch (error) {
        console.error("No se pudo obtener la transcripcion del clip", error);
      }
    }

    const datosTranscripcion = transcripcion || {
      texto: `Clip seleccionado: ${infoClip.nombreCorto}`,
      timestamp: timestampInicio,
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
  actualizarClipsRelacionados();
  actualizarContador();
  mostrarControles();
  scrollToPlayer();

  if (!transcripcionResultado) return;

  const canal = transcripcionResultado.canal;
  const timestamp = transcripcionResultado.timestamp;

  try {
    mostrarCargando(true);
    limpiarTranscripciones();

    const videos = await obtenerListaVideos(canal, timestamp);
    if (!Array.isArray(videos) || !videos.length) {
      mostrarPopup("No se encontraron videos relacionados");
      return;
    }

    setCanalActual(canal);
    setFecha(timestamp);
    setListaVideos(videos);
    
    // Buscar el archivo que contiene el timestamp solicitado
    const archivoReferencia = encontrarArchivoConTimestamp(videos, timestamp) || videos[0];
    
    setVideoActualDesdeNombre(archivoReferencia);

    if (!state.listaVideos.includes(state.videoActual)) {
      console.error(`Video ${state.videoActual} no existe en servidor`);
      mostrarPopup("El video no existe en el servidor");
      return;
    }

    // Obtener transcripción concatenada en lugar de usar solo la individual
    let transcripcionFinal = transcripcionResultado;
    try {
      const respuestaAPI = await obtenerTranscripcionClip(canal, timestamp);
      if (respuestaAPI && respuestaAPI.texto) {
        // Usar la transcripción concatenada de la API
        transcripcionFinal = {
          texto: respuestaAPI.texto,
          timestamp: timestamp,
          canal: canal,
        };
      }
    } catch (error) {
      console.error("No se pudo obtener la transcripción concatenada, usando la individual", error);
      // Si hay error, usar la transcripción individual original
      transcripcionFinal = transcripcionResultado;
    }

    guardarTranscripcion(state.videoActual, transcripcionFinal);

    const resultadosDiv = document.getElementById("resultados");
    if (resultadosDiv) resultadosDiv.innerHTML = "";

    configurarReproductor(state.videoActual);
    renderTranscripcionSeleccionadaVideo(transcripcionFinal);
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
    mostrarPopup("Video no encontrado en la lista");
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
    } else if (seleccionados >= maximoPosible && maximoPosible < MAX_ADICIONALES) {
      mostrarPopup(`Maximo ${maximoPosible} videos ${lado}`);
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
  mostrarControles();
  scrollToPlayer();
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

  // Capturar texto original ANTES de modificar el botón
  const btn = document.getElementById("btnDescargar");
  const textoOriginal = btn ? btn.textContent : "Descargar clip concatenado";
  
  mostrarCargando(true);
  actualizarEstadoDescarga("Concatenando videos...", "normal");
  deshabilitarBotonDescarga(true, "Procesando...");
  mostrarPopup(`Procesando ${seleccion.length} videos...`);

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
    if (descargaExitosa) {
      // Mostrar "Procesado" por 3 segundos, luego volver al texto original
      deshabilitarBotonDescarga(false, "Procesado");
      
      // Limpiar timeout previo si existe
      if (window.resetButtonTimeout) {
        clearTimeout(window.resetButtonTimeout);
      }
      
      // Programar reseteo del botón
      window.resetButtonTimeout = setTimeout(() => {
        deshabilitarBotonDescarga(false, textoOriginal);
        window.resetButtonTimeout = null;
      }, 3000);
    } else {
      deshabilitarBotonDescarga(false, textoOriginal);
    }
  }
}

/**
 * Encuentra el archivo que contiene el timestamp especificado
 */
function encontrarArchivoConTimestamp(archivos, timestamp) {
  if (!Array.isArray(archivos) || archivos.length === 0) {
    return null;
  }

  try {
    // Parsear el timestamp objetivo
    const timestampObj = new Date(timestamp);
    
    for (const archivo of archivos) {
      // Extraer información del archivo: canal_fecha_hora_fecha_hora.ts
      const partes = archivo.replace('.ts', '').split('_');
      if (partes.length < 5) {
        continue;
      }
      
      // Construir timestamps de inicio y fin
      const fechaInicio = partes[1]; // YYYYMMDD
      const horaInicio = partes[2];   // HHMMSS
      const fechaFin = partes[3];     // YYYYMMDD
      const horaFin = partes[4];      // HHMMSS
      
      const inicioStr = `${fechaInicio.slice(0,4)}-${fechaInicio.slice(4,6)}-${fechaInicio.slice(6,8)}T${horaInicio.slice(0,2)}:${horaInicio.slice(2,4)}:${horaInicio.slice(4,6)}`;
      const finStr = `${fechaFin.slice(0,4)}-${fechaFin.slice(4,6)}-${fechaFin.slice(6,8)}T${horaFin.slice(0,2)}:${horaFin.slice(2,4)}:${horaFin.slice(4,6)}`;
      
      const inicioObj = new Date(inicioStr);
      const finObj = new Date(finStr);
      
      // Verificar si el timestamp está dentro del rango
      if (timestampObj >= inicioObj && timestampObj <= finObj) {
        console.log("🎯 Archivo seleccionado:", archivo, "para timestamp:", timestamp);
        return archivo;
      }
    }
    
    return null;
    
  } catch (error) {
    console.error("❌ Error buscando archivo:", error);
    return null;
  }
}