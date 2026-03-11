import streamlit as st
import requests
from datetime import datetime
import pytz
import random # Para elegir mensajes al azar
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="IA de Miguel - Live", page_icon="🕒")

# Reloj cada 1 segundo
st_autorefresh(interval=1000, key="reloj_infinito")

st.title("🚀 ia inteligente sencilla de miguel")

loc = get_geolocation()

@st.cache_data(ttl=300) 
def obtener_datos_estaticos(lat, lon):
    try:
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        direccion = res_geo.get('address', {})
        ciudad = direccion.get('city') or direccion.get('town') or direccion.get('village') or "Tu zona"
        pais = direccion.get('country', '')

        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']
        
        return ciudad, pais, temp, codigo
    except:
        return "Cargando...", "", "--", 0

st.divider()

if loc:
    lat_r, lon_r = loc['coords']['latitude'], loc['coords']['longitude']
    ciudad, pais, temp, codigo = obtener_datos_estaticos(lat_r, lon_r)
    
    tf = TimezoneFinder()
    zona_nombre = tf.timezone_at(lng=lon_r, lat=lat_r) or 'Europe/Madrid'
    zona = pytz.timezone(zona_nombre)
    ahora = datetime.now(zona)
    
    hora_actual = ahora.strftime('%H:%M:%S')
    fecha_actual = ahora.strftime('%d/%m/%Y')

    col1, col2 = st.columns(2)
    col1.metric("📍 Estás en:", ciudad)
    col2.metric("🌡️ Temperatura:", f"{temp} °C")
    
    st.markdown(f"""
        <div style="background-color: #111; padding: 15px; border-radius: 15px; border: 2px solid #00ff00; text-align: center; margin: 10px 0;">
            <h1 style="color: #00ff00; margin: 0; font-family: 'Courier New', monospace; font-size: 70px;">{hora_actual}</h1>
            <p style="color: #00ff00; margin: 0;">{fecha_actual}</p>
        </div>
    """, unsafe_allow_html=True)

    # DICCIONARIO CON VARIOS MENSAJES POR CLIMA
    mensajes_variados = {
        0: [ # Despejado
            ("Despejado ☀️", "¡Día top! Gafas de sol y a comerse el mundo."),
            ("Despejado ☀️", "Ni una nube. ¡Hoy es un gran día para ser tú!"),
            ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")
        ],
        1: [ # Casi despejado
            ("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta."),
            ("Casi despejado 🌤️", "El sol está ahí fuera esperándote."),
            ("Casi despejado 🌤️", "Día perfecto para un café en una terraza.")
        ],
        3: [ # Nublado
            ("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            ("Nublado ☁️", "Aunque no se vea el sol, tú brillas igual."),
            ("Nublado ☁️", "Día de sofá, manta y peli... o de ser un crack fuera."),
            ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")
        ],
        61: [ # Lluvia
            ("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
            ("Lluvia 🌧️", "Día de lluvia, día de suerte. ¡A tope!"),
            ("Lluvia 🌧️", "Baila bajo la lluvia, pero no pilles un resfriado.")
        ]
    }

    # Elegimos un mensaje al azar de la lista según el código de clima
    # Si el código no está, usamos uno genérico
    opciones = mensajes_variados.get(codigo, [("Variable 🌈", "Disfruta del momento.")])
    estado, consejo = random.choice(opciones)
    
    st.info(f"**Cielo:** {estado}")
    st.success(f"💡 **Consejo de Miguel:** {consejo}")

else:
    st.warning("Buscando señal GPS... Pulsa 'Allow' (Permitir) para activar el reloj.")

st.divider()
st.caption("Sistema Live v3.7 • Mensajes aleatorios activados")
