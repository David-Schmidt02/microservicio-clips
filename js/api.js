const BASE = "http://127.0.0.1:8000";

export async function buscarCoincidenciasElastic(palabra) {
  const res = await fetch(`${BASE}/buscar?palabra=${encodeURIComponent(palabra)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json(); // {resultados: [...]}
}
  
export async function obtenerListaVideos(canal, start_timestamp, end_timestamp) {
  const res = await fetch(`${BASE}/videos?canal=${encodeURIComponent(canal)}&timestamp_start=${encodeURIComponent(start_timestamp)}&timestamp_end=${encodeURIComponent(end_timestamp)}`);
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
  return `${BASE}/descargar?clip=${encodeURIComponent(nombreArchivo)}`;
}

export async function concatenarYDescargar(videos, canal) {
  console.log("Concatenando videos:", videos, "canal:", canal);
  const resp = await fetch(`${BASE}/concatenar`, {
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

  const nombreArchivo = data && data.archivo;
  if (!nombreArchivo) {
    throw new Error("La respuesta no incluyó el nombre del archivo generado");
  }

  console.log("Archivo concatenado generado:", nombreArchivo);
  return nombreArchivo;
}


export async function obtenerTranscripcionClip(canal, timestampStart, timestampEnd) {
  const params = new URLSearchParams({
    canal,
    timestamp_start: timestampStart,
  });
  if (timestampEnd) {
    params.append("timestamp_end", timestampEnd);
  }
  const res = await fetch(`${BASE}/transcripcion?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data?.transcripcion ?? null;
}
