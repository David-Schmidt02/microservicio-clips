import { state } from "./state.js";
import { formatTs, extraerInfoVideo, recortarTexto } from "./utils.js";

// Referencias globales (DOM) - las inicializamos una vez
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
  if (refs.videoPlayer) refs.videoPlayer.style.display = "none";
  const controls = document.getElementById("video-control-container");
  if (controls) controls.style.display = "none";
}

export function mostrarControles() {
  const controls = document.getElementById("video-control-container");
  if (controls) controls.style.display = "block";
  if (refs.videoPlayer) refs.videoPlayer.style.display = "flex";
}

export function scrollToPlayer() {
  if (refs.videoPlayer) refs.videoPlayer.scrollIntoView({ behavior: "smooth" });
}

export function getRefs() {
  return refs;
}

// Render de resultados simples (tarjetas sueltas)
export function renderResultados(resultados, onClickVideo) {
  const cont = document.getElementById("resultados");
  const empty = document.getElementById("empty-state");
  if (!cont) return;
  cont.innerHTML = "";

  if (!Array.isArray(resultados) || resultados.length === 0) {
    if (empty) {
      const title = empty.querySelector(".empty-state__title");
      const subtitle = empty.querySelector(".empty-state__subtitle");
      if (title) title.textContent = "Sin coincidencias";
      if (subtitle) subtitle.textContent = "Intenta con otra palabra clave o revisa la ortografía.";
      empty.classList.remove("hidden");
    }
    return;
  }

  if (empty) {
    empty.classList.add("hidden");
  }

  const canales = Array.from(new Set(resultados.map(r => r.canal)));
  canales.forEach(canal => {
    const boxCanal = document.createElement("div");
    boxCanal.className = "channel-box";

    const title = document.createElement("div");
    title.className = "channel-title";
    title.textContent = `Canal: ${canal}`;

    const resultadosCanal = resultados.filter(r => r.canal === canal);
    resultadosCanal.forEach((resultado) => {
      const box = document.createElement("div");
      box.className = "transcription-box";

      const txt = document.createElement("div");
      txt.className = "transcription-text";
      txt.textContent = recortarTexto(resultado.texto, 45);
      box.appendChild(txt);

      box.addEventListener("click", () => mostrarTranscripcionSeleccionadaCompleta(resultado, onClickVideo));

      boxCanal.appendChild(box);
    });

    boxCanal.prepend(title);
    cont.appendChild(boxCanal);
  });
}

// Ventana modal con la transcripcion completa seleccionada
export function mostrarTranscripcionSeleccionadaCompleta(transcripcion, mostrarVideo) {
  const prev = document.getElementById("modal-transcripcion");
  if (prev) prev.remove();

  const overlay = document.createElement("div");
  overlay.id = "modal-transcripcion";
  overlay.className = "modal-transcripcion-overlay";

  const modal = document.createElement("div");
  modal.className = "modal-transcripcion";

  const btnCerrar = document.createElement("button");
  btnCerrar.className = "modal-close";
  btnCerrar.type = "button";
  btnCerrar.textContent = "X";
  btnCerrar.addEventListener("click", () => overlay.remove());

  const title = document.createElement("div");
  title.className = "modal-title";
  title.textContent = "Transcripción completa";

  // Info adicional del modal
  const infoBox = document.createElement("div");
  infoBox.className = "modal-info";
  // Canal
  const canalInfo = document.createElement("div");
  canalInfo.className = "modal-canal";
  canalInfo.textContent = `Canal: ${transcripcion.canal || "Desconocido"}`;
  // Horario
  const horarioInfo = document.createElement("div");
  horarioInfo.className = "modal-horario";
  // Formatear fecha si es posible
  let fechaStr = transcripcion.timestamp;
  try {
    if (fechaStr) {
      const dt = new Date(fechaStr);
      fechaStr = dt.toLocaleString();
    }
  } catch {}
  horarioInfo.textContent = `Horario: ${fechaStr || "-"}`;
  // Video ID (si existe)
  const videoIdInfo = document.createElement("div");
  videoIdInfo.className = "modal-videoid";
  if (transcripcion.video_id) {
    videoIdInfo.textContent = `Video ID: ${transcripcion.video_id}`;
    infoBox.appendChild(videoIdInfo);
  }
  infoBox.appendChild(canalInfo);
  infoBox.appendChild(horarioInfo);

  const scrollBox = document.createElement("div");
  scrollBox.className = "modal-scroll";
  const text = document.createElement("div");
  text.className = "modal-text";
  text.textContent = "Cargando transcripciones...";
  scrollBox.appendChild(text);

  // Nueva lógica: hit a obtenerTranscripcionClip con duración corta
  (async () => {
    try {
      // Import dinámico para evitar dependencias circulares
      const api = await import("./api.js");
      const canal = transcripcion.canal;
      const timestamp = transcripcion.timestamp;
      // Duración corta (30 segundos)
      const res = await api.obtenerTranscripcionClip(canal, timestamp, 30);
      if (res && res.texto) {
        text.textContent = res.texto;
      } else {
        text.textContent = transcripcion.texto || "Sin transcripciones en el rango";
      }
    } catch (err) {
      text.textContent = "Error al cargar transcripciones";
    }
  })();

  const btnVerVideo = document.createElement("button");
  btnVerVideo.className = "modal-action";
  btnVerVideo.type = "button";
  btnVerVideo.textContent = "Ver clip";
  btnVerVideo.addEventListener("click", () => {
    overlay.remove();
    mostrarVideo(transcripcion);
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });

  modal.append(btnCerrar, title, scrollBox, btnVerVideo);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
}

