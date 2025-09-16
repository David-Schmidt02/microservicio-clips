const BASE = "http://127.0.0.1:8000";

export async function buscarCoincidenciasElastic(palabra) {
  const res = await fetch(`${BASE}/buscar?palabra=${encodeURIComponent(palabra)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json(); // {resultados: [...]}
}

export async function obtenerListaVideos(transcripcionId) {
  const res = await fetch(`${BASE}/videos?transcripcionId=${transcripcionId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  console.log("Datos obtenidos de /videos:", data);
  return Array.isArray(data.videos) ? data.videos : [];
}

export async function concatenarVideos(videos) {
  // Devuelvo el Response para que el caller pueda convertirlo a Blob y descargar
  return fetch(`${BASE}/concatenar`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ videos }),
  });
}
