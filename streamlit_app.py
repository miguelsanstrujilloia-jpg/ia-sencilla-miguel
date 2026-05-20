import streamlit as st
import requests
from datetime import datetime
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

# Instanciar TimezoneFinder una sola vez a nivel de módulo (ahorra CPU y RAM)
tf = TimezoneFinder()

# --- CONSEJOS FIJOS SEGÚN CLIMA (WMO CODES) ---
if 'consejo_miguel' not in st.session_state:
    st.session_state.consejo_miguel = None

def obtener_consejo(codigo):
    if st.session_state.consejo_miguel is not None:
        return st.session_state.consejo_miguel
        
    # Mapeo y agrupación de códigos WMO de Open-Meteo
    if codigo == 0:  # Despejado
        opciones = [
            ("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")
        ]
    elif codigo in [1, 2, 3, 45, 48]:  # Parcialmente nublado, nublado, niebla
        opciones = [
            ("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")
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

# --- CACHÉ DE INFORMACIÓN DE APIs (Definido a nivel de módulo) ---
@st.cache_data(ttl=600)
def cargar_info(la, lo):
    # 1. Obtener Ciudad (OSM Nominatim) con manejo de errores individual
    try:
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}"
        g = requests.get(url_geo, headers={'User-Agent': 'MiguelApp/4.6'}, timeout=5).json()
        address = g.get('address', {})
        ciudad = address.get('city') or address.get('town') or address.get('village') or "Tu ubicación"
    except Exception:
        ciudad = "Tu ubicación"
        
    # 2. Obtener Clima (Open-Meteo) con manejo de errores individual
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

# Solicitar geolocalización sin bloquear el servidor
with st.spinner("📍 Buscando señal GPS..."):
    loc = get_geolocation()

if loc is None:
    st.info("📍 Esperando permiso de ubicación. Por favor, pulsa 'Permitir' si aparece el aviso del navegador.")
    st.stop()

try:
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Determinar zona horaria
        nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona_local = pytz.timezone(nombre_zona)

        # Cargar datos desde APIs (usando caché)
        ciudad, temp, cod = cargar_info(lat, lon)

        # Mostrar Ubicación y Fecha
        fecha_actual = datetime.now(zona_local).strftime('%d/%m/%Y')
        st.write(f"📍 **{ciudad}** | 📅 {fecha_actual}")

        # --- RELOJ DIGITAL EN JAVASCRIPT ---
        # Ejecuta la hora en el cliente sin recargar el servidor de Streamlit
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
        st.caption(f"v4.6 • Zona horaria activa: {nombre_zona}")

    else:
        st.error("No se ha podido acceder a los datos de la ubicación.")

except Exception as e:
    st.error(f"Ocurrió un error inesperado al procesar los datos.")