// Render de panel derecho (transcripcion seleccionada)
export function renderTranscripcionSeleccionadaVideo(resultado) {
  const cont = document.getElementById("selected-transcription");
  if (!cont) return;

  const info = extraerInfoVideo(resultado);

  const textoContenido = (resultado && typeof resultado === "object" && typeof resultado.texto === "string")
    ? resultado.texto
    : `Clip seleccionado: ${info.nombreCorto}`;

  const canalContenido = (resultado && typeof resultado === "object" && resultado.canal)
    ? resultado.canal
    : (info.canal && info.canal !== "Desconocido" ? info.canal : state.canalActual || "Desconocido");

  const fechaCruda = (resultado && typeof resultado === "object" && resultado.start_timestamp)
    ? resultado.start_timestamp
    : info.timestamp ?? null;

  const fechaContenido = fechaCruda
    ? formatTs(fechaCruda)
    : (info.fecha && info.fecha !== "Desconocida" ? info.fecha : state.fecha || "Desconocida");

  cont.innerHTML = "";

  const title = document.createElement("div");
  title.className = "selected-channel-title";
  title.textContent = "Transcripcion seleccionada";

  const resumen = document.createElement("div");
  resumen.className = "selected-transcription-summary";
  const resumenTexto = info.nombreCorto || info.fecha || "Clip";
  resumen.textContent = `Clip seleccionado: ${resumenTexto}`;

  const text = document.createElement("div");
  text.className = "selected-transcription-text";
  text.textContent = textoContenido;

  const meta = document.createElement("div");
  meta.className = "selected-transcription-info";
  meta.innerHTML = `
    <p><strong>Fecha:</strong> ${fechaContenido}</p>
    <p><strong>Canal:</strong> ${canalContenido}</p>
  `;

  const btn = document.createElement("button");
  btn.id = "btnNuevaBusqueda";
  btn.className = "btn-secondary";
  btn.type = "button";
  btn.textContent = "Nueva busqueda";
  btn.addEventListener("click", () => {
    ocultarReproductor();
    const input = document.getElementById("busqueda");
    if (input) input.focus();
  });

  cont.append(title, resumen, text, meta, btn);
}

