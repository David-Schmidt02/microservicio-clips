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

export function descargarArchivoSinRecarga(url) {
  const a = document.createElement('a');
  a.href = url;
  a.download = '';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

export async function concatenarYDescargar(videos, canal) {
  console.log("Concatenando videos:", videos, "canal:", canal);
  const resp = await fetch(`${BASE}/concatenar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ videos, canal }),
  });

  const data = await resp.json();
  console.log("Respuesta de /concatenar:", data);

  const nombreArchivo = data.archivo;
  if (!nombreArchivo) {
    alert("No se pudo generar el archivo. Respuesta del servidor: " + JSON.stringify(data));
    return;
  }

  console.log("Descargando archivo:", nombreArchivo);
  descargarArchivoSinRecarga(`${BASE}/descargar?clip=${encodeURIComponent(nombreArchivo)}`);
}
