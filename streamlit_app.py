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

# Instanciar TimezoneFinder una sola vez a nivel de módulo
tf = TimezoneFinder()

# --- CONSEJOS FIJOS SEGÚN CLIMA PRECISO (WMO CODES) ---
if 'consejo_miguel' not in st.session_state:
    st.session_state.consejo_miguel = None

def obtener_consejo(codigo):
    if st.session_state.consejo_miguel is not None:
        return st.session_state.consejo_miguel
        
    # Clasificación precisa de códigos WMO de Open-Meteo
    if codigo == 0:  # Totalmente despejado
        opciones = [
            ("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")
        ]
    elif codigo == 1:  # Mayormente despejado
        opciones = [
            ("Mayormente Despejado 🌤️", "¡Buen día! El sol brilla con fuerza."),
            ("Mayormente Despejado 🌤️", "Cielo casi limpio. ¡Aprovecha el día!")
        ]
    elif codigo == 2:  # Nubes y claros
        opciones = [
            ("Intervalos Nubosos ⛅", "Algunas nubes en el cielo, pero un gran día por delante."),
            ("Intervalos Nubosos ⛅", "El sol juega al escondite. ¡Que nada te pare!")
        ]
    elif codigo == 3:  # Completamente cubierto
        opciones = [
            ("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")
        ]
    elif codigo in [45, 48]:  # Niebla
        opciones = [
            ("Niebla 🌫️", "Poca visibilidad fuera, pero tú lo tienes todo claro."),
            ("Niebla 🌫️", "Día misterioso. ¡Camina con paso firme!")
        ]
    elif codigo in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:  # Llovizna y lluvia
        opciones = [
            ("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
            ("Lluvia 🌧️", "Día lluvioso, buen momento para un café caliente y reflexionar.")
        ]
    elif codigo in [71, 73, 75, 77, 85, 86]:  # Nieve
        opciones = [
            ("Nieve ❄️", "¡Está nevando! Abrígate bien y disfruta del paisaje.")
        ]
    elif codigo in [95, 96, 99]:  # Tormenta
        opciones = [
            ("Tormenta ⚡", "Cuidado con los rayos. Mejor quedarse a cubierto.")
        ]
    else:
        opciones = [("Variable 🌈", "Disfruta del día al máximo.")]
        
    st.session_state.consejo_miguel = random.choice(opciones)
    return st.session_state.consejo_miguel

# --- CACHÉ DE INFORMACIÓN DE APIs (CON PLACAS DE REDUNDANCIA) ---
@st.cache_data(ttl=600)
def cargar_info(la, lo):
    ciudad = None
    
    # Plan A: BigDataCloud (Estable y rápido)
    try:
        url_bdc = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={la}&longitude={lo}&localityLanguage=es"
        response = requests.get(url_bdc, timeout=4)
        if response.status_code == 200:
            g = response.json()
            ciudad = g.get('city') or g.get('locality') or g.get('principalSubdivision')
    except Exception:
        pass
        
    # Plan B: OpenStreetMap (Respaldo)
    if not ciudad:
        try:
            user_agent = f"MiguelAppGeolocator_{random.randint(1000, 9999)}"
            url_osm = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}"
            response = requests.get(url_osm, headers={'User-Agent': user_agent}, timeout=4)
            if response.status_code == 200:
                g = response.json()
                address = g.get('address', {})
                ciudad = address.get('city') or \
                         address.get('town') or \
                         address.get('village') or \
                         address.get('hamlet') or \
                         address.get('suburb') or \
                         address.get('municipality') or \
                         address.get('county') or \
                         address.get('state')
        except Exception:
            pass

    if not ciudad:
        ciudad = "Ubicación Detectada"
        
    # Obtener Clima
    try:
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true"
        cl = requests.get(url_clima, timeout=5).json()
        temp = cl['current_weather']['temperature']
        cod = cl['current_weather']['weathercode']
    except Exception:
        temp = "--"
        cod = -1
        
    return ciudad, temp, cod

# --- APLICACIÓN PRINCIPAL ---
st.title("🚀 ia inteligente sencilla de miguel")

# Solicitar geolocalización
with st.spinner("📍 Buscando señal GPS del dispositivo..."):
    loc = get_geolocation()

if loc is None:
    st.info("📍 Esperando permiso de ubicación. Por favor, pulsa 'Permitir' si aparece el aviso del navegador.")
    st.stop()

try:
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Zona Horaria según coordenadas
        nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona_local = pytz.timezone(nombre_zona)

        # Cargar ciudad y clima real
        ciudad, temp, cod = cargar_info(lat, lon)

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
        st.caption(f"v4.6 • Zona horaria: {nombre_zona} ({tipo_horario})")

    else:
        st.error("No se ha podido acceder a los datos de la ubicación.")

except Exception as e:
    st.error("Ocurrió un error inesperado al procesar los datos de ubicación.")
