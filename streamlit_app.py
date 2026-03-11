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

# --- LÓGICA DE CONSEJOS (Solo cambia al refrescar) ---
def obtener_consejo(codigo):
    mensajes = {
        0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
        1: [("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta."),
            ("Casi despejado 🌤️", "El sol está ahí fuera esperándote.")],
        3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
        61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
             ("Lluvia 🌧️", "Día de lluvia, día de suerte. ¡A tope!")],
    }
    # Si el código no está, mensaje genérico
    opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del día haga el tiempo que haga.")])
    return random.choice(opciones)

# --- OBTENCIÓN DE DATOS ---
loc = get_geolocation()

if loc:
    try:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        
        # 1. Datos de ubicación y clima
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        ciudad = res_geo.get('address', {}).get('city') or res_geo.get('address', {}).get('town') or "Tu ubicación"
        
        clima_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        clima_res = requests.get(clima_url).json()
        temp = clima_res['current_weather']['temperature']
        codigo_clima = clima_res['current_weather']['weathercode']
        
        # 2. Hora y Fecha (Estática)
        tf = TimezoneFinder()
        zona_nombre = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona = pytz.timezone(zona_nombre)
        ahora = datetime.now(zona)

        # --- DISEÑO ---
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("📍 Estás en:", ciudad)
        col2.metric("🌡️ Temp:", f"{temp} °C")
        
        # Reloj sencillo en el color de la página
        st.markdown(f"""
            <div style="text-align: center; margin: 30px 0;">
                <p style="margin: 0; font-size: 20px; opacity: 0.6;">{ahora.strftime('%d/%m/%Y')}</p>
                <h1 style="font-size: 90px; margin: 0; font-weight: 300;">{ahora.strftime('%H:%M')}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Consejo de Miguel
        estado, mensaje = obtener_consejo(codigo_clima)
        st.info(f"**{estado}** — {mensaje}")
        
    except Exception as e:
        st.error("Espera un momento, la IA está conectando...")
else:
    st.info("📍 Haz clic en 'Allow' (Permitir) arriba para localizarte.")

st.divider()
st.caption("v4.0 • Versión Estable y Sencilla")
