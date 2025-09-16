transcripciones = [
    {
        "id": 1,
        "texto": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua lorem."*10,
        "timestamp": "2025-09-13T10:00:00",
        "video": "video_1.mp4",
        "canal": "TN",
    },
    {
        "id": 2,
        "texto": "Aquí aparece la palabra Python en una transcripción de prueba sobre APIs y microservicios, lorem ipsum dolor sit amet."*5,
        "timestamp": "2025-09-13T10:01:30",
        "video": "video_2.mp4",
        "canal": "C5N",
    },
    {
        "id": 3,
        "texto": "Este es otro ejemplo donde mencionamos microservicios y bases de datos distribuidas para escalabilidad, lorem ipsum dolor sit."*20,
        "timestamp": "2025-09-13T10:03:00",
        "video": "video_3.mp4",
        "canal": "LN+",
    },
    {
        "id": 4,
        "texto": "La inteligencia artificial se integra con buscadores y motores de bases de datos para análisis, lorem ipsum dolor sit amet."*5,
        "timestamp": "2025-09-13T10:05:00",
        "video": "video_4.mp4",
        "canal": "TN",
    },
    {
        "id": 5,
        "texto": "Python y microservicios: buenas prácticas para escalar APIs y manejar concurrencia, lorem ipsum dolor sit amet consectetur."*5,
        "timestamp": "2025-09-13T10:07:10",
        "video": "video_5.mp4",
        "canal": "C5N",
    },
    {
        "id": 6,
        "texto": "Microservicios, colas y bases de datos distribuidas forman la base de arquitectura cloud moderna, lorem ipsum dolor sit amet."*5,
        "timestamp": "2025-09-13T10:09:30",
        "video": "video_6.mp4",
        "canal": "LN+",
    },
    {
        "id": 7,
        "texto": "Elasticsearch y Python: indexación de transcripciones y consultas full-text en tiempo real, lorem ipsum dolor sit amet lorem."*5,
        "timestamp": "2025-09-13T10:12:00",
        "video": "video_7.mp4",
        "canal": "TN",
    },
    {
        "id": 8,
        "texto": "Consultas full-text, relevancia y escalabilidad en Elasticsearch aplicado a sistemas de noticias, lorem ipsum dolor sit amet."*5,
        "timestamp": "2025-09-13T10:14:20",
        "video": "video_8.mp4",
        "canal": "LN+",
    },
]

def get_transcripciones(palabra: str):
    return [t for t in transcripciones if palabra.lower() in t["texto"].lower()]