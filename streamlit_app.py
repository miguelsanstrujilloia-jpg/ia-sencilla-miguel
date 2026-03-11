import streamlit as st
import requests
from datetime import datetime
import random
import time
from streamlit_js_eval import get_geolocation

# 1. Configuración y OCULTAR MENÚS (Para que no salga la barra de Fork/Stop)
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

if loc:
    try:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        @st.cache_data(ttl=600)
        def cargar_info(la, lo):
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}", headers={'User-Agent': 'MiguelApp'}).json()
            c = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "Tu ubicación"
            cl = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true").json()
            return c, cl['current_weather']['temperature'], cl['current_weather']['weathercode']

        ciudad, temp, cod = cargar_info(lat, lon)

        st.write(f"📍 **{ciudad}** | 📅 {datetime.now().strftime('%d/%m/%Y')}")

        # Contenedor para el reloj
        reloj_valla = st.empty()
        
        st.metric("🌡️ Temperatura", f"{temp} °C")
        estado, mensaje = obtener_consejo(cod)
        st.info(f"**{estado}** — {mensaje}")

        # Bucle infinito para los segundos
        while True:
            ahora = datetime.now().strftime('%H:%M:%S')
            reloj_valla.markdown(f"<h1 style='text-align: center; font-size: 100px; font-weight: 200;'>{ahora}</h1>", unsafe_allow_html=True)
            time.sleep(1)

    except:
        st.error("No se ha podido acceder a la ubicación")
else:
    # Mensaje en rojo si no hay permisos o no carga el GPS
    st.error("No se ha podido acceder a la ubicación")
    st.info("💡 Por favor, asegúrate de pulsar 'Permitir' cuando el navegador te pida la ubicación.")

st.divider()
st.caption("v4.4 • Control de errores de GPS activado")
