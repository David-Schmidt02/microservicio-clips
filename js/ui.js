import { state } from "./state.js";
import { formatTime, formatTs, extraerInfoVideo, recortarTexto } from "./utils.js";

// Referencias globales (DOM) — las inicializamos una vez
const refs = {
  videoPlayer: null,
  videoElement: null,
  videoSrc: null,
  videoTitle: null,
};

export function initDOMRefs() {
  refs.videoPlayer = document.getElementById("video-player");
  refs.videoElement = document.getElementById("video");
  refs.videoSrc = document.getElementById("video-src");
  refs.videoTitle = document.getElementById("video-title");
  // Ocultar controles al inicio
  const vc = document.getElementById("video-control-container");
  if (vc) vc.style.display = "none";
}

export function ocultarReproductor() {
  refs.videoPlayer.style.display = "none";
  document.getElementById("video-control-container").style.display = "none";
}

export function mostrarControles() {
  document.getElementById("video-control-container").style.display = "block";
  refs.videoPlayer.style.display = "flex";
}

export function scrollToPlayer() {
  refs.videoPlayer.scrollIntoView({ behavior: "smooth" });
}

export function getRefs() {
  return refs;
}

// Render de resultados simples (tarjetas sueltas)
export function renderResultados(resultados, onClickVideo) {
  const cont = document.getElementById("resultados");
  cont.innerHTML = "";

  if (!resultados || resultados.length === 0) { // podemos poner un contador del mensaje
    cont.innerHTML = "<p style='text-align:center'>No se encontraron resultados</p>";
    return;
  }

  const canales = Array.from(new Set(resultados.map(r => r.canal)));
  canales.forEach(canal => {
    const box_canal = document.createElement("div");
    box_canal.className = "channel-box";

    const title = document.createElement("div");
    title.className = "channel-title";
    title.textContent = `Canal: ${canal}`;

    const resultadosCanal = resultados.filter(r => r.canal === canal);
    resultadosCanal.forEach((r, idx) => {

      const box = document.createElement("div");
      box.className = "transcription-box";

      const txt = document.createElement("div");
      txt.className = "transcription-text";
      txt.textContent = recortarTexto(r.texto, 45);
      box.appendChild(txt);

      //mostramos la transcripcion completa si se selecciona
      box.addEventListener("click", () => mostrarTranscripcionSeleccionadaCompleta(r, onClickVideo));

      box_canal.appendChild(box); 
    });
    box_canal.prepend(title); // prepend para que el título quede arriba
    cont.appendChild(box_canal);
  });
  
}

// ventana con la transcripcion completa seleccionada
export function mostrarTranscripcionSeleccionadaCompleta(resultado, mostrarVideo) {
  // Elimina cualquier modal anterior
  const prev = document.getElementById("modal-transcripcion");
  if (prev) prev.remove();

  const info = extraerInfoVideo(resultado.video);

  // Overlay
  const overlay = document.createElement("div");
  overlay.id = "modal-transcripcion";
  overlay.className = "modal-transcripcion-overlay";

  // Modal
  const modal = document.createElement("div");
  modal.className = "modal-transcripcion";

  // Botón cerrar
  const btnCerrar = document.createElement("button");
  btnCerrar.className = "modal-close";
  btnCerrar.textContent = "✕";
  btnCerrar.addEventListener("click", () => overlay.remove());

  // Título
  const title = document.createElement("div");
  title.className = "modal-title";
  title.textContent = "Transcripción completa";

  // Scrollable
  const scrollBox = document.createElement("div");
  scrollBox.className = "modal-scroll";
  const text = document.createElement("div");
  text.className = "modal-text";
  text.textContent = resultado.texto;
  scrollBox.appendChild(text);


  // Botón para ver el video
  const btnVerVideo = document.createElement("button");
  btnVerVideo.className = "modal-action";
  btnVerVideo.textContent = "Ver clip";
  btnVerVideo.addEventListener("click", () => {
    overlay.remove();
    mostrarVideo(resultado); // usa tu función existente
  });

  // Cerrar modal al hacer click fuera
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });

  // Ensamblar
  modal.append(btnCerrar, title, scrollBox, btnVerVideo);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
}

// Render de panel derecho (transcripción seleccionada) — con info del archivo habilitada
export function renderTranscripcionSeleccionadaVideo(resultado) {
  const cont = document.getElementById("selected-transcription");
  const info = extraerInfoVideo(resultado.video);

  cont.innerHTML = "";
  const title = document.createElement("div");
  title.className = "selected-channel-title";
  title.textContent = "Transcripción seleccionada";

  const text = document.createElement("div");
  text.className = "selected-transcription-text";
  text.textContent = resultado.texto;

  const meta = document.createElement("div");
  meta.className = "selected-transcription-info";
  meta.innerHTML = `
    <p><strong>Fecha:</strong> ${formatTs(resultado.timestamp)}</p>
    <p><strong>Canal:</strong> ${info.canal}</p>
    <p><strong>Video:</strong> ${info.nombreCorto}</p>
    <p><strong>Fecha video:</strong> ${info.fecha}</p>
    <p><strong>Posición:</strong> ${formatTime(resultado.segundo_inicio || 0)}</p>
  `;

  const btn = document.createElement("button");
  btn.id = "btnNuevaBusqueda";
  btn.className = "btn-secondary";
  btn.textContent = "Nueva búsqueda";
  btn.addEventListener("click", () => {
    ocultarReproductor();
    document.getElementById("busqueda").focus();
  });

  cont.append(title, text, meta, btn);
}

// Estado descargando / botones
export function actualizarEstadoDescarga(mensaje, tipo = "normal") {
  const el = document.getElementById("download-status");
  el.textContent = mensaje;
  el.style.display = "block";
  el.style.color = tipo === "error" ? "#ff5757" : tipo === "success" ? "#4caf50" : "#fff";
}

export function deshabilitarBotonDescarga(deshabilitar, texto) {
  const btn = document.getElementById("btnDescargar");
  btn.textContent = texto;
  btn.disabled = deshabilitar;
}

export function actualizarContador() {
  document.getElementById("contador").textContent =
    `${state.acumuladosAtras} atrás | ${state.acumuladosAdelante} adelante`;
}

// Título del player (usamos info del nombre de archivo)
export function setTituloPlayer(nombreVideo) {
  const info = extraerInfoVideo(nombreVideo);
  const titulo = info.canal !== "Desconocido"
    ? `${info.canal} — ${info.nombreCorto}`
    : `Reproduciendo: ${info.nombreCorto}`;
  const { videoTitle } = getRefs();
  videoTitle.textContent = titulo;
}

