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

# --- CACHÉ DE INFORMACIÓN DE APIs ---
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

# --- BÚSQUEDA MANUAL DE COORDENADAS ---
@st.cache_data(ttl=3600)
def buscar_coordenadas(nombre_ciudad):
    try:
        user_agent = f"MiguelAppSearch_{random.randint(1000, 9999)}"
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={nombre_ciudad}&limit=1"
        res = requests.get(url, headers={'User-Agent': user_agent}, timeout=5).json()
        if res:
            lat = float(res[0]['lat'])
            lon = float(res[0]['lon'])
            nombre_bonito = res[0].get('display_name', nombre_ciudad).split(',')[0]
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
        # Si el GPS no responde o es lento, se le ofrece introducir la ciudad
        st.info("📍 Buscando señal GPS... Si tarda en cargar o deseas poner tu ciudad manualmente, escríbela abajo:")
        ciudad_inicial = st.text_input("Escribe tu ciudad o pueblo:", key="input_inicial")
        if st.button("Establecer ubicación"):
            res = buscar_coordenadas(ciudad_inicial)
            if res:
                st.session_state.lat, st.session_state.lon, st.session_state.ciudad_manual = res
                st.session_state.consejo_miguel = None
                st.rerun()
            else:
                st.error("No se ha encontrado esa localidad. Por favor, revisa cómo está escrita.")
        st.stop()

# --- SI YA TENEMOS LAS COORDENADAS (POR GPS O MANUAL) ---
try:
    # Obtener Zona Horaria automática según GPS o ciudad buscada
    nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
    zona_local = pytz.timezone(nombre_zona)

    # Cargar datos del clima y ubicación
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

    # --- MENÚ DE CAMBIO MANUAL DE UBICACIÓN ---
    with st.expander("⚙️ ¿No es tu ubicación? Cambiar ciudad"):
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_ciudad = st.text_input("Escribe el nombre de tu ciudad o pueblo:", key="buscar_nueva")
        with col2:
            st.write("") # Espacio estético
            buscar_btn = st.button("Buscar")
            
        if buscar_btn and nueva_ciudad:
            res = buscar_coordenadas(nueva_ciudad)
            if res:
                st.session_state.lat, st.session_state.lon, st.session_state.ciudad_manual = res
                st.session_state.consejo_miguel = None
                st.rerun()
            else:
                st.error("No se encontró. Intenta escribir el nombre completo.")
        
        # Botón para restaurar la geolocalización automática
        if st.button("🔄 Usar GPS automático del dispositivo"):
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.ciudad_manual = None
            st.session_state.consejo_miguel = None
            st.rerun()

    st.caption(f"v4.6 • Zona horaria: {nombre_zona} ({tipo_horario})")

except Exception as e:
    st.error("Ocurrió un error inesperado al procesar los datos de ubicación.")
