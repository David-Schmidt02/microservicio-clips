// UI helpers
export function mostrarCargando(mostrar) {
  const el = document.getElementById("loading");
  if (el) el.style.display = mostrar ? "flex" : "none";
}

export function mostrarPopup(mensaje) {
  const popup = document.getElementById("popup");
  if (!popup) {
    console.error("Elemento popup no encontrado");
    alert(mensaje);
    return;
  }
  popup.textContent = mensaje;
  popup.style.display = "block";
  if (popup.timeoutId) clearTimeout(popup.timeoutId);
  popup.timeoutId = setTimeout(() => { popup.style.display = "none"; }, 3000);
}

export function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
}

export function formatTs(ts) {
  // Si ts ya viene ISO, el toLocaleString anda bien.
  const d = new Date(ts);
  return isNaN(d.getTime()) ? ts : d.toLocaleString();
}

// Soporta rutas tipo "a24/a24_20250905_234106_20250905_234236.ts"

export function extraerInfoVideo(transcripcionDTO) {
  console.log("Extraer info de video - input:", transcripcionDTO);
  // Si no es un objeto o es null, devolvemos valores por defecto
  if (!transcripcionDTO || typeof transcripcionDTO !== "object") {
    return {
      canal: "Desconocido",
      fecha: "Desconocida",
    };
  }
  // Si es un objeto, devolvemos los datos o valores por defecto
  return {
    canal: transcripcionDTO.canal ?? "Desconocido",
    fecha: extraerFecha(transcripcionDTO.start_timestamp)
  };
}

function extraerFecha(ts) {
  const d = new Date(ts);
  return isNaN(d.getTime()) ? "Desconocida" : d.toLocaleDateString();
}

function extraerHora(ts) {
  const d = new Date(ts);
  return isNaN(d.getTime()) ? "Desconocida" : d.toLocaleTimeString();
}

export function recortarTexto(texto, maxCaracteres = 30) {
  return texto.length > maxCaracteres
    ? texto.slice(0, maxCaracteres) + "..."
    : texto;
}