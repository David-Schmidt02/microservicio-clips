import { log } from "winjs";

// Variables para el manejo de videos
let listaVideos = [];                  // Lista de todos los videos disponibles
let videoActual = null;                // Video seleccionado actualmente
let acumuladosAtras = 0;               // Número de videos seleccionados hacia atrás
let acumuladosAdelante = 0;            // Número de videos seleccionados hacia adelante

// Referencias a elementos DOM frecuentemente usados
let videoPlayer;                       // Contenedor del reproductor
let videoElement;                      // Elemento <video> HTML5
let videoSrc;                          // Elemento <source> dentro del video
let videoTitle;                        // Elemento para mostrar el título del video

// Inicializar los manejadores de eventos después de cargar el DOM

// Buscar transcripciones que contienen una palabra
async function buscar() {
  const palabra = document.getElementById("busqueda").value.trim();
  
  if (!palabra) {
    mostrarPopup("Por favor introduce una palabra para buscar");
    return;
  }

  try {
    // Mostrar indicador de carga
    mostrarCargando(true);
    
    // Realizar la petición al servidor
    const res = await fetch(`http://127.0.0.1:8000/buscar?palabra=${palabra}`);
    const data = await res.json();
    
    // Ocultar cargador y reproductor
    mostrarCargando(false);
    ocultarReproductor();
    
    // Mostrar resultados
    mostrarResultadosBusqueda(data.resultados);
  } catch (error) {
    mostrarCargando(false);
    console.error("Error al buscar:", error);
    mostrarPopup("Error de conexión con el servidor");
  }
}

// Mostrar/ocultar indicador de carga
function mostrarCargando(mostrar) {
  document.getElementById("loading").style.display = mostrar ? "flex" : "none";
}

// Ocultar el reproductor y controles de video
function ocultarReproductor() {
  videoPlayer.style.display = "none";
  document.getElementById("video-control-container").style.display = "none";
}

// Mostrar resultados de búsqueda
function mostrarResultadosBusqueda(resultados) {
  const resultadosDiv = document.getElementById("resultados");
  resultadosDiv.innerHTML = "";
  
  if (resultados && resultados.length > 0) {
    resultados.forEach((resultado, idx) => {
      const box = document.createElement("div");
      box.className = "transcription-box";
      box.innerHTML = `
        <div class="transcription-title">Resultado ${idx+1} - ${resultado.timestamp}</div>
        <div class="transcription-text">${resultado.texto}</div>
      `;
      box.addEventListener("click", () => mostrarVideo(resultado));
      resultadosDiv.appendChild(box);
    });
    mostrarPopup(`Se encontraron ${resultados.length} resultados`);
  } else {
    resultadosDiv.innerHTML = "<p style='text-align:center'>No se encontraron resultados</p>";
    mostrarPopup("No se encontraron resultados");
  }
}

// Mostrar el video seleccionado con su transcripción
function mostrarVideo(resultado) {
  // Resetear estado
  console.log("mostrarVideo llamado con resultado:", resultado);
  videoActual = resultado.video;
  acumuladosAtras = 0;
  acumuladosAdelante = 0;
  
  // Limpiar resultados de búsqueda
  document.getElementById("resultados").innerHTML = "";
  
  // Verificar que el video existe
  console.log(`mostrarVideo: videoActual=${videoActual}`);
  console.log(`mostrarVideo: listaVideos=${JSON.stringify(listaVideos)}`);
  
  if (!listaVideos.includes(videoActual)) {
    console.error(`El video ${videoActual} no existe en la lista de videos disponibles`);
    mostrarPopup("El video no existe en el servidor");
    return;
  }
  
  console.log(`mostrarVideo: Video existe en la lista, índice: ${listaVideos.indexOf(videoActual)}`);
  

  // Configurar el reproductor de video
  configurarReproductor(resultado);
  
  // Mostrar la transcripción seleccionada
  mostrarTranscripcion(resultado);
  
  // Mostrar controles de video y actualizar interfaz
  document.getElementById("video-control-container").style.display = "block";
  videoPlayer.style.display = "flex";
  actualizarContador();
  
  // Desplazarse al reproductor
  videoPlayer.scrollIntoView({ behavior: 'smooth' });
}

