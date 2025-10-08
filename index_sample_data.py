#!/usr/bin/env python3
"""
Script para indexar datos de ejemplo en Elasticsearch para testing
"""

import json
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import pytz

# Deshabilitar warnings SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de Elasticsearch
ELASTICSEARCH_URL = "https://172.20.100.40:9200"
ELASTICSEARCH_USER = "elastic" 
ELASTICSEARCH_PASSWORD = "7=cZYAocp_XYeNfjsuk5"  # Password from .env
INDEX_NAME = "streaming_tv_test"  # Índice separado para testing/desarrollo

def create_sample_documents():
    import random
    """Crear documentos EXTENSOS de ejemplo para probar concatenación de transcripciones"""
    
    argentina_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    base_time = datetime.now(argentina_tz).replace(minute=0, second=0, microsecond=0)
    documents = []
    
    # ===== LUZU TV - 120 transcripciones cada 5 segundos (10 minutos de stream) =====
    luzutv_transcripts = [
        "[LUZ-001] Buenos días y bienvenidos a Luzu TV",
        "[LUZ-002] comenzamos con las noticias más importantes del día",
        "[LUZ-003] El presidente anunció nuevas medidas económicas",
        "[LUZ-004] para combatir la inflación que afecta a todos los sectores",
        "[LUZ-005] Los empresarios se reunieron ayer",
        "[LUZ-006] para analizar las nuevas políticas gubernamentales",
        "[LUZ-007] La crisis económica sigue siendo el tema principal",
        "[LUZ-008] en el debate político nacional de esta semana",
        "[LUZ-009] Según los últimos datos oficiales",
        "[LUZ-010] la inflación alcanzó un nuevo récord histórico",
        "[LUZ-011] Los sectores más afectados por la crisis",
        "[LUZ-012] son el comercio minorista y la industria manufacturera",
        "[LUZ-013] El gobierno promete medidas adicionales",
        "[LUZ-014] para estabilizar la economía el próximo mes",
        "[LUZ-015] Los gremios anunciaron un paro general",
        "[LUZ-016] para protestar por las nuevas medidas económicas",
        "[LUZ-017] La oposición criticó duramente",
        "[LUZ-018] las políticas económicas del gobierno actual",
        "[LUZ-019] Los mercados internacionales observan con atención",
        "[LUZ-020] la situación económica argentina",
        "[LUZ-021] El dólar oficial se mantuvo estable",
        "[LUZ-022] durante toda la jornada de ayer",
        "[LUZ-023] Los bancos centrales reportaron",
        "[LUZ-024] una alta demanda de divisas extranjeras",
        "[LUZ-025] La Bolsa de Comercio cerró",
        "[LUZ-026] con una baja significativa del dos por ciento",
        "[LUZ-027] Los analistas económicos prevén",
        "[LUZ-028] mayor volatilidad en los próximos días",
        "[LUZ-029] El Banco Central anunció",
        "[LUZ-030] que intervendrá activamente en el mercado cambiario",
        "[LUZ-031] Las exportaciones agrícolas muestran",
        "[LUZ-032] los primeros signos de recuperación económica",
        "[LUZ-033] Los productores rurales celebran",
        "[LUZ-034] el aumento de los precios internacionales",
        "[LUZ-035] La nueva temporada de cosecha",
        "[LUZ-036] promete ser exitosa según los especialistas",
        "[LUZ-037] El clima favorable de este año",
        "[LUZ-038] beneficia especialmente los cultivos de soja",
        "[LUZ-039] Los puertos del país están operando",
        "[LUZ-040] El gobierno evalúa nuevos acuerdos comerciales",
        "[LUZ-041] con países de la región asiática",
        "[LUZ-042] Los productores ganaderos expresan optimismo",
        "[LUZ-043] por las perspectivas del sector",
        "[LUZ-044] La faena bovina registra números récord",
        "[LUZ-045] en lo que va del presente año",
        "[LUZ-046] Los especialistas en comercio exterior",
        "[LUZ-047] predicen un crecimiento sostenido",
        "[LUZ-048] Las inversiones en el sector agroindustrial",
        "[LUZ-049] aumentaron significativamente este trimestre",
        "[LUZ-050] Nuevas tecnologías mejoran la productividad",
        "[LUZ-051] en los establecimientos rurales",
        "[LUZ-052] La digitalización llega al campo argentino",
        "[LUZ-053] con sistemas de monitoreo avanzados",
        "[LUZ-054] Los drones se utilizan cada vez más",
        "[LUZ-055] para supervisar los cultivos",
        "[LUZ-056] La agricultura de precisión revoluciona",
        "[LUZ-057] las prácticas tradicionales del campo",
        "[LUZ-058] Los sensores IoT monitorean",
        "[LUZ-059] las condiciones del suelo en tiempo real",
        "[LUZ-060] El Big Data optimiza",
        "[LUZ-061] las decisiones de siembra y cosecha",
        "[LUZ-062] La inteligencia artificial predice",
        "[LUZ-063] patrones climáticos con mayor precisión",
        "[LUZ-064] Los tractores autónomos comienzan",
        "[LUZ-065] a utilizarse en grandes extensiones",
        "[LUZ-066] La robótica agrícola promete",
        "[LUZ-067] revolucionar la industria alimentaria",
        "[LUZ-068] Los sistemas GPS mejoran",
        "[LUZ-069] la eficiencia en las tareas rurales",
        "[LUZ-070] La conectividad rural se expande",
        "[LUZ-071] llevando internet a zonas remotas",
        "[LUZ-072] Los productores acceden a información",
        "[LUZ-073] de mercados en tiempo real",
        "[LUZ-074] Las aplicaciones móviles facilitan",
        "[LUZ-075] la gestión de los establecimientos",
        "[LUZ-076] Las plataformas digitales conectan",
        "[LUZ-077] directamente productores con compradores",
        "[LUZ-078] El e-commerce agrícola crece exponencialmente",
        "[LUZ-079] cambiando las reglas del mercado",
        "[LUZ-080] Los marketplaces online facilitan",
        "[LUZ-081] la comercialización de productos rurales",
        "[LUZ-082] Las fintech rurales ofrecen",
        "[LUZ-083] soluciones financieras innovadoras",
        "[LUZ-084] Los créditos digitales llegan",
        "[LUZ-085] a pequeños y medianos productores",
        "[LUZ-086] La inclusión financiera mejora",
        "[LUZ-087] en las zonas rurales del país",
        "[LUZ-088] Los pagos digitales se adoptan",
        "[LUZ-089] masivamente en el sector agropecuario",
        "[LUZ-090] Las billeteras virtuales simplifican",
        "[LUZ-091] las transacciones comerciales rurales",
        "[LUZ-092] La trazabilidad digital garantiza",
        "[LUZ-093] la calidad de los productos",
        "[LUZ-094] Los códigos QR identifican",
        "[LUZ-095] el origen de cada producto",
        "[LUZ-096] La blockchain asegura",
        "[LUZ-097] la transparencia en la cadena alimentaria",
        "[LUZ-098] Los consumidores pueden rastrear",
        "[LUZ-099] desde el campo hasta su mesa",
        "[LUZ-100] La certificación digital verifica",
        "[LUZ-101] los estándares de calidad",
        "[LUZ-102] Los sellos de origen se digitalizan",
        "[LUZ-103] para combatir la falsificación",
        "[LUZ-104] La sustentabilidad se convierte",
        "[LUZ-105] en un diferencial competitivo",
        "[LUZ-106] Las prácticas ecológicas mejoran",
        "[LUZ-107] la imagen de los productos argentinos",
        "[LUZ-108] La huella de carbono se mide",
        "[LUZ-109] digitalmente en cada proceso",
        "[LUZ-110] Los mercados internacionales valoran",
        "[LUZ-111] los productos sustentables",
        "[LUZ-112] Las certificaciones ambientales abren",
        "[LUZ-113] nuevos nichos de exportación",
        "[LUZ-114] La agricultura regenerativa gana",
        "[LUZ-115] terreno entre los productores",
        "[LUZ-116] Las técnicas orgánicas se expanden",
        "[LUZ-117] por todo el territorio nacional",
        "[LUZ-118] Los fertilizantes naturales reemplazan",
        "[LUZ-119] gradualmente a los químicos",
        "[LUZ-120] La biodiversidad se protege",
        "[LUZ-121] mediante prácticas responsables",
        "[LUZ-122] Continuamos después del corte",
        "[LUZ-123] con información deportiva y del espectáculo"
    ]
    
    for i, text in enumerate(luzutv_transcripts):
        documents.append({
            "text": text,
            "slug": "luzutv",
            "name": "Luzu TV",
            "@timestamp": (base_time + timedelta(seconds=i * 5)).isoformat(),
            "service": "soflex2",
            "channel_id": "luzutv_main"
        })
    
    # ===== TODO NOTICIAS - 120 transcripciones cada 5 segundos (10 minutos de noticiero) =====
    todonoticias_transcripts = [
        "[TN-001] En vivo desde el Congreso Nacional",
        "[TN-002] seguimos la sesión especial de hoy",
        "[TN-003] Los diputados debaten intensamente",
        "[TN-004] el proyecto de ley de emergencia económica",
        "[TN-005] La oposición presentó más de cien modificaciones",
        "[TN-006] al proyecto original del oficialismo",
        "[TN-007] El oficialismo busca desesperadamente",
        "[TN-008] los votos necesarios para aprobar la ley",
        "[TN-009] Los legisladores intercambian argumentos",
        "[TN-010] sobre la controvertida reforma tributaria",
        "[TN-011] La sesión parlamentaria se extendió",
        "[TN-012] mucho más allá del horario previsto",
        "[TN-013] Miles de manifestantes protestan afuera",
        "[TN-014] del Congreso Nacional esta tarde",
        "[TN-015] La seguridad del edificio fue reforzada",
        "[TN-016] significativamente ante las protestas",
        "[TN-017] Los manifestantes piden la renuncia",
        "[TN-018] inmediata del ministro de Economía",
        "[TN-019] La policía federal mantiene el orden",
        "[TN-020] en todos los alrededores del edificio",
        "[TN-021] Dentro del recinto legislativo continúa",
        "[TN-022] el intenso debate político",
        "[TN-023] Los partidos provinciales aún no han definido",
        "[TN-024] su posición sobre el proyecto",
        "[TN-025] El gobernador de Buenos Aires expresó",
        "[TN-026] públicamente su apoyo a la iniciativa",
        "[TN-027] Los mandatarios del interior mantienen",
        "[TN-028] serias reservas sobre la propuesta",
        "[TN-029] La votación definitiva del proyecto",
        "[TN-030] se realizará en las próximas horas",
        "[TN-031] Los medios de comunicación internacionales",
        "[TN-032] siguen de cerca estos desarrollos",
        "[TN-033] Wall Street reacciona muy positivamente",
        "[TN-034] a las noticias desde Argentina",
        "[TN-035] Los bonos argentinos suben considerablemente",
        "[TN-036] en los mercados emergentes",
        "[TN-037] El riesgo país disminuye",
        "[TN-038] por primera vez en varias semanas",
        "[TN-039] Los inversores extranjeros muestran",
        "[TN-040] renovados signos de confianza",
        "[TN-041] El FMI expresó su satisfacción",
        "[TN-042] por las medidas adoptadas",
        "[TN-043] Las calificadoras de riesgo evalúan",
        "[TN-044] una posible mejora en la calificación",
        "[TN-045] Los analistas financieros prevén",
        "[TN-046] mayor estabilidad económica",
        "[TN-047] El ministro de Hacienda confirmó",
        "[TN-048] la llegada de nuevos desembolsos",
        "[TN-049] Los recursos permitirán financiar",
        "[TN-050] programas sociales prioritarios",
        "[TN-051] La ayuda social se incrementa",
        "[TN-052] para los sectores más vulnerables",
        "[TN-053] Las transferencias directas beneficiarán",
        "[TN-054] a millones de familias argentinas",
        "[TN-055] Los comedores comunitarios reciben",
        "[TN-056] mayor apoyo gubernamental",
        "[TN-057] La asistencia alimentaria se refuerza",
        "[TN-058] en todo el territorio nacional",
        "[TN-059] Las organizaciones sociales colaboran",
        "[TN-060] en la distribución de alimentos",
        "[TN-061] Los voluntarios trabajan incansablemente",
        "[TN-062] para llegar a todos los barrios",
        "[TN-063] La solidaridad argentina se hace presente",
        "[TN-064] en estos momentos difíciles",
        "[TN-065] Las donaciones privadas complementan",
        "[TN-066] los esfuerzos estatales",
        "[TN-067] Las empresas se suman a la ayuda",
        "[TN-068] con programas de responsabilidad social",
        "[TN-069] Los deportistas argentinos también colaboran",
        "[TN-070] con campañas de concientización",
        "[TN-071] Lionel Messi encabeza una iniciativa",
        "[TN-072] para ayudar a comedores infantiles",
        "[TN-073] La Selección Argentina dona parte",
        "[TN-074] de sus premios a causas sociales",
        "[TN-075] El fútbol argentino se moviliza",
        "[TN-076] por los sectores más necesitados",
        "[TN-077] Los clubes abren sus instalaciones",
        "[TN-078] para actividades comunitarias",
        "[TN-079] Las canchas se transforman temporalmente",
        "[TN-080] en centros de distribución",
        "[TN-081] Los jugadores visitan barrios humildes",
        "[TN-082] llevando alegría a los niños",
        "[TN-083] Las camisetas se rifan para recaudar",
        "[TN-084] fondos destinados a la ayuda social",
        "[TN-085] Los hinchas responden masivamente",
        "[TN-086] a los llamados solidarios",
        "[TN-087] Las barras organizan colectas",
        "[TN-088] en los alrededores de los estadios",
        "[TN-089] El deporte une a los argentinos",
        "[TN-090] en torno a objetivos comunes",
        "[TN-091] Los valores deportivos trascienden",
        "[TN-092] las diferencias sociales",
        "[TN-093] La competencia sana promueve",
        "[TN-094] la integración y la convivencia",
        "[TN-095] Las escuelas deportivas municipales",
        "[TN-096] ofrecen contención social",
        "[TN-097] Los profesores de educación física",
        "[TN-098] se convierten en referentes comunitarios",
        "[TN-099] Las actividades recreativas alejan",
        "[TN-100] a los jóvenes de situaciones de riesgo",
        "[TN-101] El deporte como herramienta",
        "[TN-102] de transformación social",
        "[TN-103] Los programas gubernamentales promueven",
        "[TN-104] la práctica deportiva masiva",
        "[TN-105] Las plazas públicas se equipan",
        "[TN-106] con elementos para ejercitarse",
        "[TN-107] Los circuitos aeróbicos se multiplican",
        "[TN-108] en parques y espacios verdes",
        "[TN-109] La actividad física mejora",
        "[TN-110] la salud de la población",
        "[TN-111] Los médicos recomiendan ejercicio",
        "[TN-112] como medicina preventiva",
        "[TN-113] Las campañas de salud pública",
        "[TN-114] promueven estilos de vida saludables",
        "[TN-115] La alimentación balanceada se enseña",
        "[TN-116] en escuelas y centros comunitarios",
        "[TN-117] Los nutricionistas ofrecen charlas gratuitas",
        "[TN-118] en barrios de todo el país",
        "[TN-119] Las huertas urbanas se expanden",
        "[TN-120] promoviendo la producción propia",
        "[TN-121] Los vecinos se organizan",
        "[TN-122] para cultivar sus propios alimentos",
        "[TN-123] Las semillas se distribuyen gratuitamente",
        "[TN-124] en programas municipales",
        "[TN-125] La agricultura urbana genera",
        "[TN-126] conciencia ambiental",
        "[TN-127] Los espacios verdes se cuidan",
        "[TN-128] mediante iniciativas ciudadanas",
        "[TN-129] El reciclaje se practica masivamente",
        "[TN-130] en todos los barrios",
        "[TN-131] Las campañas de limpieza movilizan",
        "[TN-132] a miles de voluntarios",
        "[TN-133] La separación de residuos se implementa",
        "[TN-134] progresivamente en toda la ciudad",
        "[TN-135] Los contenedores diferenciados facilitan",
        "[TN-136] el manejo sustentable de la basura",
        "[TN-137] Las cooperativas de recicladores",
        "[TN-138] se fortalecen con apoyo estatal",
        "[TN-139] El trabajo digno se promueve",
        "[TN-140] en el sector ambiental",
        "[TN-141] La economía circular genera",
        "[TN-142] nuevas oportunidades laborales",
        "[TN-143] Los materiales reciclados se valorizan",
        "[TN-144] creando cadenas productivas",
        "[TN-145] La industria nacional incorpora",
        "[TN-146] insumos provenientes del reciclaje",
        "[TN-147] Las empresas adoptan políticas",
        "[TN-148] de producción sustentable",
        "[TN-149] Los consumidores eligen productos",
        "[TN-150] ambientalmente responsables",
        "[TN-151] La conciencia ecológica crece",
        "[TN-152] entre todos los argentinos",
        "[TN-153] Ahora información meteorológica",
        "[TN-154] para todo el territorio nacional"
    ]
    
    for i, text in enumerate(todonoticias_transcripts):
        documents.append({
            "text": text,
            "slug": "todonoticias",
            "name": "Todo Noticias",
            "@timestamp": (base_time + timedelta(seconds=i * 5)).isoformat(),
            "service": "soflex3",
            "channel_id": "todonoticias_main"
        })
    
    # ===== OLGA EN VIVO - 100 transcripciones cada 5 segundos (8+ minutos de programa) =====
    olga_transcripts = [
        "[OLG-001] Hola mi gente bella y querida",
        "[OLG-002] bienvenidos a un nuevo programa en vivo",
        "[OLG-003] Hoy tenemos invitados súper especiales",
        "[OLG-004] esperándonos aquí en el estudio",
        "[OLG-005] Vamos a charlar sobre todos los temas",
        "[OLG-006] que más les interesan a ustedes",
        "[OLG-007] Las redes sociales están que explotan",
        "[OLG-008] con la polémica de ayer",
        "[OLG-009] Los famosos argentinos no paran",
        "[OLG-010] de generar contenido controversial cada día",
        "[OLG-011] La farándula nacional nunca deja",
        "[OLG-012] de sorprendernos con nuevos escándalos",
        "[OLG-013] Ahora vamos directo con las llamadas",
        "[OLG-014] telefónicas de nuestros queridos oyentes",
        "[OLG-015] María desde La Plata nos quiere contar",
        "[OLG-016] su increíble experiencia personal",
        "[OLG-017] Los chicos del chat están participando",
        "[OLG-018] muchísimo en el programa de hoy",
        "[OLG-019] Las donaciones y aportes no paran",
        "[OLG-020] de llegar, muchísimas gracias a todos",
        "[OLG-021] Recuerden que pueden seguirnos",
        "[OLG-022] en absolutamente todas las redes sociales",
        "[OLG-023] Instagram, TikTok, Twitter y YouTube",
        "[OLG-024] estamos presentes en todas las plataformas",
        "[OLG-025] Los clips más divertidos y virales",
        "[OLG-026] siempre los suben a YouTube",
        "[OLG-027] Nuestra hermosa comunidad de seguidores",
        "[OLG-028] crece muchísimo día a día",
        "[OLG-029] Ahora llegó el momento de la sección",
        "[OLG-030] de música en vivo que tanto esperaban",
        "[OLG-031] Tenemos una banda independiente",
        "[OLG-032] súper talentosa aquí en nuestro estudio",
        "[OLG-033] Van a interpretar su último single",
        "[OLG-034] que está sonando en todas las radios",
        "[OLG-035] La música argentina realmente tiene",
        "[OLG-036] un talento absolutamente increíble",
        "[OLG-037] Los músicos jóvenes están renovando",
        "[OLG-038] completamente la escena musical nacional",
        "[OLG-039] Después de este tema musical",
        "[OLG-040] seguimos con mucho más contenido divertido",
        "[OLG-041] Los juegos interactivos siempre son",
        "[OLG-042] los favoritos absolutos del público",
        "[OLG-043] Vamos a sortear merchandising oficial",
        "[OLG-044] y exclusivo del programa entre todos",
        "[OLG-045] Los premios incluyen remeras, gorras",
        "[OLG-046] stickers y muchas sorpresas más",
        "[OLG-047] Para participar en el sorteo",
        "[OLG-048] solo tienen que estar suscritos al canal",
        "[OLG-049] La diversión y las risas están",
        "[OLG-050] completamente garantizadas en cada programa",
        "[OLG-051] Ahora viene Juancito con su guitarra",
        "[OLG-052] para tocar una canción súper especial",
        "[OLG-053] La música nos conecta con las emociones",
        "[OLG-054] más profundas del alma humana",
        "[OLG-055] Los artistas expresan sus sentimientos",
        "[OLG-056] a través de melodías hermosas",
        "[OLG-057] Cada nota musical toca el corazón",
        "[OLG-058] de quienes nos están escuchando",
        "[OLG-059] La creatividad argentina no tiene límites",
        "[OLG-060] cuando se trata de arte y cultura",
        "[OLG-061] Los compositores locales crean obras",
        "[OLG-062] que trascienden las fronteras",
        "[OLG-063] Nuestro folklore es reconocido",
        "[OLG-064] mundialmente por su riqueza",
        "[OLG-065] El tango sigue siendo un emblema",
        "[OLG-066] que nos representa en el mundo",
        "[OLG-067] Buenos Aires es la capital mundial",
        "[OLG-068] de este género musical único",
        "[OLG-069] Las milongas se llenan cada noche",
        "[OLG-070] de parejas que bailan con pasión",
        "[OLG-071] Los turistas vienen especialmente",
        "[OLG-072] para aprender nuestros bailes típicos",
        "[OLG-073] La cultura argentina se exporta",
        "[OLG-074] a través de su música y danza",
        "[OLG-075] Los festivales folclóricos convocan",
        "[OLG-076] multitudes en todo el país",
        "[OLG-077] Cosquín es la meca de la música",
        "[OLG-078] tradicional argentina",
        "[OLG-079] Cada enero miles de personas",
        "[OLG-080] peregrinan hacia Córdoba",
        "[OLG-081] Para vivir la experiencia única",
        "[OLG-082] de la música en vivo",
        "[OLG-083] Los artistas emergentes encuentran",
        "[OLG-084] su oportunidad de brillar",
        "[OLG-085] Las redes sociales ayudan",
        "[OLG-086] a difundir nuevos talentos",
        "[OLG-087] YouTube se convirtió en la plataforma",
        "[OLG-088] de lanzamiento de muchos músicos",
        "[OLG-089] Los covers caseros se vuelven virales",
        "[OLG-090] llegando a millones de reproducciones",
        "[OLG-091] La democratización de la música",
        "[OLG-092] permite que todos participen",
        "[OLG-093] Ya no hacen falta grandes discográficas",
        "[OLG-094] para llegar al público",
        "[OLG-095] Los estudios de grabación caseros",
        "[OLG-096] producen música de calidad profesional",
        "[OLG-097] La tecnología acercó las herramientas",
        "[OLG-098] de producción a todos los artistas",
        "[OLG-099] Los programas de edición de audio",
        "[OLG-100] están al alcance de cualquiera",
        "[OLG-101] La educación musical online",
        "[OLG-102] se expandió durante la pandemia",
        "[OLG-103] Los profesores enseñan instrumentos",
        "[OLG-104] a través de videollamadas",
        "[OLG-105] Las clases virtuales llegaron",
        "[OLG-106] a estudiantes de todo el país",
        "[OLG-107] La música no conoce distancias",
        "[OLG-108] cuando hay pasión de por medio",
        "[OLG-109] Los conservatorios adaptaron",
        "[OLG-110] sus metodologías a la virtualidad",
        "[OLG-111] Los exámenes se toman online",
        "[OLG-112] manteniendo los estándares de calidad",
        "[OLG-113] La formación musical se democratizó",
        "[OLG-114] llegando a más personas que nunca"
    ]
    
    for i, text in enumerate(olga_transcripts):
        documents.append({
            "text": text,
            "slug": "olgaenvivo_",
            "name": "Olga en Vivo",
            "@timestamp": (base_time + timedelta(seconds=i * 5)).isoformat(),
            "service": "soflex1",
            "channel_id": "olgaenvivo_main"
        })
    
    # ===== C5N - 100 transcripciones cada 5 segundos (8+ minutos de noticias) =====
    c5n_transcripts = [
        "[C5N-001] Último momento: se registró un fuerte sismo",
        "[C5N-002] en el centro del país",
        "[C5N-003] El epicentro del temblor se ubicó",
        "[C5N-004] precisamente en la provincia de San Juan",
        "[C5N-005] La intensidad del sismo alcanzó",
        "[C5N-006] los 4.2 grados en la escala de Richter",
        "[C5N-007] Hasta el momento no se reportan",
        "[C5N-008] daños materiales significativos ni víctimas",
        "[C5N-009] Todos los servicios de emergencia",
        "[C5N-010] del país están en máxima alerta",
        "[C5N-011] Defensa Civil coordina activamente",
        "[C5N-012] las tareas de evaluación de daños",
        "[C5N-013] Los vecinos de toda la zona afectada",
        "[C5N-014] sintieron claramente el movimiento sísmico",
        "[C5N-015] Las autoridades provinciales solicitan",
        "[C5N-016] a la población mantener absoluta calma",
        "[C5N-017] En otras noticias importantes",
        "[C5N-018] el dólar blue cerró nuevamente en alza",
        "[C5N-019] La brecha cambiaria se amplió",
        "[C5N-020] considerablemente en el mercado paralelo",
        "[C5N-021] Los ahorristas buscan desesperadamente",
        "[C5N-022] refugio seguro en moneda extranjera",
        "[C5N-023] Las casas de cambio de todo el país",
        "[C5N-024] reportan una demanda sin precedentes",
        "[C5N-025] El Banco Central de la República",
        "[C5N-026] evaluará nuevas medidas esta misma semana",
        "[C5N-027] Los economistas más prestigiosos",
        "[C5N-028] dividen sus opiniones sobre las perspectivas",
        "[C5N-029] Mientras tanto, en el ámbito deportivo",
        "[C5N-030] nacional tenemos novedades importantes",
        "[C5N-031] La selección argentina de fútbol",
        "[C5N-032] se prepara intensivamente para el próximo partido",
        "[C5N-033] Todos los jugadores convocados entrenan",
        "[C5N-034] diariamente en el predio de la AFA",
        "[C5N-035] El técnico nacional definirá",
        "[C5N-036] el equipo titular en las próximas horas",
        "[C5N-037] Los hinchas de todo el país",
        "[C5N-038] ya comenzaron a comprar las entradas",
        "[C5N-039] Se espera una multitud récord",
        "[C5N-040] en el estadio para presenciar el encuentro",
        "[C5N-041] Las camisetas oficiales se agotan",
        "[C5N-042] en todos los comercios deportivos",
        "[C5N-043] Los sponsors aumentan su inversión",
        "[C5N-044] publicitaria para el partido",
        "[C5N-045] La expectativa crece minuto a minuto",
        "[C5N-046] entre todos los aficionados",
        "[C5N-047] Las redes sociales explotan",
        "[C5N-048] con mensajes de apoyo al equipo",
        "[C5N-049] Los jugadores reciben el cariño",
        "[C5N-050] de millones de argentinos",
        "[C5N-051] La concentración del plantel",
        "[C5N-052] se realiza en completo hermetismo",
        "[C5N-053] Los periodistas deportivos buscan",
        "[C5N-054] cualquier información sobre la formación",
        "[C5N-055] Las filtraciones sobre el equipo",
        "[C5N-056] generan debate en los medios",
        "[C5N-057] Los programas deportivos analizan",
        "[C5N-058] cada posible cambio táctico",
        "[C5N-059] Los ex jugadores dan su opinión",
        "[C5N-060] sobre las decisiones del entrenador",
        "[C5N-061] El fútbol argentino vive una nueva",
        "[C5N-062] jornada de máxima expectativa",
        "[C5N-063] Los clubes locales también se preparan",
        "[C5N-064] para sus compromisos del fin de semana",
        "[C5N-065] El torneo local genera gran interés",
        "[C5N-066] entre los hinchas de cada equipo",
        "[C5N-067] Los clásicos convocan multitudes",
        "[C5N-068] en todos los estadios del país",
        "[C5N-069] La pasión por el fútbol une",
        "[C5N-070] a argentinos de todas las edades",
        "[C5N-071] Los niños sueñan con ser futbolistas",
        "[C5N-072] inspirados por sus ídolos",
        "[C5N-073] Las escuelitas de fútbol se multiplican",
        "[C5N-074] en todos los barrios",
        "[C5N-075] Los entrenadores forman",
        "[C5N-076] a las nuevas generaciones",
        "[C5N-077] El semillero argentino sigue",
        "[C5N-078] produciendo talentos excepcionales",
        "[C5N-079] Las divisiones inferiores trabajan",
        "[C5N-080] con metodologías modernas",
        "[C5N-081] La formación integral incluye",
        "[C5N-082] aspectos técnicos y humanos",
        "[C5N-083] Los valores del deporte se inculcan",
        "[C5N-084] desde las categorías más pequeñas",
        "[C5N-085] El respeto por el rival",
        "[C5N-086] es fundamental en la educación deportiva",
        "[C5N-087] Los árbitros también se capacitan",
        "[C5N-088] constantemente para mejorar",
        "[C5N-089] La tecnología llega al fútbol",
        "[C5N-090] con nuevas herramientas de análisis",
        "[C5N-091] El VAR revoluciona las decisiones",
        "[C5N-092] arbitrales en los partidos importantes",
        "[C5N-093] Las cámaras de alta definición",
        "[C5N-094] capturan cada jugada polémica",
        "[C5N-095] Los replays ayudan a tomar",
        "[C5N-096] decisiones más justas",
        "[C5N-097] La polémica arbitral disminuye",
        "[C5N-098] gracias a estas innovaciones",
        "[C5N-099] Los hinchas aceptan mejor",
        "[C5N-100] las decisiones tecnológicas",
        "[C5N-101] La transparencia en el arbitraje",
        "[C5N-102] mejora la credibilidad del torneo",
        "[C5N-103] Los reglamentos se actualizan",
        "[C5N-104] permanentemente para mayor claridad",
        "[C5N-105] Las capacitaciones arbitrales incluyen",
        "[C5N-106] el uso de nuevas tecnologías",
        "[C5N-107] Los jueces de línea también",
        "[C5N-108] se adaptan a los cambios",
        "[C5N-109] El fútbol evoluciona constantemente",
        "[C5N-110] manteniendo su esencia tradicional",
        "[C5N-111] La pasión popular permanece intacta",
        "[C5N-112] a pesar de las innovaciones",
        "[C5N-113] Los estadios siguen siendo",
        "[C5N-114] templos de la emoción deportiva",
        "[C5N-115] La fiesta del fútbol convoca",
        "[C5N-116] a familias enteras cada fin de semana",
        "[C5N-117] Abuelos, padres e hijos comparten",
        "[C5N-118] la pasión por sus colores",
        "[C5N-119] Las tradiciones se transmiten",
        "[C5N-120] de generación en generación",
        "[C5N-121] Los cánticos históricos resuenan",
        "[C5N-122] en cada encuentro futbolístico"
    ]
    
    for i, text in enumerate(c5n_transcripts):
        documents.append({
            "text": text,
            "slug": "c5n",
            "name": "C5N",
            "@timestamp": (base_time + timedelta(seconds=i * 5)).isoformat(),
            "service": "soflex6",
            "channel_id": "c5n_main"
        })
    
    # ===== A24 - 80 transcripciones cada 5 segundos (6+ minutos de análisis) =====
    a24_transcripts = [
        "[A24-001] Analizamos en profundidad la compleja",
        "[A24-002] situación política que vive el país",
        "[A24-003] Los partidos de la oposición buscan",
        "[A24-004] desesperadamente consensos estratégicos importantes",
        "[A24-005] La peligrosa polarización social",
        "[A24-006] se intensifica dramáticamente día tras día",
        "[A24-007] Los ciudadanos expresan claramente",
        "[A24-008] su profundo descontento en las encuestas",
        "[A24-009] La gobernabilidad democrática está siendo",
        "[A24-010] severamente puesta a prueba",
        "[A24-011] Los analistas políticos más experimentados",
        "[A24-012] debaten intensamente sobre el futuro nacional",
        "[A24-013] Las próximas elecciones presidenciales",
        "[A24-014] generan muchísima incertidumbre",
        "[A24-015] Los potenciales candidatos comienzan",
        "[A24-016] lentamente a definir sus estrategias electorales",
        "[A24-017] Las tradicionales alianzas partidarias",
        "[A24-018] se reconfiguran completamente",
        "[A24-019] El panorama electoral general cambia",
        "[A24-020] drásticamente semana tras semana",
        "[A24-021] Los medios de comunicación masiva",
        "[A24-022] juegan un rol absolutamente fundamental",
        "[A24-023] La información política circula",
        "[A24-024] a una velocidad nunca antes vista",
        "[A24-025] Las redes sociales digitales amplifican",
        "[A24-026] exponencialmente todos los mensajes políticos",
        "[A24-027] Los políticos profesionales adaptan",
        "[A24-028] completamente su comunicación digital",
        "[A24-029] La juventud argentina participa",
        "[A24-030] mucho más activamente en el debate público",
        "[A24-031] Las universidades públicas organizan",
        "[A24-032] constantemente foros de discusión política",
        "[A24-033] Los estudiantes universitarios manifiestan",
        "[A24-034] muy claramente sus posiciones políticas",
        "[A24-035] El sistema de educación pública",
        "[A24-036] enfrenta serios desafíos presupuestarios",
        "[A24-037] Los docentes de todos los niveles",
        "[A24-038] reclaman urgentemente mejores salarios",
        "[A24-039] La inversión estatal en ciencia",
        "[A24-040] y tecnología preocupa al sector académico",
        "[A24-041] Los investigadores alertan sobre",
        "[A24-042] el riesgo de fuga de cerebros",
        "[A24-043] Las becas de investigación disminuyen",
        "[A24-044] año tras año preocupantemente",
        "[A24-045] Los laboratorios necesitan equipamiento",
        "[A24-046] moderno para competir internacionalmente",
        "[A24-047] La innovación tecnológica requiere",
        "[A24-048] inversión sostenida a largo plazo",
        "[A24-049] Los países vecinos avanzan",
        "[A24-050] mientras nosotros nos estancamos",
        "[A24-051] La competitividad internacional",
        "[A24-052] depende del desarrollo científico",
        "[A24-053] Las patentes argentinas disminuyen",
        "[A24-054] en el registro mundial",
        "[A24-055] La transferencia tecnológica",
        "[A24-056] desde universidades es insuficiente",
        "[A24-057] Las empresas necesitan mayor",
        "[A24-058] vinculación con centros de investigación",
        "[A24-059] Los parques tecnológicos se desarrollan",
        "[A24-060] lentamente por falta de recursos",
        "[A24-061] Las startups tecnológicas emigran",
        "[A24-062] buscando mejores condiciones",
        "[A24-063] El ecosistema emprendedor necesita",
        "[A24-064] políticas públicas de fomento",
        "[A24-065] Los fondos de inversión extranjeros",
        "[A24-066] evalúan cuidadosamente el marco regulatorio",
        "[A24-067] La seguridad jurídica es fundamental",
        "[A24-068] para atraer capitales genuinos",
        "[A24-069] Las reglas de juego claras",
        "[A24-070] generan confianza en los inversores",
        "[A24-071] El marco impositivo debe ser",
        "[A24-072] competitivo a nivel regional",
        "[A24-073] Los trámites burocráticos desalientan",
        "[A24-074] la creación de nuevas empresas",
        "[A24-075] La simplificación administrativa",
        "[A24-076] es una demanda constante del sector privado",
        "[A24-077] Las ventanillas únicas digitales",
        "[A24-078] agilizan los procedimientos estatales",
        "[A24-079] La digitalización del Estado",
        "[A24-080] mejora la eficiencia gubernamental",
        "[A24-081] Los ciudadanos valoran",
        "[A24-082] los servicios públicos digitales",
        "[A24-083] Las aplicaciones móviles gubernamentales",
        "[A24-084] facilitan el acceso a trámites",
        "[A24-085] La identidad digital unifica",
        "[A24-086] todos los servicios estatales",
        "[A24-087] La interoperabilidad entre organismos",
        "[A24-088] evita la duplicación de datos",
        "[A24-089] Los datos abiertos promueven",
        "[A24-090] la transparencia gubernamental",
        "[A24-091] La participación ciudadana se potencia",
        "[A24-092] con herramientas digitales",
        "[A24-093] Las consultas públicas online",
        "[A24-094] amplían la base de participación"
    ]
    
    for i, text in enumerate(a24_transcripts):
        documents.append({
            "text": text,
            "slug": "a24com",
            "name": "A24",
            "@timestamp": (base_time + timedelta(hours=1, minutes=30, seconds=i * 5)).isoformat(),
            "service": "soflex7",
            "channel_id": "a24_main"
        })

    return documents

