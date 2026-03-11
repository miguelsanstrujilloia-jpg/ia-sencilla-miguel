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

# --- LÓGICA DE CONSEJOS (Solo cambian al cargar/refrescar) ---
if 'consejo_fijo' not in st.session_state:
    st.session_state.consejo_fijo = None

def obtener_consejo_estatico(codigo):
    if st.session_state.consejo_fijo is None:
        mensajes = {
            0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
                ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
            1: [("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta.")],
            3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
                ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
            61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes.")],
        }
        opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del día.")])
        st.session_state.consejo_fijo = random.choice(opciones)
    return st.session_state.consejo_fijo

# --- OBTENCIÓN DE DATOS ---
loc = get_geolocation()

if loc:
    try:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Datos de clima (cacheamos para que no sature la red)
        @st.cache_data(ttl=600)
        def datos_clima(la, lo):
            res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true").json()
            return res['current_weather']['temperature'], res['current_weather']['weathercode']
        
        temp, codigo_clima = datos_clima(lat, lon)
        
        # Zona horaria
        tf = TimezoneFinder()
        zona = pytz.timezone(tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid')
        
        # --- DISEÑO DEL RELOJ EN TIEMPO REAL ---
        # Este código HTML/JS hace que el reloj se mueva sin refrescar la página
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0; font-family: sans-serif;">
                <h1 id="reloj" style="font-size: 80px; font-weight: 200; margin: 0;">--:--:--</h1>
                <p style="opacity: 0.6; font-size: 20px;">{datetime.now(zona).strftime('%d/%m/%Y')}</p>
            </div>
            <script>
                function actualizarReloj() {{
                    const ahora = new Date();
                    const opciones = {{ timeZone: '{zona.zone}', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
                    const horaTexto = ahora.toLocaleTimeString('es-ES', opciones);
                    document.getElementById('reloj').innerHTML = horaTexto;
                }}
                setInterval(actualizarReloj, 1000);
                actualizarReloj();
            </script>
        """, unsafe_allow_html=True)

        st.metric("🌡️ Temperatura actual", f"{temp} °C")
        
        # Consejo de Miguel (se queda fijo hasta que refresquen)
        estado, mensaje = obtener_consejo_estatico(codigo_clima)
        st.info(f"**{estado}** — {mensaje}")
        
    except Exception as e:
        st.write("Cargando datos locales...")
else:
    st.info("📍 Esperando permiso de ubicación para activar el reloj...")

st.divider()
st.caption("v4.1 • Reloj fluido en tiempo real")
