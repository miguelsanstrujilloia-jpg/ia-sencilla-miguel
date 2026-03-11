import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="IA de Miguel", page_icon="📍")

# Título con tu estilo
st.title("🚀 ia inteligente sencilla de miguel")

# Pedimos la ubicación GPS
loc = get_geolocation()

def obtener_datos_final(lat_gps, lon_gps):
    try:
        # Buscamos el nombre del sitio por coordenadas (Reverse Geocoding)
        # Usamos un servicio que suele dar el municipio o ciudad
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat_gps}&lon={lon_gps}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        
        # Intentamos sacar la ciudad, el pueblo o la villa
        direccion = res_geo.get('address', {})
        ciudad = direccion.get('city') or direccion.get('town') or direccion.get('village') or direccion.get('suburb') or "Tu ubicación"
        
        # Hora exacta según GPS
        tf = TimezoneFinder()
        zona_nombre = tf.timezone_at(lng=lon_gps, lat=lat_gps) or 'Europe/Madrid'
        zona = pytz.timezone(zona_nombre)
        hora = datetime.now(zona).strftime('%H:%M:%S')

        # Clima exacto
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat_gps}&longitude={lon_gps}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        
        return ciudad, temp, hora
    except:
        return "Cargando...", "--", "--:--:--"

st.divider()

if loc:
    # Si diste a permitir, usamos tus coordenadas reales
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    ciudad, temp, hora = obtener_datos_final(lat, lon)
    
    c1, c2 = st.columns(2)
    c1.metric("📍 Estás en:", ciudad)
    c2.metric("🌡️ Temperatura:", f"{temp} °C")
    
    st.subheader(f"🕒 Hora exacta: {hora}")
    st.success(f"💡 **Consejo de Miguel:** Estás viendo el tiempo real en {ciudad}.")
else:
    # Mensaje mientras esperas o si no das permiso
    st.info("Esperando ubicación... Haz clic en 'Allow' (Permitir) arriba para localizarte.")
    # Datos por defecto (Palma) por si no hay GPS
    st.metric("📍 Estás en:", "Palma (por defecto)")

st.divider()
st.caption("Miguel IA • v3.3 Precisión GPS")
