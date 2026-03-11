import streamlit as st
import requests
from datetime import datetime
import pytz
import random
import time
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation

# 1. Configuración y OCULTAR MENÚS
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

st.title("🚀 ia inteligente sencilla de miguel")

# --- CONSEJOS FIJOS ---
if 'consejo_miguel' not in st.session_state:
    st.session_state.consejo_miguel = None

def obtener_consejo(codigo):
    if st.session_state.consejo_miguel is None:
        mensajes = {
            0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
                ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
            3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
                ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
            61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes.")],
        }
        opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del día.")])
        st.session_state.consejo_miguel = random.choice(opciones)
    return st.session_state.consejo_miguel

# --- DATOS Y RELOJ ---
loc = get_geolocation()

if loc is None:
    st.info("📍 Buscando señal GPS... Pulsa 'Permitir' si aparece el aviso.")
    time.sleep(2)
    st.stop()

try:
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Obtener Zona Horaria automática según GPS
        tf = TimezoneFinder()
        nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona_local = pytz.timezone(nombre_zona)

        @st.cache_data(ttl=600)
        def cargar_info(la, lo):
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}", headers={'User-Agent': 'MiguelApp'}).json()
            c = g.get('address', {}).get('city') or g.get('address', {}).get('town') or g.get('address', {}).get('village') or "Tu ubicación"
            cl = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true").json()
            return c, cl['current_weather']['temperature'], cl['current_weather']['weathercode']

        ciudad, temp, cod = cargar_info(lat, lon)

        st.write(f"📍 **{ciudad}** | 📅 {datetime.now(zona_local).strftime('%d/%m/%Y')}")

        reloj_valla = st.empty()
        st.metric("🌡️ Temperatura", f"{temp} °C")
        
        estado, mensaje = obtener_consejo(cod)
        st.info(f"**{estado}** — {mensaje}")

        # Bucle para el reloj con la hora local correcta
        while True:
            # datetime.now(zona_local) asegura que si cambia la hora oficial, el reloj cambia solo
            ahora_local = datetime.now(zona_local).strftime('%H:%M:%S')
            reloj_valla.markdown(f"<h1 style='text-align: center; font-size: 100px; font-weight: 200;'>{ahora_local}</h1>", unsafe_allow_html=True)
            time.sleep(1)
    else:
        st.error("No se ha podido acceder a la ubicación")

except Exception as e:
    st.error("No se ha podido acceder a la ubicación")

st.divider()
st.caption(f"v4.6 • Zona horaria activa: {nombre_zona}")
