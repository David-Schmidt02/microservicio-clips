const BASE = "http://127.0.0.1:8001";
const API_BASE = `${BASE}/api/v1`;

export async function buscarCoincidenciasElastic(palabra) {
  const res = await fetch(`${API_BASE}/search/buscar?palabra=${encodeURIComponent(palabra)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json(); // {resultados: [...]}
}
  
export async function obtenerListaVideos(canal, timestamp) {
  const params = new URLSearchParams({
    canal,
    timestamp: timestamp,
    rango: 3
  });
  const res = await fetch(`${API_BASE}/clips/videos?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data.videos) ? data.videos : [];
}


export function descargarArchivoSinRecarga(url, filename = "") {
  const a = document.createElement('a');
  a.href = url;
  if (filename) {
    a.download = filename;
  } else {
    a.download = "";
  }
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

export function obtenerUrlDescarga(nombreArchivo) {
  return `${API_BASE}/clips/descargar?clip=${encodeURIComponent(nombreArchivo)}`;
}

export function obtenerUrlVideo(canal, nombreArchivo) {
  return `${API_BASE}/clips/video/${encodeURIComponent(canal)}/${encodeURIComponent(nombreArchivo)}`;
}

export async function concatenarYDescargar(videos, canal) {
  console.log("Concatenando videos:", videos, "canal:", canal);
  const resp = await fetch(`${API_BASE}/clips/concatenar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ videos, canal }),
  });

  let data;
  try {
    data = await resp.json();
  } catch (err) {
    console.error("No se pudo parsear la respuesta de /concatenar", err);
    data = null;
  }

  if (!resp.ok) {
    const mensaje = data && data.error ? data.error : `HTTP ${resp.status}`;
    throw new Error(mensaje);
  }

  const nombreArchivo = data && data.clip_filename;
  if (!nombreArchivo) {
    throw new Error("La respuesta no incluyó el nombre del archivo generado");
  }

  console.log("Archivo concatenado generado:", nombreArchivo);
  return nombreArchivo;
}


export async function obtenerTranscripcionClip(canal, timestamp, duracion_segundos = 90) {
  const params = new URLSearchParams({
    canal,
    timestamp: timestamp,
    duracion_segundos: duracion_segundos
  });
  const res = await fetch(`${API_BASE}/search/transcripcionClip?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data; // Devolver el objeto completo con {texto, canal, timestamp}
}
