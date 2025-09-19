import { buscarCoincidenciasElastic } from "./api.js";
import { mostrarCargando, mostrarPopup } from "./utils.js";
import { initDOMRefs, ocultarReproductor, renderResultados } from "./ui.js";
import { mostrarVideo, expandir, descargarConcatenado } from "./player.js";

async function buscar() {
  const input = document.getElementById("busqueda");
  if (!input) return;
  const palabra = input.value.trim();
  if (!palabra) {
    mostrarPopup("Por favor introduce una palabra para buscar");
    return;
  }

  try {
    mostrarCargando(true);
    const data = await buscarCoincidenciasElastic(palabra);
    mostrarCargando(false);
    ocultarReproductor();
    renderResultados(data.resultados, mostrarVideo);
    mostrarPopup(`Se encontraron ${data.resultados?.length || 0} resultados`);
  } catch (e) {
    mostrarCargando(false);
    console.error("Error al buscar:", e);
    mostrarPopup("Error de conexion con el servidor");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initDOMRefs();

  const btnBuscar = document.getElementById("btnBuscar");
  if (btnBuscar) btnBuscar.addEventListener("click", buscar);

  const inputBusqueda = document.getElementById("busqueda");
  if (inputBusqueda) {
    inputBusqueda.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        buscar();
      }
    });
  }

  const botonesExpandir = [
    ["menosAtras", -1, "atras"],
    ["masAtras", 1, "atras"],
    ["menosAdelante", -1, "adelante"],
    ["masAdelante", 1, "adelante"],
  ];

  botonesExpandir.forEach(([id, direccion, lado]) => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener("click", () => expandir(direccion, lado));
    }
  });

  const btnDescargar = document.getElementById("btnDescargar");
  if (btnDescargar) btnDescargar.addEventListener("click", descargarConcatenado);
});
