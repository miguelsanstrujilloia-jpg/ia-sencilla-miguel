import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh # Para el auto-refresco

st.set_page_config(page_title="IA de Miguel", page_icon="🌤️")

# Refrescar la app automáticamente cada 30 segundos
st_autorefresh(interval=30000, key="datarefresh")

st.title("🚀 ia inteligente sencilla de miguel")

loc = get_geolocation()

def obtener_datos_completos(lat, lon):
    try:
        # 1. Nombre del lugar exacto (con traducción al idioma local)
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&accept-language=es"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        direccion = res_geo.get('address', {})
        ciudad = direccion.get('city') or direccion.get('town') or direccion.get('village') or direccion.get('suburb') or "Tu zona"
        pais = direccion.get('country', '')

        # 2. Hora exacta según GPS
        tf = TimezoneFinder()
        zona_nombre = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona = pytz.timezone(zona_nombre)
        hora = datetime.now(zona).strftime('%H:%M:%S')

        # 3. Clima y código de estado
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']

        # 4. Consejos de Miguel
        info_clima = {
            0: ("Despejado ☀️", "¡Día top! Gafas de sol puestas."),
            1: ("Casi despejado 🌤️", "Buen tiempo para salir a dar una vuelta."),
            2: ("Nubes y claros ⛅", "El sol va y viene, se está a gusto."),
            3: ("Nublado ☁️", "Día gris, pero tú eres el crack que le da color."),
            45: ("Niebla 🌫️", "Ojo si sales, que no se ve ni un pimiento."),
            61: ("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
            95: ("Tormenta ⛈️", "¡Rayos! Mejor quédate a cubierto.")
        }
        
        estado, consejo = info_clima.get(codigo, ("Variable 🌈", "Disfruta del día."))
        
        return ciudad, pais, temp, hora, estado, consejo
    except:
        return "Cargando...", "", "--", "--:--:--", "Variable", "Reintentando..."

st.divider()

if loc:
    lat_real = loc['coords']['latitude']
    lon_real = loc['coords']['longitude']
    ciudad, pais, temp, hora, estado, consejo = obtener_datos_completos(lat_real, lon_real)
    
    col1, col2 = st.columns(2)
    col1.metric("📍 Estás en:", f"{ciudad}")
    col2.metric("🌡️ Temperatura:", f"{temp} °C")
    
    st.write(f"🌍 **País:** {pais}")
    st.markdown(f"### 🕒 Hora exacta: `{hora}`")
    
    st.info(f"**Estado del cielo:** {estado}")
    st.success(f"💡 **Consejo de Miguel:** {consejo}")
else:
    st.warning("Esperando ubicación... Si estás fuera de España, asegúrate de permitir el GPS.")

st.divider()
st.caption(f"Actualizado automáticamente a las: {datetime.now().strftime('%H:%M:%S')}")
