import { buscarCoincidenciasElastic } from "./api.js";
import { state } from "./state.js";
import { mostrarCargando, mostrarPopup, } from "./utils.js";
import { initDOMRefs, ocultarReproductor, renderResultados, } from "./ui.js";
import { mostrarVideo, ajustarClip, expandir, descargarConcatenado } from "./player.js";

// === BÚSQUEDA ===
async function buscar() {
  const palabra = document.getElementById("busqueda").value.trim();
  if (!palabra) {
    mostrarPopup("Por favor introduce una palabra para buscar");
    return;
  }

  try {
    mostrarCargando(true);
    const data = await buscarCoincidenciasElastic(palabra);
    mostrarCargando(false);
    ocultarReproductor(); // data.resultados = transcripciones que matchean con las palabras
    renderResultados(data.resultados, mostrarVideo); // onClick -> mostrarVideo
    mostrarPopup(`Se encontraron ${data.resultados?.length || 0} resultados`);
  } catch (e) {
    mostrarCargando(false);
    console.error("Error al buscar:", e);
    mostrarPopup("Error de conexión con el servidor");
  }
}

// === INIT ===
document.addEventListener("DOMContentLoaded", () => {
  // DOM refs
  initDOMRefs();

  // Eventos UI
  // Busqueda con click o enter
  document.getElementById("btnBuscar").addEventListener("click", buscar);
  document.getElementById("busqueda").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      buscar();
    }
  });
// Podemos aprovechar esta funcion en el futuro con un expandir distinto
  //document.getElementById("btnMenos15").addEventListener("click", () => ajustarClip(-15));
  //document.getElementById("btnMas15").addEventListener("click", () => ajustarClip(15));
  /*
  document.getElementById("menosAtras").addEventListener("click", () => expandir(-1, "atras"));
  document.getElementById("masAtras").addEventListener("click", () => expandir(1, "atras"));
  document.getElementById("menosAdelante").addEventListener("click", () => expandir(-1, "adelante"));
  document.getElementById("masAdelante").addEventListener("click", () => expandir(1, "adelante"));
  */


  document.getElementById("btnDescargar").addEventListener("click", descargarConcatenado);


});
