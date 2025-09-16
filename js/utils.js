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

// === Implementación comentada: extraer info de la RUTA del video ===
// Soporta rutas tipo "a24/a24_20250905_234106_20250905_234236.ts"
// y también un simple "video_1.mp4"
export function extraerInfoVideo(rutaVideo) {
  if (!rutaVideo || typeof rutaVideo !== "string") {
    return {
      canal: "Desconocido",
      nombreCompleto: String(rutaVideo ?? ""),
      nombreCorto: String(rutaVideo ?? ""),
      fecha: "Desconocida",
    };
  }

  // Canal = primera carpeta si hay subcarpetas
  const partes = rutaVideo.split("/");
  const canal = partes.length > 1 ? partes[0] : "Desconocido";
  const nombreArchivo = partes[partes.length - 1];

  // Intentar extraer fecha/hora de patrones _AAAAMMDD_HHMMSS
  // Ej.: a24_20250905_234106_20250905_234236.ts  => tomamos la primera fecha/hora
  const patron = /(\d{8})_(\d{6})/;
  const match = nombreArchivo.match(patron);

  let fecha = "Desconocida";
  if (match) {
    const [_, f, h] = match; // f=AAAAMMDD, h=HHMMSS
    const año = f.substring(0, 4);
    const mes = f.substring(4, 6);
    const dia = f.substring(6, 8);
    const HH = h.substring(0, 2);
    const MM = h.substring(2, 4);
    const SS = h.substring(4, 6);
    fecha = `${dia}/${mes}/${año} ${HH}:${MM}:${SS}`;
  }

  const nombreCorto =
    nombreArchivo.length > 30 ? nombreArchivo.slice(0, 27) + "..." : nombreArchivo;

  return {
    canal,
    nombreCompleto: nombreArchivo,
    nombreCorto,
    fecha,
  };
}

export function recortarTexto(texto, maxCaracteres = 20) {
  return texto.length > maxCaracteres
    ? texto.slice(0, maxCaracteres) + "..."
    : texto;
}