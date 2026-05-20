import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
import random
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
import streamlit.components.v1 as components

# 1. Configuración y OCULTAR MENÚS de Streamlit
st.set_page_config(page_title="IA de Miguel", page_icon="🌤️", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# Instanciar TimezoneFinder una sola vez
tf = TimezoneFinder()

# --- CONSEJOS FIJOS SEGÚN CLIMA PRECISO ---
if 'consejo_miguel' not in st.session_state:
    st.session_state.consejo_miguel = None

def obtener_consejo(codigo):
    if st.session_state.consejo_miguel is not None:
        return st.session_state.consejo_miguel
        
    if codigo == 0:
        opciones = [
            ("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")
        ]
    elif codigo == 1:
        opciones = [
            ("Mayormente Despejado 🌤️", "¡Buen día! El sol brilla con fuerza."),
            ("Mayormente Despejado 🌤️", "Cielo casi limpio. ¡Aprovecha el día!")
        ]
    elif codigo == 2:
        opciones = [
            ("Intervalos Nubosos ⛅", "Algunas nubes en el cielo, pero un gran día por delante."),
            ("Intervalos Nubosos ⛅", "El sol juega al escondite. ¡Que nada te pare!")
        ]
    elif codigo == 3:
        opciones = [
            ("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")
        ]
    elif codigo in [45, 48]:
        opciones = [
            ("Niebla 🌫️", "Poca visibilidad fuera, pero tú lo tienes todo claro."),
            ("Niebla 🌫️", "Día misterioso. ¡Camina con paso firme!")
        ]
    elif codigo in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        opciones = [
            ("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
            ("Lluvia 🌧️", "Día lluvioso, buen momento para un café caliente y reflexionar.")
        ]
    elif codigo in [71, 73, 75, 77, 85, 86]:
        opciones = [
            ("Nieve ❄️", "¡Está nevando! Abrígate bien y disfruta del paisaje.")
        ]
    elif codigo in [95, 96, 99]:
        opciones = [
            ("Tormenta ⚡", "Cuidado con los rayos. Mejor quedarse a cubierto.")
        ]
    else:
        opciones = [("Variable 🌈", "Disfruta del día al máximo.")]
        
    st.session_state.consejo_miguel = random.choice(opciones)
    return st.session_state.consejo_miguel

# --- CACHÉ DE INFORMACIÓN DE APIs (Clima y reversión de coordenadas) ---
@st.cache_data(ttl=600)
def cargar_info(la, lo):
    ciudad = None
    try:
        url_bdc = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={la}&longitude={lo}&localityLanguage=es"
        response = requests.get(url_bdc, timeout=4)
        if response.status_code == 200:
            g = response.json()
            ciudad = g.get('city') or g.get('locality') or g.get('principalSubdivision')
    except Exception:
        pass
        
    if not ciudad:
        try:
            user_agent = f"MiguelAppGeolocator_{random.randint(1000, 9999)}"
            url_osm = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}"
            response = requests.get(url_osm, headers={'User-Agent': user_agent}, timeout=4)
            if response.status_code == 200:
                g = response.json()
                address = g.get('address', {})
                ciudad = address.get('city') or address.get('town') or address.get('village')
        except Exception:
            pass

    if not ciudad:
        ciudad = "Ubicación Detectada"
        
    try:
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true"
        cl = requests.get(url_clima, timeout=5).json()
        temp = cl['current_weather']['temperature']
        cod = cl['current_weather']['weathercode']
    except Exception:
        temp = "--"
        cod = -1
        
    return ciudad, temp, cod

# --- BÚSQUEDA MUNDIAL DE COORDENADAS (Usando Open-Meteo Geocoding) ---
@st.cache_data(ttl=3600)
def buscar_coordenadas(nombre_ciudad):
    try:
        # Intentar buscar el texto completo
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(nombre_ciudad)}&count=1&language=es&format=json"
        response = requests.get(url, timeout=5)
        res = response.json()
        results = res.get('results')
        
        # Si no hay resultados y contiene una coma, buscamos solo por el primer término (ej: de "Tremp, Barcelona" busca "Tremp")
        if not results and "," in nombre_ciudad:
            primer_termino = nombre_ciudad.split(",")[0].strip()
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(primer_termino)}&count=1&language=es&format=json"
            response = requests.get(url, timeout=5)
            res = response.json()
            results = res.get('results')

        if results:
            result = results[0]
            lat = result['latitude']
            lon = result['longitude']
            
            # Formatear el nombre de la ubicación
            name = result.get('name')
            admin1 = result.get('admin1')
            country = result.get('country')
            
            parts = [name]
            if admin1 and admin1 != name:
                parts.append(admin1)
            if country:
                nombre_bonito = f"{', '.join(parts)} ({country})"
            else:
                nombre_bonito = ', '.join(parts)
                
            return lat, lon, nombre_bonito
    except Exception:
        pass
    return None

