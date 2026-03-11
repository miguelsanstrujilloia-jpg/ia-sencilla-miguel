import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="IA de Miguel", page_icon="🕒")

# Refresco cada 1 segundo (1000 milisegundos) para que el reloj corra
st_autorefresh(interval=1000, key="reloj_segundos")

st.title("🚀 ia inteligente sencilla de miguel")

loc = get_geolocation()

def obtener_datos_completos(lat, lon):
    try:
        # 1. Ubicación en el idioma del dispositivo (quitamos el forzado de idioma)
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        direccion = res_geo.get('address', {})
        
        # Intentamos sacar el nombre del lugar
        ciudad = direccion.get('city') or direccion.get('town') or direccion.get('village') or direccion.get('suburb') or "..."
        pais = direccion.get('country', '')

        # 2. Hora exacta (se actualizará cada segundo)
        tf = TimezoneFinder()
        zona_nombre = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona = pytz.timezone(zona_nombre)
        hora = datetime.now(zona).strftime('%H:%M:%S')

        # 3. Clima
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']

        info_clima = {
            0: ("Despejado ☀️", "¡Día top! Gafas de sol puestas."),
            1: ("Casi despejado 🌤️", "Buen tiempo para salir."),
            2: ("Nubes y claros ⛅", "El sol va y viene."),
            3: ("Nublado ☁️", "Día gris, pero tú le das color."),
            61: ("Lluvia 🌧️", "Coge el paraguas, Miguel avisa."),
            95: ("Tormenta ⛈️", "Mejor quédate a cubierto.")
        }
        estado, consejo = info_clima.get(codigo, ("Variable 🌈", "Disfruta del día."))
        
        return ciudad, pais, temp, hora, estado, consejo
    except:
        return "Localizando...", "", "--", "--:--:--", "...", "..."

st.divider()

if loc:
    lat_r = loc['coords']['latitude']
    lon_r = loc['coords']['longitude']
    ciudad, pais, temp, hora, estado, consejo = obtener_datos_completos(lat_r, lon_r)
    
    col1, col2 = st.columns(2)
    col1.metric("📍 Estás en:", ciudad)
    col2.metric("🌡️ Temperatura:", f"{temp} °C")
    
    st.write(f"🌍 **País:** {pais}")
    
    # La hora ahora cambiará cada segundo visualmente
    st.markdown(f"## 🕒 Hora exacta: `{hora}`")
    
    st.info(f"**Estado:** {estado}")
    st.success(f"💡 **Consejo:** {consejo}")
else:
    st.info("Buscando señal GPS... Por favor, pulsa 'Allow' (Permitir).")

st.divider()
st.caption("Miguel IA • v3.5 Tiempo Real")
