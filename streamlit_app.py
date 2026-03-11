import streamlit as st
import requests
from datetime import datetime
import pytz
import random
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh

# Configuración de página limpia
st.set_page_config(page_title="IA de Miguel", page_icon="⌚")

# El reloj se actualiza cada segundo
st_autorefresh(interval=1000, key="reloj_segundos")

st.title("🚀 ia inteligente sencilla de miguel")

# --- LÓGICA DE MENSAJES (Se ejecuta solo al cargar/refrescar) ---
if 'mensaje_fijo' not in st.session_state:
    st.session_state.mensaje_fijo = {}

def elegir_mensaje(codigo):
    if codigo not in st.session_state.mensaje_fijo:
        mensajes = {
            0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
                ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
            1: [("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta."),
                ("Casi despejado 🌤️", "El sol está ahí fuera esperándote.")],
            3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
                ("Nublado ☁️", "Aunque no se vea el sol, tú brillas igual."),
                ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
            61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
                 ("Lluvia 🌧️", "Día de lluvia, día de suerte. ¡A tope!")],
        }
        # Si el clima no está en la lista, mensaje genérico
        opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del momento.")])
        st.session_state.mensaje_fijo = random.choice(opciones)
    return st.session_state.mensaje_fijo

# --- OBTENCIÓN DE DATOS ---
loc = get_geolocation()

@st.cache_data(ttl=600)
def obtener_datos(lat, lon):
    try:
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        ciudad = res_geo.get('address', {}).get('city') or res_geo.get('address', {}).get('town') or "Tu ubicación"
        
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']
        return ciudad, temp, codigo
    except:
        return "Cargando...", "--", 0

st.divider()

if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    ciudad, temp, codigo = obtener_datos(lat, lon)
    
    # Hora y Fecha (esto sí cambia cada segundo)
    tf = TimezoneFinder()
    zona = pytz.timezone(tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid')
    ahora = datetime.now(zona)
    
    # Diseño Minimalista
    st.text(f"📍 {ciudad} | {ahora.strftime('%d/%m/%Y')}")
    
    # Reloj simple sin cuadros de colores
    st.markdown(f"<h1 style='text-align: center; font-size: 100px; font-weight: 200;'>{ahora.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)
    
    st.metric("Temperatura", f"{temp} °C")
    
    # Mensaje fijo (solo cambia al refrescar la web)
    estado, consejo = elegir_mensaje(codigo)
    
    st.write("---")
    st.info(f"**{estado}** — {consejo}")

else:
    st.info("Esperando señal GPS... Por favor, permite la ubicación.")

st.caption("v3.8 • Reloj fluido y consejos estáticos")
