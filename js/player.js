import { state, setVideoActual,setListaVideos , resetSeleccion, indiceActual } from "./state.js";
import { obtenerListaVideos, concatenarVideos } from "./api.js";
import {
  mostrarCargando, mostrarPopup, formatTime,
} from "./utils.js";
import {
  getRefs, mostrarControles, ocultarReproductor, scrollToPlayer,
  renderTranscripcionSeleccionadaVideo, actualizarContador,
  actualizarEstadoDescarga, deshabilitarBotonDescarga, setTituloPlayer
} from "./ui.js";

const MAX_ADICIONALES = 3;

// Carga perezosa de lista de videos ver cómo implementar a futuro
async function ensureVideosCargados() {
  if (state.listaVideos.length) return;
  const vids = await obtenerListaVideos();
  state.listaVideos = vids;
}

// Configurar el reproductor con el video seleccionado
function configurarReproductor(nombreArchivo) {
  const { videoElement, videoSrc } = getRefs();
  videoSrc.src = `./videos/${nombreArchivo}`;
  videoElement.load();

  videoElement.onloadedmetadata = () => {
    videoElement.currentTime = 0;
    videoElement.play().catch(() => {
      // Autoplay bloqueado: no es error grave
    });
  };
  setTituloPlayer(nombreArchivo);
}

// Mostrar un resultado (abrir player + panel derecho)
export async function mostrarVideo(resultado) {
  const videos = await obtenerListaVideos(resultado.id);
  
  console.log("Videos obtenidos del servidor:", videos);
  // Estado
  setVideoActual(resultado.video);
  setListaVideos(videos);
  resetSeleccion();

  console.log("state.listaVideos:", state.listaVideos);
  console.log("state.videoActual:", state.videoActual);
  console.log("includes?", state.listaVideos.includes(state.videoActual));

  // Validar existencia
  if (!state.listaVideos.includes(state.videoActual)) {
    console.error(`Video ${state.videoActual} no existe en servidor`);
    mostrarPopup("El video no existe en el servidor");
    return;
  }

  // Limpiar resultados listados
  const resultadosDiv = document.getElementById("resultados");
  if (resultadosDiv) resultadosDiv.innerHTML = "";

  // Player y panel
  configurarReproductor(resultado.video);
  renderTranscripcionSeleccionadaVideo(resultado);

  // Mostrar controles y actualizar contador
  mostrarControles();
  actualizarContador();

  scrollToPlayer();
}

// Ajustar timeline del clip actual
export function ajustarClip(segundos) {
  const { videoElement } = getRefs();
  if (!videoElement) return;
  videoElement.currentTime += segundos;
}

// Expandir/quitar selección de videos
export function expandir(direccion, lado) {
  const idx = indiceActual();
  if (idx === -1) {
    mostrarPopup("Error: Video no encontrado");
    return;
  }

  const esAtras = lado === "atras";
  const disponiblesAtras = idx;
  const disponiblesAdelante = state.listaVideos.length - idx - 1;

  if (direccion === 1) {
    const seleccionados = esAtras ? state.acumuladosAtras : state.acumuladosAdelante;
    const maximoPosible = Math.min(
      MAX_ADICIONALES,
      esAtras ? disponiblesAtras : disponiblesAdelante
    );

    if (seleccionados < maximoPosible) {
      if (esAtras) state.acumuladosAtras++;
      else state.acumuladosAdelante++;
      mostrarPopup(`Se agregó un video ${lado}`);
    } else if (seleccionados >= MAX_ADICIONALES) {
      mostrarPopup(`Máximo ${MAX_ADICIONALES} videos ${lado}`);
    } else {
      mostrarPopup(`No hay más videos ${lado}`);
    }
  } else {
    if (esAtras ? state.acumuladosAtras > 0 : state.acumuladosAdelante > 0) {
      if (esAtras) state.acumuladosAtras--;
      else state.acumuladosAdelante--;
      mostrarPopup(`Se quitó un video ${lado}`);
    } else {
      mostrarPopup(`No hay más videos ${lado}`);
    }
  }

  actualizarContador();
}

// Descargar concatenado
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

  // Selección
  const inicio = Math.max(0, idx - state.acumuladosAtras);
  const fin = Math.min(state.listaVideos.length - 1, idx + state.acumuladosAdelante);
  const seleccion = state.listaVideos.slice(inicio, fin + 1);
  if (seleccion.length === 0) {
    mostrarPopup("No hay videos para concatenar");
    return;
  }

  // UI
  mostrarCargando(true);
  actualizarEstadoDescarga("Concatenando videos...", "normal");
  deshabilitarBotonDescarga(true, "Procesando...");
  mostrarPopup(`Procesando ${seleccion.length} videos...`);
  const btn = document.getElementById("btnDescargar");
  const textoOriginal = btn.textContent;

  try {
    const res = await concatenarVideos(seleccion);

    mostrarCargando(false);
    deshabilitarBotonDescarga(false, textoOriginal);

    if (!res.ok) {
      actualizarEstadoDescarga("Error en la concatenación", "error");
      mostrarPopup(`Error al generar clip: ${res.status} ${res.statusText}`);
      return;
    }

    actualizarEstadoDescarga("Descargando archivo...", "normal");

    // Descargar
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = "clip_concatenado.mp4";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    mostrarPopup("Descarga iniciada");
    actualizarEstadoDescarga("Descarga completada", "success");
    setTimeout(() => {
      const ds = document.getElementById("download-status");
      if (ds) ds.style.display = "none";
    }, 5000);
  } catch (e) {
    mostrarCargando(false);
    deshabilitarBotonDescarga(false, textoOriginal);
    mostrarPopup("Error en la descarga");
    actualizarEstadoDescarga("Error en la descarga", "error");
    console.error(e);
  }
}
