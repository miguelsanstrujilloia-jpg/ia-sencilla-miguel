import streamlit as st
import requests
from datetime import datetime
import random
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="IA de Miguel", page_icon="🌤️")

# Título
st.title("🚀 ia inteligente sencilla de miguel")

# --- LÓGICA DE CONSEJOS (Se queda fijo al cargar la página) ---
if 'consejo_miguel' not in st.session_state:
    st.session_state.consejo_miguel = None

def obtener_consejo_estatico(codigo):
    if st.session_state.consejo_miguel is None:
        mensajes = {
            0: [("Despejado ☀️", "¡Día top! Gafas de sol y a disfrutar."), 
                ("Despejado ☀️", "Cielo limpio, como tu futuro. ¡A por todas!")],
            1: [("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta.")],
            3: [("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
                ("Nublado ☁️", "¡No dejes que las nubes te quiten la sonrisa!")],
            61: [("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes.")],
        }
        opciones = mensajes.get(codigo, [("Variable 🌈", "Disfruta del día haga el tiempo que haga.")])
        st.session_state.consejo_miguel = random.choice(opciones)
    return st.session_state.consejo_miguel

# --- OBTENCIÓN DE DATOS ---
loc = get_geolocation()

if loc:
    try:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # Datos de Ciudad y Clima
        @st.cache_data(ttl=600)
        def obtener_info(la, lo):
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}", headers={'User-Agent': 'MiguelApp'}).json()
            c = g.get('address', {}).get('city') or g.get('address', {}).get('town') or g.get('address', {}).get('village') or "Tu zona"
            cl = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true").json()
            return c, cl['current_weather']['temperature'], cl['current_weather']['weathercode']

        ciudad, temp, codigo_clima = obtener_info(lat, lon)

        # Mostrar Ciudad y Fecha
        st.write(f"📍 **Estás en:** {ciudad} | 📅 {datetime.now().strftime('%d/%m/%Y')}")

        # --- RELOJ QUE PASA SEGUNDO A SEGUNDO ---
        # Usamos un contenedor vacío que se actualiza solo
        placeholder_reloj = st.empty()
        
        # Consejo de Miguel (Fijo)
        estado, consejo = obtener_consejo_estatico(codigo_clima)
        
        st.metric("🌡️ Temperatura", f"{temp} °C")
        st.info(f"**{estado}** — {consejo}")

        # Bucle para el reloj (esto hará que los segundos pasen)
        while True:
            ahora = datetime.now().strftime('%H:%M:%S')
            placeholder_reloj.markdown(f"<h1 style='text-align: center; font-size: 100px; font-weight: 200;'>{ahora}</h1>", unsafe_allow_html=True)
            time.sleep(1)

    except Exception as e:
        st.error("Conectando con Marratxí...")
else:
    st.info("📍 Haz clic en 'Allow' (Permitir) para que Miguel te localice.")

st.divider()
st.caption("v4.3 • Reloj en movimiento infinito")
