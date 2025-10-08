// UI helpers
export function mostrarCargando(mostrar) {
  const el = document.getElementById("loading");
  if (!el) return;
  el.classList.toggle("hidden", !mostrar);
  if (mostrar) {
    el.setAttribute("aria-busy", "true");
  } else {
    el.removeAttribute("aria-busy");
  }
}

export function mostrarPopup(mensaje) {
  const popup = document.getElementById("popup");
  if (!popup) {
    console.error("Elemento popup no encontrado");
    alert(mensaje);
    return;
  }
  popup.textContent = mensaje;
  popup.classList.add("show");
  if (popup.timeoutId) clearTimeout(popup.timeoutId);
  popup.timeoutId = setTimeout(() => {
    popup.classList.remove("show");
  }, 3000);
}

export function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
}

export function formatTs(ts) {
  const d = new Date(ts);
  // Usar toLocaleString con zona horaria específica para Argentina y formato 24hs
  return isNaN(d.getTime()) ? ts : d.toLocaleString('es-AR', {
    timeZone: 'America/Argentina/Buenos_Aires',
    day: '2-digit',
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false  // Formato 24 horas
  });
}

export function extraerInfoVideo(origen) {

  if (typeof origen === "string") {
    return extraerInfoDesdeNombre(origen);
  }

  if (origen && typeof origen === "object") {
    const infoDesdeNombre = typeof origen.video === "string" ? extraerInfoDesdeNombre(origen.video) : null;

    const canal = origen.canal ?? infoDesdeNombre?.canal ?? "Desconocido";

    const timestamp = normalizarIso(origen.start_timestamp) ?? infoDesdeNombre?.timestamp ?? null;
    const timestampFin = normalizarIso(origen.end_timestamp) ?? infoDesdeNombre?.timestampFin ?? null;

    const fecha = timestamp ? extraerFecha(timestamp)
      : (typeof origen.fecha === "string" ? origen.fecha : infoDesdeNombre?.fecha ?? "Desconocida");

    const horaDesdeTimestamp = timestamp ? extraerHora(timestamp) : null;

    const nombreCorto = origen.nombreCorto
      ?? (horaDesdeTimestamp && horaDesdeTimestamp !== "Desconocida" ? horaDesdeTimestamp : null)
      ?? infoDesdeNombre?.nombreCorto
      ?? (typeof origen.nombre === "string" ? origen.nombre : null)
      ?? (typeof origen.video === "string" ? quitarExtension(obtenerNombreArchivo(origen.video)) : null)
      ?? "Clip sin titulo";

    return {
      canal,
      fecha,
      nombreCorto,
      timestamp,
      timestampFin,
    };
  }

  return {
    canal: "Desconocido",
    fecha: "Desconocida",
    nombreCorto: "Clip sin titulo",
    timestamp: null,
    timestampFin: null,
  };
}

function extraerInfoDesdeNombre(nombre) {
  const archivo = obtenerNombreArchivo(nombre);
  const sinExtension = quitarExtension(archivo);
  const match = sinExtension.match(/^(?<canal>[^_]+)_(?<fechaInicio>\d{8})_(?<horaInicio>\d{6})(?:_(?<fechaFin>\d{8})_(?<horaFin>\d{6}))?/);

  if (!match || !match.groups) {
    return {
      canal: "Desconocido",
      fecha: "Desconocida",
      nombreCorto: sinExtension || archivo,
      timestamp: null,
      timestampFin: null,
    };
  }

  const { canal, fechaInicio, horaInicio, fechaFin, horaFin } = match.groups;
  const fechaLegible = formatearFechaDesdeCadena(fechaInicio) ?? "Desconocida";
  const horaLegible = formatearHoraDesdeCadena(horaInicio);
  const timestamp = crearTimestampIso(fechaInicio, horaInicio);
  const timestampFin = fechaFin && horaFin ? crearTimestampIso(fechaFin, horaFin) : null;

  return {
    canal: canal || "Desconocido",
    fecha: fechaLegible,
    nombreCorto: horaLegible ?? sinExtension,
    timestamp,
    timestampFin,
  };
}

function obtenerNombreArchivo(ruta) {
  if (typeof ruta !== "string") return "Clip sin titulo";
  const partes = ruta.split(/[\\/]/);
  return partes.pop() || ruta;
}

function quitarExtension(nombre) {
  return typeof nombre === "string" ? nombre.replace(/\.[^.]+$/, "") : nombre;
}

function formatearFechaDesdeCadena(yyyymmdd) {
  if (!/^\d{8}$/.test(yyyymmdd)) return null;
  const year = Number(yyyymmdd.slice(0, 4));
  const month = Number(yyyymmdd.slice(4, 6));
  const day = Number(yyyymmdd.slice(6, 8));
  const date = new Date(Date.UTC(year, month - 1, day));
  return isNaN(date.getTime()) ? null : date.toLocaleDateString('es-AR', {
    timeZone: 'America/Argentina/Buenos_Aires',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
}

function formatearHoraDesdeCadena(hhmmss) {
  if (!/^\d{6}$/.test(hhmmss)) return null;
  const hh = hhmmss.slice(0, 2);
  const mm = hhmmss.slice(2, 4);
  const ss = hhmmss.slice(4, 6);
  return `${hh}:${mm}:${ss}`;
}

function crearTimestampIso(yyyymmdd, hhmmss) {
  if (!/^\d{8}$/.test(yyyymmdd) || !/^\d{6}$/.test(hhmmss)) return null;
  const iso = `${yyyymmdd.slice(0, 4)}-${yyyymmdd.slice(4, 6)}-${yyyymmdd.slice(6, 8)}T${hhmmss.slice(0, 2)}:${hhmmss.slice(2, 4)}:${hhmmss.slice(4, 6)}`;
  
  // Los archivos están en zona horaria de Argentina, no UTC
  // Crear el timestamp con offset de Argentina (-03:00)
  const timestampArgentina = `${iso}-03:00`;
  const d = new Date(timestampArgentina);
  return isNaN(d.getTime()) ? null : timestampArgentina;
}

function normalizarIso(ts) {
  if (typeof ts !== "string" || !ts) return null;
  if (ts.endsWith("Z")) return ts;
  if (/[+-]\d{2}:\d{2}$/.test(ts)) return ts;
  return `${ts}Z`;
}

function extraerFecha(ts) {
  return formatTs(ts);
}

function extraerHora(ts) {
  return formatTs(ts);
}

export function recortarTexto(texto, maxCaracteres = 30) {
  return texto.length > maxCaracteres
    ? texto.slice(0, maxCaracteres) + "..."
    : texto;
}
