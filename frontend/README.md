# Frontend - Buscador de Transcripciones

## 📋 Descripción
Interfaz web para buscar transcripciones de video. Construida con HTML, CSS y JavaScript vanilla.

## 🗂️ Estructura
```
frontend/
├── index.html      # Página principal
├── css/           # Estilos
└── js/            # JavaScript modules
    ├── main.js    # Punto de entrada
    ├── api.js     # Comunicación con backend
    ├── ui.js      # Manipulación de DOM
    ├── player.js  # Reproductor de video
    ├── state.js   # Estado de la app
    └── utils.js   # Utilidades
```

## � Responsabilidades

- **`api.js`**: Peticiones HTTP al backend
- **`ui.js`**: Manipular DOM, mostrar datos
- **`state.js`**: Estado global de la aplicación
- **`player.js`**: Control del reproductor
- **`main.js`**: Coordina todos los módulos

## � Desarrollo

```bash
# Levantar el frontend
python -m http.server 8080

# Configurar backend en api.js
const CONFIG = { API_BASE_URL: "http://127.0.0.1:8000" };
```

**Ver [API-COMMUNICATION.md](./API-COMMUNICATION.md) para endpoints del backend.**