// Configurar el reproductor de video
function configurarReproductor(resultado) {
  // Usar directamente el nombre del archivo sin considerar subcarpetas
  videoSrc.src = "./videos/" + resultado.video;
  videoElement.load();
  
  videoElement.onloadedmetadata = () => {
    // Siempre iniciar el video desde el segundo 0
    videoElement.currentTime = 0;
    // Intentar reproducción automática
    videoElement.play().catch(e => console.log("Reproducción automática bloqueada por el navegador"));
  };
  
  // Título simple con el nombre del archivo
  videoTitle.textContent = `Reproduciendo: ${resultado.video}`;
  
  /* 
  // Código comentado para cuando se quiera usar la extracción de información del nombre del archivo
  const videoInfo = extraerInfoVideo(resultado.video);
  videoTitle.textContent = `Reproduciendo: ${videoInfo.canal} - ${videoInfo.nombreCorto}`;
  */
}

// Mostrar la transcripción seleccionada
function mostrarTranscripcion(resultado) {
  const transcripcionDiv = document.getElementById("selected-transcription");
  transcripcionDiv.innerHTML = `
    <div class="selected-transcription-title">Transcripción seleccionada</div>
    <div class="selected-transcription-text">${resultado.texto}</div>
    <div class="selected-transcription-info">
      <p><strong>Fecha:</strong> ${resultado.timestamp}</p>
      <p><strong>Video:</strong> ${resultado.video}</p>
      <p><strong>Posición:</strong> ${formatTime(resultado.segundo_inicio || 0)}</p>
    </div>
    <button id="btnNuevaBusqueda" class="btn-secondary">Nueva búsqueda</button>
  `;
  
  /* 
  // Código comentado para cuando se quiera usar la información extraída del nombre del archivo
  const videoInfo = extraerInfoVideo(resultado.video);
  transcripcionDiv.innerHTML = `
    <div class="selected-transcription-title">Transcripción seleccionada</div>
    <div class="selected-transcription-text">${resultado.texto}</div>
    <div class="selected-transcription-info">
      <p><strong>Fecha:</strong> ${resultado.timestamp}</p>
      <p><strong>Canal:</strong> ${videoInfo.canal}</p>
      <p><strong>Video:</strong> ${videoInfo.nombreCorto}</p>
      <p><strong>Fecha video:</strong> ${videoInfo.fecha}</p>
    </div>
    <button id="btnNuevaBusqueda" class="btn-secondary">Nueva búsqueda</button>
  `;
  */
  
  // Configurar botón de nueva búsqueda
  document.getElementById("btnNuevaBusqueda").addEventListener("click", () => {
    ocultarReproductor();
    document.getElementById("busqueda").focus();
  });
}

// Función para formatear segundos en formato mm:ss
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/*
// Función comentada para uso futuro - Extraer información de la ruta del video con la nueva estructura
function extraerInfoVideo(rutaVideo) {
  // Ejemplo de ruta: a24/a24_20250905_234106_20250905_234236.ts
  
  // Extraer el canal (nombre de la carpeta)
  const partes = rutaVideo.split('/');
  const canal = partes.length > 1 ? partes[0] : 'Desconocido';
  
  // Extraer el nombre del archivo sin la carpeta
  const nombreArchivo = partes[partes.length - 1];
  
  // Intentar extraer la fecha del nombre del archivo
  let fecha = 'Desconocida';
  
  const patronFecha = /(\d{8})_(\d{6})/;
  const coincidencias = nombreArchivo.match(patronFecha);
  
  if (coincidencias && coincidencias.length >= 3) {
    // Formatear la fecha: AAAAMMDD a DD/MM/AAAA
    const fechaStr = coincidencias[1];
    if (fechaStr.length === 8) {
      const año = fechaStr.substring(0, 4);
      const mes = fechaStr.substring(4, 6);
      const día = fechaStr.substring(6, 8);
      fecha = `${día}/${mes}/${año}`;
      
      // Añadir hora si está disponible
      const hora = coincidencias[2];
      if (hora.length === 6) {
        const h = hora.substring(0, 2);
        const m = hora.substring(2, 4);
        const s = hora.substring(4, 6);
        fecha += ` ${h}:${m}:${s}`;
      }
    }
  }
  
  return {
    canal: canal,
    nombreCompleto: nombreArchivo,
    nombreCorto: nombreArchivo.length > 25 ? nombreArchivo.substring(0, 22) + '...' : nombreArchivo,
    fecha: fecha
  };
}
*/