# --- MANEJO DE ESTADO DE UBICACIÓN ---
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None
if 'ciudad_manual' not in st.session_state:
    st.session_state.ciudad_manual = None

st.title("🚀 ia inteligente sencilla de miguel")

# 1. Verificar si hay ubicación guardada en la sesión
lat = st.session_state.lat
lon = st.session_state.lon

if lat is None or lon is None:
    # Intentar obtener GPS del navegador
    with st.spinner("📍 Buscando señal GPS del dispositivo..."):
        loc = get_geolocation()
    
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.rerun()
    else:
        # Formulario inicial si no carga el GPS
        st.info("📍 Buscando señal GPS... Escribe tu ubicación para empezar al instante:")
        with st.form("buscador_inicial"):
            ciudad_inicial = st.text_input("Escribe tu ciudad, pueblo o país (ej: Tremp):")
            buscar_init = st.form_submit_button("Establecer ubicación")
            
        if buscar_init and ciudad_inicial:
            res = buscar_coordenadas(ciudad_inicial)
            if res:
                st.session_state.lat, st.session_state.lon, st.session_state.ciudad_manual = res
                st.session_state.consejo_miguel = None
                st.rerun()
            else:
                st.error("❌ No se encontró esa ubicación. Intenta escribir el nombre completo.")
        st.stop()

# --- SI YA TENEMOS LAS COORDENADAS ---
try:
    # Obtener Zona Horaria según coordenadas
    nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
    zona_local = pytz.timezone(nombre_zona)

    # Cargar clima y ubicación
    ciudad_detectada, temp, cod = cargar_info(lat, lon)
    ciudad = st.session_state.ciudad_manual or ciudad_detectada

    # Detectar Horario de Verano/Invierno
    ahora_local = datetime.now(zona_local)
    es_dst = ahora_local.dst() is not None and ahora_local.dst() != timedelta(0)
    tipo_horario = "Horario de Verano (DST) ☀️" if es_dst else "Horario Estándar (Invierno) ❄️"

    # Mostrar Ubicación y Fecha
    fecha_actual = ahora_local.strftime('%d/%m/%Y')
    st.write(f"📍 **{ciudad}** | 📅 {fecha_actual}")

    # --- RELOJ DIGITAL EN JAVASCRIPT ---
    reloj_html = f"""
    <div id="reloj" style="
        text-align: center; 
        font-size: 85px; 
        font-weight: 200; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 10px 0;
    ">00:00:00</div>
    
    <script>
    function actualizarReloj() {{
        const ahora = new Date();
        const opciones = {{
            timeZone: '{nombre_zona}',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }};
        const formateador = new Intl.DateTimeFormat('es-ES', opciones);
        document.getElementById('reloj').innerText = formateador.format(ahora);
    }}
    actualizarReloj();
    setInterval(actualizarReloj, 1000);
    </script>
    
    <style>
    #reloj {{ color: #31333F; }}
    @media (prefers-color-scheme: dark) {{
        #reloj {{ color: #FAFAFA; }}
    }}
    </style>
    """
    components.html(reloj_html, height=120)

    # Mostrar métricas y consejo
    st.metric("🌡️ Temperatura", f"{temp} °C")
    
    estado, mensaje = obtener_consejo(cod)
    st.info(f"**{estado}** — {mensaje}")
    
    st.divider()

    # --- BUSCADOR DE CIUDAD EN EXPANDER ---
    with st.expander("⚙️ ¿No es tu ubicación? Cambiar ciudad"):
        with st.form("buscador_form"):
            nueva_ciudad = st.text_input("Escribe tu ubicación (puedes poner 'Tremp, Barcelona', 'Barcelona' o cualquier sitio del mundo):")
            buscar_btn = st.form_submit_button("🔍 Buscar Ubicación")
            
        if buscar_btn and nueva_ciudad:
            res = buscar_coordenadas(nueva_ciudad)
            if res:
                st.session_state.lat, st.session_state.lon, st.session_state.ciudad_manual = res
                st.session_state.consejo_miguel = None
                st.rerun()
            else:
                st.error("❌ No se encontró esa ubicación. Intenta escribir el nombre completo.")
        
        # Botón para restaurar la geolocalización automática
        if st.button("🔄 Volver a usar GPS automático"):
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.ciudad_manual = None
            st.session_state.consejo_miguel = None
            st.rerun()

    st.caption(f"v4.6 • Zona horaria: {nombre_zona} ({tipo_horario})")

except Exception as e:
    st.error("Ocurrió un error inesperado al procesar los datos de ubicación.")
