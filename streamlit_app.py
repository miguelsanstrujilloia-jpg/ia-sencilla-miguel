import streamlit as st
import requests
from datetime import datetime
import pytz
import random
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation

# Configuración de página
st.set_page_config(page_title="IA de Miguel", page_icon="🌤️")

st.title("🚀 ia inteligente sencilla de miguel")

# --- LÓGICA DE MENSAJES (Cambia solo al cargar o refrescar) ---
def obtener_consejo_miguel(codigo):
    mensajes = {
        0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
        1: [("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta."),
            ("Casi despejado 🌤️", "El sol está ahí fuera esperándote.")],
        2: [("Nubes y claros ⛅", "El sol va y viene, se está a gusto.")],
        3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "Aunque no se vea el sol, tú brillas igual."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
        61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
             ("Lluvia 🌧️", "Día de lluvia, día de suerte. ¡A tope!")],
    }
    opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del momento.")])
    return random.choice(opciones)

# --- OBTENCIÓN DE DATOS ---
loc = get_geolocation()

if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    try:
        # Ubicación y Clima
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        ciudad = res_geo.get('address', {}).get('city') or res_geo.get('address', {}).get('town') or "Tu ubicación"
        
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']
        
        # Hora y Fecha (estática hasta el próximo refresco)
        tf = TimezoneFinder()
        zona = pytz.timezone(tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid')
        ahora = datetime.now(zona)
        
        # --- DISEÑO VISUAL ---
        st.divider()
        
        col1, col2 = st.columns(2)
        col1.metric("📍 Ubicación", ciudad)
        col2.metric("🌡️ Temperatura", f"{temp} °C")
        
        # Reloj sencillo que conjuga con el color del texto de la página
        st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <p style="margin: 0; opacity: 0.7;">{ahora.strftime('%d/%m/%Y')}</p>
                <h1 style="font-size: 80px; margin: 0;">{ahora.strftime('%H:%M')}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Consejo de Miguel
        estado, consejo = obtener_consejo_miguel(codigo)
        st.info(f"**{estado}** — {consejo}")
        
    except:
        st.error("Hubo un error al conectar con los satélites. Refresca la página.")

else:
    st.info("Esperando señal GPS... Por favor, permite la ubicación para ver tu hora y clima.")

st.divider()
st.caption("v3.9 • Diseño estable sin auto-refresco")