// Función simple para obtener el nombre del archivo sin procesar
function extraerInfoVideo(rutaVideo) {
  return {
    canal: 'N/A',
    nombreCompleto: rutaVideo,
    nombreCorto: rutaVideo,
    fecha: 'N/A'
  };
}

// Ajustar la posición del video en segundos
function ajustarClip(segundos) {
  if (!videoElement) return;
  videoElement.currentTime += segundos;
}

// Expandir la selección de videos hacia atrás o adelante
function expandir(direccion, lado) {
  const idx = listaVideos.indexOf(videoActual);
  console.log(`expandir: videoActual=${videoActual}, idx=${idx}, listaVideos.length=${listaVideos.length}`);
  
  if (idx === -1) {
    console.error(`Video actual "${videoActual}" no encontrado en listaVideos`);
    mostrarPopup("Error: Video no encontrado");
    return;
  }
  
  // Variables según el lado (atrás o adelante)
  const esAtras = lado === "atras";
  const maximoPermitido = 3;  // Máximo 3 videos adicionales en cada dirección
  
  // Verificar cuántos videos disponibles hay en cada dirección
  const disponiblesAtras = idx;
  const disponiblesAdelante = listaVideos.length - idx - 1;
  
  console.log(`expandir: disponibles atrás=${disponiblesAtras}, disponibles adelante=${disponiblesAdelante}`);
  
  if (direccion === 1) { // Agregar video
    // Cuántos videos ya están seleccionados en la dirección correspondiente
    const seleccionados = esAtras ? acumuladosAtras : acumuladosAdelante;
    
    // Cuántos videos máximos se pueden seleccionar (el mínimo entre maximoPermitido y los disponibles)
    const maximoPosible = Math.min(maximoPermitido, esAtras ? disponiblesAtras : disponiblesAdelante);
    
    console.log(`expandir: ya seleccionados=${seleccionados}, máximo posible=${maximoPosible}`);
    
    if (seleccionados < maximoPosible) {
      // Todavía podemos agregar más videos
      if (esAtras) {
        acumuladosAtras++;
      } else {
        acumuladosAdelante++;
      }
      mostrarPopup(`Se agregó un video ${lado}`);
    } else if (seleccionados >= maximoPermitido) {
      // Ya alcanzamos el límite máximo permitido
      mostrarPopup(`Máximo ${maximoPermitido} videos ${lado}`);
    } else {
      // Ya no hay más videos disponibles en esa dirección
      mostrarPopup(`No hay más videos ${lado}`);
    }
  } else { // Quitar video
    if ((esAtras ? acumuladosAtras : acumuladosAdelante) > 0) {
      if (esAtras) {
        acumuladosAtras--;
      } else {
        acumuladosAdelante--;
      }
      mostrarPopup(`Se quitó un video ${lado}`);
    } else {
      mostrarPopup(`No hay más videos ${lado}`);
    }
  }
  
  actualizarContador();
}

// Actualizar el contador de videos seleccionados
function actualizarContador() {
  document.getElementById("contador").textContent =
    `${acumuladosAtras} atrás | ${acumuladosAdelante} adelante`;
}