def create_test_index():
    """Crear el índice de testing si no existe"""
    
    # Verificar si el índice ya existe
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    check_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}"
    
    try:
        response = requests.head(check_url, auth=auth, verify=False)
        if response.status_code == 200:
            print(f"✅ Índice {INDEX_NAME} ya existe")
            return True
    except Exception:
        pass
    
    # Crear el índice con mapping similar al original
    mapping = {
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "text": {"type": "text", "analyzer": "spanish"},
                "slug": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "name": {"type": "text"},
                "service": {"type": "keyword"},
                "channel_id": {"type": "keyword"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    try:
        response = requests.put(
            check_url,
            json=mapping,
            headers={"Content-Type": "application/json"},
            auth=auth,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Índice de testing {INDEX_NAME} creado exitosamente")
            return True
        else:
            print(f"❌ Error creando índice: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creando índice: {e}")
        return False

def index_document(doc, doc_id=None):
    """Indexar un documento en Elasticsearch"""
    
    url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_doc"
    if doc_id:
        url += f"/{doc_id}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    
    try:
        response = requests.post(
            url,
            json=doc,
            headers=headers, 
            auth=auth,
            verify=False  # Deshabilitar verificación SSL para desarrollo
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Documento indexado: {doc['slug']} - {doc['text'][:50]}...")
            return True
        else:
            print(f"❌ Error indexando documento: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_elasticsearch_connection():
    """Verificar conexión con Elasticsearch"""
    
    try:
        auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
        response = requests.get(
            f"{ELASTICSEARCH_URL}/_cluster/health",
            auth=auth,
            verify=False
        )
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Elasticsearch conectado - Estado: {health.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Error conectando a Elasticsearch: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión a Elasticsearch: {e}")
        print("   Verifica que Elasticsearch esté ejecutándose en:", ELASTICSEARCH_URL)
        return False

def create_index_if_not_exists():
    """Crear el índice si no existe"""
    
    mapping = {
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "slug": {"type": "keyword"}, 
                "name": {"type": "text"},
                "@timestamp": {"type": "date"},
                "service": {"type": "keyword"},
                "channel_id": {"type": "keyword"}
            }
        }
    }
    
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    
    try:
        # Verificar si el índice existe
        response = requests.head(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}",
            auth=auth,
            verify=False
        )
        
        if response.status_code == 200:
            print(f"✅ Índice '{INDEX_NAME}' ya existe")
            return True
        
        # Crear el índice
        response = requests.put(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}",
            json=mapping,
            auth=auth,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Índice '{INDEX_NAME}' creado exitosamente")
            return True
        else:
            print(f"❌ Error creando índice: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error manejando índice: {e}")
        return False

def main():
    """Función principal"""
    
    print("🔍 Indexando MUCHOS datos de ejemplo para probar CONCATENACIÓN")
    print(f"📍 Índice de destino: {INDEX_NAME}")
    print("=" * 60)
    
    # Verificar conexión
    if not check_elasticsearch_connection():
        return
    
    # Crear índice de testing si no existe
    if not create_test_index():
        return
    
    # Crear y indexar documentos
    documents = create_sample_documents()
    
    print(f"\n📄 Indexando {len(documents)} transcripciones SÚPER REALISTAS...")
    print(f"📺 Canales con transcripciones cada 5 SEGUNDOS:")
    print(f"   🟢 Luzu TV: 120 transcripciones (10 min) - Tema: Economía y Agro")
    print(f"   🔴 Todo Noticias: 120 transcripciones (10 min) - Tema: Política y Social")
    print(f"   🟡 Olga en Vivo: 100 transcripciones (8+ min) - Tema: Entretenimiento") 
    print(f"   🔵 C5N: 100 transcripciones (8+ min) - Tema: Noticias y Deportes") 
    print(f"   🟣 A24: 80 transcripciones (6+ min) - Tema: Análisis Político")
    
    success_count = 0
    for i, doc in enumerate(documents, 1):
        if index_document(doc, f"mock_{i}"):
            success_count += 1
            if i % 10 == 0:
                print(f"   📊 Procesados: {i}/{len(documents)} documentos")
    
    print("\n" + "=" * 60)
    print(f"✅ Transcripciones indexadas: {success_count}/{len(documents)}")
    print(f"📊 Índice de testing: {INDEX_NAME}")
    
    if success_count > 0:
        print(f"\n🎯 PRUEBA DE CONCATENACIÓN ULTRA-REALISTA - Busca:")
        print(f"   💰 'presidente' o 'inflación' → Luzu TV (120 transcripciones cada 5seg)")
        print(f"   🏛️  'Congreso' o 'diputados' → Todo Noticias (120 transcripciones cada 5seg)")
        print(f"   🎭 'programa' o 'música' → Olga en Vivo (100 transcripciones cada 5seg)")
        print(f"   📺 'sismo' o 'fútbol' → C5N (100 transcripciones cada 5seg)")
        print(f"   🎙️  'política' o 'democracia' → A24 (80 transcripciones cada 5seg)")
        
        print(f"\n� REALISMO EXTREMO:")
        print(f"   ⚡ Transcripciones cada 5 SEGUNDOS (como streaming real)")
        print(f"   📹 Simula 6-10 MINUTOS continuos de cada canal")
        print(f"   🔗 Perfectas para probar concatenación automática")
        print(f"   🎬 Cada búsqueda debería encontrar MUCHAS transcripciones seguidas")
        
        print(f"\n🧪 CÓMO PROBAR:")
        print(f"   1️⃣  Busca cualquier palabra clave de arriba")
        print(f"   2️⃣  Selecciona un resultado en 'TRANSCRIPCIÓN SELECCIONADA'")
        print(f"   3️⃣  Deberías ver 80-120 transcripciones del mismo canal")
        print(f"   4️⃣  La concatenación unirá automáticamente clips consecutivos")
        print(f"   5️⃣  El video final tendrá 6-10 minutos de contenido real")
        
        print(f"\n⚠️  CONFIGURACIÓN NECESARIA:")
        print(f"   • Backend debe usar índice: '{INDEX_NAME}'")
        print(f"   • Necesitas videos mock correspondientes (create_mock_videos.py)")
        print(f"   • Cada transcripción = 1 clip de 5 segundos")
        
        print(f"\n🚀 ¡{success_count} transcripciones ULTRA-REALISTAS listas para concatenar!")

if __name__ == "__main__":
    main()