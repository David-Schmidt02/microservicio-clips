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

## Estructura del Proyecto

```
microservicio-clips/
│
├── main.py                    # Servidor backend con FastAPI
├── index.html                 # Estructura HTML de la interfaz
├── script.js                  # Lógica de frontend en JavaScript
├── style.css                  # Estilos CSS
├── videos/                    # Directorio con videos originales
└── clips/                     # Directorio para guardar videos concatenados
```

## Flujo de Trabajo Detallado

### 1. Inicialización

Cuando el usuario abre la aplicación en el navegador:

1. **Carga de la página**: Se inicializa la interfaz de usuario.
2. **Inicialización del sistema**:
   - Se establecen referencias a elementos DOM importantes
   - Se configuran manejadores de eventos para botones y controles
   - Se carga la lista de videos disponibles desde el servidor

### 2. Búsqueda de Transcripciones

1. **Entrada del usuario**: El usuario escribe una palabra en el campo de búsqueda y hace clic en "Buscar".
2. **Proceso de búsqueda**:
   - Se muestra un indicador de carga
   - Se envía la consulta al servidor vía API
   - El servidor busca la palabra en las transcripciones de todos los videos
3. **Visualización de resultados**:
   - Se oculta el indicador de carga
   - Se muestran los resultados como cajas clickeables con fragmentos de texto
   - Cada resultado incluye información sobre el video y el contexto donde apareció la palabra

### 3. Selección y Visualización de Video

1. **Selección del usuario**: El usuario hace clic en un resultado de búsqueda.
2. **Preparación del video**:
   - Se ocultan los resultados de búsqueda
   - Se configura el reproductor de video con la ruta del archivo correspondiente
   - Se establece el video actual como punto de referencia
   - Se inicializa el video para comenzar desde el segundo 0
3. **Visualización**:
   - Se muestra el reproductor de video en pantalla
   - Se muestra la transcripción seleccionada a la derecha
   - Se muestran los controles para manipular el video

### 4. Manipulación del Video

Una vez que el usuario está viendo un video, puede:

1. **Navegar dentro del video**:
   - Botón "-15s": Retroceder 15 segundos
   - Botón "+15s": Avanzar 15 segundos
   
2. **Seleccionar videos adicionales**:
   - Botones "+/-" para "Atrás": Añadir/quitar hasta 3 videos anteriores al actual
   - Botones "+/-" para "Adelante": Añadir/quitar hasta 3 videos posteriores al actual
   
3. **Ver detalles de la transcripción**:
   - Texto completo de la transcripción
   - Información sobre el video (nombre, fecha)

### 5. Concatenación y Descarga

1. **Inicio del proceso**:
   - El usuario hace clic en "Descargar clip concatenado"
   - Se muestra un indicador de carga
   - Se actualiza el estado de la operación en la interfaz
   
2. **Proceso en el servidor**:
   - Se envía al servidor la lista de videos a concatenar
   - El servidor utiliza FFmpeg para concatenar los videos
   - Se genera un nuevo archivo con el resultado
   
3. **Finalización**:
   - El navegador recibe el archivo concatenado
   - Se inicia automáticamente la descarga
   - Se muestra un mensaje de éxito o error

### 6. Nueva Búsqueda

- El usuario puede hacer clic en "Nueva búsqueda" para volver al estado inicial
- Se oculta el reproductor y se enfoca el campo de búsqueda

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