// Mostrar un mensaje emergente temporal
function mostrarPopup(mensaje) {
  const popup = document.getElementById("popup");
  if (!popup) {
    console.error("Elemento popup no encontrado");
    alert(mensaje); // Fallback a alert
    return;
  }
  
  // Configurar el popup
  popup.textContent = mensaje;
  popup.style.display = "block";
  
  // Limpiar temporizador anterior si existe
  if (popup.timeoutId) {
    clearTimeout(popup.timeoutId);
  }
  
  // Ocultar automáticamente después de 3 segundos
  popup.timeoutId = setTimeout(() => {
    popup.style.display = "none";
  }, 3000);
}

// Descargar el video concatenado
async function descargarConcatenado() {
  // Verificar que hay un video seleccionado
  if (!videoActual) {
    console.error("Error: No hay video seleccionado");
    mostrarPopup("No hay video seleccionado");
    return;
  }

  console.log(`descargarConcatenado: videoActual=${videoActual}, acumuladosAtras=${acumuladosAtras}, acumuladosAdelante=${acumuladosAdelante}`);

  // Obtener el índice del video actual
  const idx = listaVideos.indexOf(videoActual);
  console.log(`descargarConcatenado: índice de videoActual en listaVideos: ${idx}`);
  
  if (idx === -1) {
    console.error(`Error: Video "${videoActual}" no encontrado en la lista de videos`);
    mostrarPopup("Video no encontrado en la lista");
    return;
  }

  // Seleccionar los videos a concatenar
  const inicio = Math.max(0, idx - acumuladosAtras);
  const fin = Math.min(listaVideos.length - 1, idx + acumuladosAdelante);
  console.log(`descargarConcatenado: inicio=${inicio}, fin=${fin}, listaVideos.length=${listaVideos.length}`);
  
  // Crear una copia ordenada de los videos seleccionados
  const seleccion = listaVideos.slice(inicio, fin + 1);
  
  // Aseguramos que estamos enviando todos los videos en orden, incluyendo el video actual
  console.log(`descargarConcatenado: videos seleccionados=${JSON.stringify(seleccion)}`);
  
  // Comprobar si video_1 está incluido cuando debe estarlo
  if (inicio === 0 && !seleccion.includes("video_1.mp4") && listaVideos.includes("video_1.mp4")) {
    console.warn("Video_1 debería estar incluido pero no lo está, verificando lista completa de videos...");
  }
  
  if (seleccion.length === 0) {
    console.error("Error: No hay videos para concatenar");
    mostrarPopup("No hay videos para concatenar");
    return;
  }

  // Actualizar interfaz para mostrar progreso
  const downloadStatus = document.getElementById("download-status");
  const btnDescargar = document.getElementById("btnDescargar");
  const btnTextoOriginal = btnDescargar.textContent;
  
  // Mostrar detalle de videos seleccionados
  const videoInfo = {
    videoActual: videoActual,
    indiceActual: idx,
    acumuladosAtras: acumuladosAtras,
    acumuladosAdelante: acumuladosAdelante,
    indiceInicio: inicio,
    indiceFin: fin,
    seleccion: seleccion
  };
  console.log("Detalle de concatenación:", videoInfo);
  
  // Preparar la interfaz para la operación
  mostrarCargando(true);
  actualizarEstadoDescarga("Concatenando videos...", "normal");
  deshabilitarBotonDescarga(true, "Procesando...");
  mostrarPopup(`Procesando ${seleccion.length} videos...`);
  
  try {
    // Enviar petición para concatenar videos
    console.log("Enviando videos para concatenar:", seleccion);
    const res = await fetch("http://127.0.0.1:8000/concatenar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ videos: seleccion })
    });

    // Restaurar interfaz
    mostrarCargando(false);
    deshabilitarBotonDescarga(false, btnTextoOriginal);

    // Manejar errores
    if (!res.ok) {
      manejarErrorDescarga(res);
      return;
    }

    // Descargar archivo
    actualizarEstadoDescarga("Descargando archivo...", "normal");
    await descargarArchivo(res);
    
    // Mostrar finalización
    mostrarPopup("Descarga iniciada");
    actualizarEstadoDescarga("Descarga completada", "success");
    
    // Ocultar mensaje de estado después de un tiempo
    setTimeout(() => {
      downloadStatus.style.display = "none";
    }, 5000);
    
  } catch (error) {
    // Restaurar interfaz en caso de error
    mostrarCargando(false);
    deshabilitarBotonDescarga(false, btnTextoOriginal);
    actualizarEstadoDescarga("Error en la descarga", "error");
    mostrarPopup("Error en la descarga");
    console.error(error);
  }
}

