# Microservicio de Clips de Video

Este proyecto es un microservicio para buscar, reproducir y concatenar clips de video basados en transcripciones. Permite a los usuarios buscar palabras específicas dentro de transcripciones de videos y luego seleccionar segmentos para concatenarlos en un nuevo clip personalizado.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Flujo de Trabajo Detallado](#flujo-de-trabajo-detallado)
- [Frontend: Interfaz de Usuario](#frontend-interfaz-de-usuario)
- [Backend: API y Procesamiento de Videos](#backend-api-y-procesamiento-de-videos)
- [Funciones JavaScript Principales](#funciones-javascript-principales)
- [API Endpoints](#api-endpoints)
- [Instalación y Configuración](#instalación-y-configuración)
- [Requisitos](#requisitos)

## Descripción General

El microservicio permite a los usuarios:
- Buscar palabras dentro de transcripciones de video
- Visualizar los segmentos donde aparecen esas palabras
- Reproducir los videos correspondientes
- Seleccionar videos adicionales antes o después del segmento encontrado
- Concatenar y descargar clips personalizados

microservicio-clips/
│

## Estructura del Proyecto

```
microservicio-clips/
│
├── main.py
├── index.html
├── README.md
├── .gitignore
│
├── videos/                  # Videos originales
├── clips/                   # Clips concatenados
│
├── css/
│   ├── main.css
│   ├── base/
│   │   └── base.css
│   ├── components/
│   │   ├── buttons.css
│   │   ├── cards.css
│   │   ├── channel.css
│   │   ├── loading.css
│   │   ├── modal.css
│   │   ├── player.css
│   │   ├── popup.css
│   │   ├── search.css
│   │   └── status.css
│   ├── layout/
│   │   └── layout.css
│   ├── pages/
│   │   └── search.css
│   ├── settings/
│   │   └── variables.css
│   └── utilities/
│       └── animations.css
│
├── js/
│   ├── api.js
│   ├── main.js
│   ├── player.js
│   ├── state.js
│   ├── ui.js
│   └── utils.js
│
```

---

## Descripción de las carpetas principales

### css/
- **main.css**: Importa y centraliza los estilos globales.
- **base/**: Estilos base y resets.
- **components/**: Estilos de componentes reutilizables (botones, tarjetas, modales, reproductor, etc).
- **layout/**: Estilos de estructura y disposición general.
- **pages/**: Estilos específicos por página.
- **settings/**: Variables CSS y tokens de diseño.
- **utilities/**: Utilidades y animaciones.

### js/
- **api.js**: Funciones para interactuar con el backend (fetch, endpoints).
- **main.js**: Punto de entrada, inicialización y lógica principal.
- **player.js**: Lógica del reproductor de video y controles relacionados.
- **state.js**: Manejo del estado global de la aplicación.
- **ui.js**: Renderizado y manipulación del DOM, ventanas modales, resultados, etc.
- **utils.js**: Funciones utilitarias y helpers generales.

---



## Flujo de Trabajo Detallado

### 1. Inicialización

Al abrir la aplicación:
- Se cargan los estilos y scripts principales.
- Se inicializan referencias a elementos del DOM y eventos de UI.
- Se obtiene la lista de videos disponibles desde el backend.

### 2. Búsqueda de Transcripciones

- El usuario ingresa una palabra y presiona Enter o hace clic en "Buscar".
- Se muestra un loader mientras se consulta el backend.
- Se muestran los resultados como tarjetas agrupadas por canal.

### 3. Selección y Visualización de Video

- Al hacer clic en un resultado, se muestra el reproductor con el video y la transcripción.
- Se pueden ver detalles del video y del canal.

### 4. Manipulación del Video

- Controles para avanzar/retroceder 15 segundos.
- Botones para agregar/quitar videos anteriores o siguientes (máx. 3 en cada dirección).
- Contador visual de la selección.

### 5. Concatenación y Descarga

- El usuario puede descargar un clip concatenado con la selección actual.
- El backend procesa la solicitud y devuelve el archivo listo para descargar.

### 6. Nueva Búsqueda

- El usuario puede volver a buscar y reiniciar el flujo en cualquier momento.

## Frontend: Interfaz de Usuario

La interfaz de usuario está compuesta por:

### Elementos de Búsqueda
- Campo de texto para ingresar palabras a buscar
- Botón "Buscar"
- Indicador de carga
- Contenedor para resultados de búsqueda

### Reproductor de Video
- Elemento `<video>` de HTML5 
- Título del video actual
- Controles de navegación (-15s, +15s)
- Botones para seleccionar videos adicionales
- Contador de videos seleccionados
- Botón para descargar el clip concatenado

### Panel de Transcripción
- Texto de la transcripción seleccionada
- Información sobre el video
- Botón "Nueva búsqueda"

### Notificaciones
- Popup temporal para mostrar mensajes al usuario

## Backend: API y Procesamiento de Videos

El backend, implementado en Python con FastAPI, proporciona:

### Gestión de Videos
- Listado de videos disponibles
- Búsqueda en transcripciones
- Concatenación de clips con FFmpeg

### API RESTful
- Endpoints para todas las operaciones necesarias
- Manejo de errores y excepciones
- Respuestas en formato JSON

### Procesamiento de Archivos
- Creación de archivos temporales para FFmpeg
- Manejo seguro de rutas de archivos
- Limpieza de archivos temporales

## Funciones JavaScript Principales

### Inicialización
- `inicializarReferenciasDOM()`: Obtiene referencias a elementos HTML importantes
- `configurarEventos()`: Configura manejadores de eventos para los controles
- `initVideos()`: Carga la lista de videos desde el servidor

### Búsqueda y Visualización
- `buscar()`: Envía la consulta de búsqueda al servidor y muestra resultados
- `mostrarResultadosBusqueda()`: Crea elementos HTML para cada resultado
- `mostrarVideo()`: Configura y muestra el reproductor con el video seleccionado
- `configurarReproductor()`: Prepara el elemento de video para reproducción
- `mostrarTranscripcion()`: Muestra la transcripción seleccionada

### Manipulación de Videos
- `ajustarClip()`: Cambia la posición de reproducción del video
- `expandir()`: Añade o quita videos adicionales antes o después del actual
- `actualizarContador()`: Actualiza el texto que muestra cuántos videos están seleccionados

### Concatenación y Descarga
- `descargarConcatenado()`: Envía la lista de videos al servidor y maneja la descarga
- `actualizarEstadoDescarga()`: Actualiza el mensaje de estado durante el proceso
- `descargarArchivo()`: Inicia la descarga del archivo resultante

### Utilidades
- `mostrarPopup()`: Muestra mensajes emergentes temporales
- `mostrarCargando()`: Controla la visibilidad del indicador de carga
- `formatTime()`: Convierte segundos a formato mm:ss

## API Endpoints

### Listado de Videos
```
GET /videos
```
Devuelve una lista de todos los videos disponibles en el sistema.

### Búsqueda en Transcripciones
```
GET /buscar?palabra=<texto>
```
Busca la palabra especificada en todas las transcripciones y devuelve los resultados.

### Concatenación de Videos
```
POST /concatenar
Body: { "videos": ["video1.mp4", "video2.mp4", ...] }
```
Concatena los videos especificados y devuelve el archivo resultante.

## Instalación y Configuración

### Requisitos Previos
- Python 3.6+
- FFmpeg instalado y disponible en el PATH
- Navegador web moderno

### Pasos de Instalación

1. **Clonar el repositorio**
   ```
   git clone https://github.com/David-Schmidt02/microservicio-clips.git
   cd microservicio-clips
   ```

2. **Instalar dependencias de Python**
   ```
   pip install fastapi uvicorn python-multipart ffmpeg-python
   ```

3. **Verificar instalación de FFmpeg**
   ```
   ffmpeg -version
   ```

4. **Iniciar el servidor**
   ```
   uvicorn main:app --reload
   ```

5. **Acceder a la aplicación**
   
   Abrir un navegador y visitar: http://127.0.0.1:8000

## Requisitos

- **Frontend**: Navegador moderno con soporte para HTML5, CSS3 y JavaScript ES6+
- **Backend**: Python 3.6+, FastAPI, Uvicorn
- **Procesamiento de Video**: FFmpeg

## Funcionalidad detallada de script.js

El archivo `script.js` contiene toda la lógica del frontend y se organiza de la siguiente manera:

### Variables Globales
- `listaVideos`: Array con los nombres de todos los videos disponibles
- `videoActual`: Nombre del video seleccionado actualmente
- `acumuladosAtras`, `acumuladosAdelante`: Contadores de videos seleccionados en cada dirección
- Referencias a elementos DOM frecuentes: `videoPlayer`, `videoElement`, `videoSrc`, `videoTitle`

### Flujo de Ejecución

1. **Inicialización**:
   ```javascript
   document.addEventListener('DOMContentLoaded', async () => {
     inicializarReferenciasDOM();
     configurarEventos();
     await initVideos();
   });
   ```
   - Se ejecuta cuando el DOM está completamente cargado
   - Obtiene referencias a elementos DOM importantes
   - Configura todos los eventos de click y otros
   - Carga la lista de videos desde el servidor

2. **Proceso de Búsqueda**:
   ```javascript
   async function buscar() {
     const palabra = document.getElementById("busqueda").value;
     // Muestra indicador de carga
     // Realiza petición al servidor
     // Muestra resultados o error
   }
   ```
   - Se activa cuando el usuario hace clic en "Buscar"
   - Muestra resultados como cajas clickeables
   - Cada caja activa la función `mostrarVideo()` cuando se hace clic

3. **Selección de Video**:
   ```javascript
   function mostrarVideo(resultado) {
     videoActual = resultado.video;
     // Configura el reproductor
     // Muestra controles y transcripción
   }
   ```
   - Establece el video actual y resetea contadores
   - Configura y muestra el reproductor y controles
   - Muestra la transcripción seleccionada

4. **Manipulación**:
   ```javascript
   function expandir(direccion, lado) {
     // Añade o quita videos hacia adelante o atrás
     // Actualiza contadores
   }
   ```
   - Gestiona la selección de videos adicionales
   - Mantiene control de límites (máximo 3 en cada dirección)
   - Actualiza la interfaz de usuario

5. **Concatenación**:
   ```javascript
   async function descargarConcatenado() {
     // Selecciona videos según contadores
     // Envía petición al servidor
     // Maneja la descarga o error
   }
   ```
   - Determina qué videos concatenar según la selección
   - Envía la solicitud al servidor
   - Maneja la descarga del archivo resultante

### Interconexión entre Funciones

El flujo de información entre funciones es:

```
DOMContentLoaded → inicializarReferenciasDOM() + configurarEventos() + initVideos()
    |
    ↓
[btnBuscar clic] → buscar() → mostrarResultadosBusqueda()
    |
    ↓
[resultado clic] → mostrarVideo() → configurarReproductor() + mostrarTranscripcion()
    |
    ↓
[btnMenos15/btnMas15] → ajustarClip()
    |
[+/- atrás/adelante] → expandir() → actualizarContador()
    |
    ↓
[btnDescargar] → descargarConcatenado() → descargarArchivo()
    |
    ↓
[btnNuevaBusqueda] → ocultarReproductor()
```

Esta documentación detallada debería ayudarte a entender mejor el funcionamiento del código JavaScript, especialmente si necesitas revisarlo en detalle mañana.