export function renderClipsRelacionados(videos, videoActual, onSelect, onToggle) {
  const cont = document.getElementById("related-clips");
  if (!cont) return;

  cont.innerHTML = "";

  if (!Array.isArray(videos) || videos.length === 0) {
    const empty = document.createElement("div");
    empty.className = "related-empty";
    empty.textContent = "No hay clips relacionados";
    cont.appendChild(empty);
    return;
  }

  const indexActual = typeof videoActual === "string" ? videos.indexOf(videoActual) : -1;
  const centro = indexActual >= 0 ? indexActual : 0;
  const inicio = Math.max(0, centro - 3);
  const fin = Math.min(videos.length - 1, centro + 3);
  const incluidosAtras = state.acumuladosAtras;
  const incluidosAdelante = state.acumuladosAdelante;
  const maxAdicionales = 3;

  for (let i = inicio; i <= fin; i++) {
    const nombre = videos[i];
    const infoClip = extraerInfoVideo(nombre);
    const offset = i - centro;

    const card = document.createElement("button");
    card.type = "button";
    card.className = "related-clip-card";
    if (i === centro) card.classList.add("is-active");
    card.setAttribute("aria-pressed", i === centro ? "true" : "false");
    card.dataset.clip = nombre;
    card.dataset.offset = String(offset);

    const incluido = offset < 0
      ? Math.abs(offset) <= incluidosAtras
      : offset > 0
        ? offset <= incluidosAdelante
        : false;

    if (incluido && offset !== 0) {
      card.classList.add("is-selected");
    }

    const offsetLabel = document.createElement("span");
    offsetLabel.className = "related-clip-offset";
    offsetLabel.textContent = offset === 0 ? "ACTUAL" : `${offset > 0 ? "+" : ""}${offset}`;

    const infoBox = document.createElement("div");
    infoBox.className = "related-clip-info";

    const title = document.createElement("span");
    title.className = "related-clip-title";
    title.textContent = infoClip.nombreCorto || nombre;

    const meta = document.createElement("span");
    meta.className = "related-clip-meta";
    const metaParts = [];
    if (infoClip.fecha && infoClip.fecha !== "Desconocida") metaParts.push(infoClip.fecha);
    const canalLabel = infoClip.canal && infoClip.canal !== "Desconocido" ? infoClip.canal : state.canalActual;
    if (canalLabel) metaParts.push(canalLabel);
    meta.textContent = metaParts.join(" | ");

    infoBox.appendChild(title);
    if (meta.textContent) infoBox.appendChild(meta);

    card.append(offsetLabel, infoBox);

    let mostrarToggle = false;
    let toggleEsAgregar = false;

    if (offset !== 0) {
      if (incluido) {
        mostrarToggle = true;
        toggleEsAgregar = false;
      } else if (offset < 0) {
        const objetivo = Math.abs(offset);
        if (objetivo === incluidosAtras + 1 && incluidosAtras < maxAdicionales) {
          mostrarToggle = true;
          toggleEsAgregar = true;
        }
      } else {
        if (offset === incluidosAdelante + 1 && incluidosAdelante < maxAdicionales) {
          mostrarToggle = true;
          toggleEsAgregar = true;
        }
      }
    }

    if (mostrarToggle) {
      const toggleBtn = document.createElement("button");
      toggleBtn.type = "button";
      toggleBtn.className = `related-clip-action ${toggleEsAgregar ? "related-clip-action--add" : "related-clip-action--remove"}`;
      toggleBtn.textContent = toggleEsAgregar ? "+" : "-";
      toggleBtn.title = toggleEsAgregar
        ? "Agregar este clip a la concatenacion"
        : "Quitar este clip de la concatenacion";
      toggleBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        if (typeof onToggle === "function") {
          onToggle(offset, toggleEsAgregar);
        }
      });
      card.appendChild(toggleBtn);
    }

    if (typeof onSelect === "function") {
      card.addEventListener("click", () => onSelect(nombre));
    }

    cont.appendChild(card);
  }
}


// Estado descargando / botones
export function actualizarEstadoDescarga(mensaje, tipo = "normal") {
  const el = document.getElementById("download-status");
  if (!el) return;
  el.textContent = mensaje;
  el.style.display = "block";
  el.style.color = tipo === "error" ? "#ff5757" : tipo === "success" ? "#4caf50" : "#fff";
}

export function deshabilitarBotonDescarga(deshabilitar, texto) {
  const btn = document.getElementById("btnDescargar");
  if (!btn) return;
  btn.textContent = texto;
  btn.disabled = deshabilitar;
}

export function actualizarContador() {
  const label = document.getElementById("contador");
  if (!label) return;
  label.textContent = `${state.acumuladosAtras} atras | ${state.acumuladosAdelante} adelante`;
}

// Titulo del player (usamos info del nombre de archivo)
export function setTituloPlayer(origenVideo) {
  const info = extraerInfoVideo(origenVideo);
  const fallbackRaw = typeof origenVideo === "string" ? origenVideo.split(/[\/]/).pop() || "" : "";
  const fallbackSinExtension = fallbackRaw.replace(/\.[^.]+$/, "");
  const nombreLegible = info.nombreCorto || fallbackSinExtension || fallbackRaw || "clip";
  const tieneCanal = info.canal && info.canal !== "Desconocido";

  let titulo = tieneCanal
    ? `${info.canal} - ${nombreLegible}`
    : `Reproduciendo: ${nombreLegible}`;

  if (info.fecha && info.fecha !== "Desconocida") {
    titulo += ` (${info.fecha})`;
  }

  const { videoTitle } = getRefs();
  if (videoTitle) {
    videoTitle.textContent = titulo;
  }
}