// Actualizar el estado de la descarga
function actualizarEstadoDescarga(mensaje, tipo) {
  const downloadStatus = document.getElementById("download-status");
  downloadStatus.textContent = mensaje;
  downloadStatus.style.display = "block";
  
  // Establecer color según tipo
  if (tipo === "error") {
    downloadStatus.style.color = "#ff5757";
  } else if (tipo === "success") {
    downloadStatus.style.color = "#4caf50";
  } else {
    downloadStatus.style.color = "#fff";
  }
}

// Deshabilitar/habilitar botón de descarga
function deshabilitarBotonDescarga(deshabilitar, texto) {
  const btnDescargar = document.getElementById("btnDescargar");
  btnDescargar.textContent = texto;
  btnDescargar.disabled = deshabilitar;
}

// Manejar error en la descarga
function manejarErrorDescarga(respuesta) {
  respuesta.json()
    .catch(() => ({}))
    .then(errorData => {
      console.error("Error del servidor:", errorData);
      mostrarPopup(`Error al generar clip: ${respuesta.status} ${respuesta.statusText}`);
      actualizarEstadoDescarga("Error en la concatenación", "error");
    });
}

// Descargar el archivo
async function descargarArchivo(respuesta) {
  const blob = await respuesta.blob();
  const url = window.URL.createObjectURL(blob);

  // Crear elemento para descarga
  const enlaceDescarga = document.createElement("a");
  enlaceDescarga.style.display = "none";
  enlaceDescarga.href = url;
  enlaceDescarga.download = "clip_concatenado.mp4";
  
  // Iniciar descarga
  document.body.appendChild(enlaceDescarga);
  enlaceDescarga.click();
  document.body.removeChild(enlaceDescarga);
  
  // Liberar URL
  window.URL.revokeObjectURL(url);
}

// Inicialización de la aplicación cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', async () => {
  // Inicializar referencias a elementos DOM frecuentemente usados
  inicializarReferenciasDOM();
  
  // Configurar todos los eventos de la aplicación
  configurarEventos();

  // Cargar la lista de videos desde el servidor -> Lo mejor sería no cargar toda la lista, sino hacerlo a pedido
  
});

// Inicializar referencias a elementos del DOM
function inicializarReferenciasDOM() {
  videoPlayer = document.getElementById("video-player");
  videoElement = document.getElementById("video");
  videoSrc = document.getElementById("video-src");
  videoTitle = document.getElementById("video-title");
  
  // Ocultar controles de video inicialmente
  document.getElementById("video-control-container").style.display = "none";
}

// Configurar todos los eventos de la aplicación
function configurarEventos() {
  // Evento de búsqueda
  document.getElementById("btnBuscar").addEventListener("click", buscar);
  
  // Eventos de control de video
  document.getElementById("btnMenos15").addEventListener("click", () => ajustarClip(-15));
  document.getElementById("btnMas15").addEventListener("click", () => ajustarClip(15));
  
  // Eventos para selección de videos
  document.getElementById("menosAtras").addEventListener("click", () => expandir(-1, "atras"));
  document.getElementById("masAtras").addEventListener("click", () => expandir(1, "atras"));
  document.getElementById("menosAdelante").addEventListener("click", () => expandir(-1, "adelante"));
  document.getElementById("masAdelante").addEventListener("click", () => expandir(1, "adelante"));
  
  // Evento de descarga
  document.getElementById("btnDescargar").addEventListener("click", descargarConcatenado);
  
  // Permitir búsqueda con tecla Enter
  document.getElementById("busqueda").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      document.getElementById("btnBuscar").click();
    }
  });
}
