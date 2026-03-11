import streamlit as st
import requests
from datetime import datetime
import random
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="IA de Miguel", page_icon="🌤️")

st.title("🚀 ia inteligente sencilla de miguel")

# --- LÓGICA DE CONSEJOS (Se queda fijo al cargar) ---
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

# --- OBTENCIÓN DE UBICACIÓN ---
loc = get_geolocation()

if loc:
    try:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
        # 1. Obtener Ciudad y Clima (Cacheado para que no tarde)
        @st.cache_data(ttl=600)
        def obtener_info_local(la, lo):
            # Ciudad
            geo = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={la}&lon={lo}", headers={'User-Agent': 'MiguelApp'}).json()
            ciudad = geo.get('address', {}).get('city') or geo.get('address', {}).get('town') or geo.get('address', {}).get('village') or "Tu zona"
            # Clima
            clima = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={la}&longitude={lo}&current_weather=true").json()
            return ciudad, clima['current_weather']['temperature'], clima['current_weather']['weathercode']

        ciudad, temp, codigo_clima = obtener_info_local(lat, lon)

        # 2. Diseño del Reloj Fluido (Segundos en movimiento)
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 22px; opacity: 0.8;">📍 {ciudad}</p>
                <h1 id="reloj_pro" style="font-size: 90px; font-weight: 200; margin: 10px 0;">00:00:00</h1>
                <p id="fecha_pro" style="opacity: 0.6; font-size: 18px;"></p>
            </div>
            <script>
                function moverReloj() {{
                    const ahora = new Date();
                    document.getElementById('reloj_pro').innerHTML = ahora.toLocaleTimeString('es-ES');
                    document.getElementById('fecha_pro').innerHTML = ahora.toLocaleDateString('es-ES', {{ day: '2-digit', month: '2-digit', year: 'numeric' }});
                }}
                setInterval(moverReloj, 1000);
                moverReloj();
            </script>
        """, unsafe_allow_html=True)

        # 3. Métricas y Consejos
        st.metric("🌡️ Temperatura", f"{temp} °C")
        
        estado, consejo = obtener_consejo_estatico(codigo_clima)
        st.info(f"**{estado}** — {consejo}")

    except Exception as e:
        st.error("Conectando con la ubicación...")
else:
    st.info("📍 Haz clic en 'Allow' (Permitir) para que Miguel te localice.")

st.divider()
st.caption("v4.2 • Reloj nativo y ubicación precisa")
