import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation # Esto es para el GPS real

st.set_page_config(page_title="IA de Miguel", page_icon="📍")

st.title("🚀 ia inteligente sencilla de miguel")

# 1. Intentamos sacar el GPS real del dispositivo (móvil o PC)
loc = get_geolocation()

def obtener_datos(lat_gps=None, lon_gps=None):
    try:
        if lat_gps and lon_gps:
            # Si tenemos GPS, lo usamos directamente
            lat, lon = lat_gps, lon_gps
            # Buscamos el nombre de la ciudad por coordenadas
            geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
            ciudad = requests.get(geo_url, headers={'User-Agent': 'MiguelApp'}).json().get('address', {}).get('city', 'Tu zona')
        else:
            # Si no hay GPS, usamos IP pero bloqueando los servidores de Google
            res = requests.get('http://ip-api.com/json/').json()
            if "Google" in res.get('org', ''):
                # Si detecta Google, forzamos tu zona real (Mallorca)
                ciudad, lat, lon = "Palma de Mallorca", 39.5693, 2.6502
            else:
                ciudad, lat, lon = res.get('city'), res.get('lat'), res.get('lon')

        # Hora exacta según las coordenadas
        tf = TimezoneFinder()
        zona_nombre = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona = pytz.timezone(zona_nombre)
        hora = datetime.now(zona).strftime('%H:%M:%S')

        # Clima real
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        
        return ciudad, temp, hora
    except:
        return "Detectando...", "--", "--:--:--"

# Si el navegador nos da la ubicación:
if loc:
    lat_real = loc['coords']['latitude']
    lon_real = loc['coords']['longitude']
    ciudad, temp, hora = obtener_datos(lat_real, lon_real)
else:
    st.warning("Pulsa 'Allow' (Permitir) arriba si quieres precisión GPS, o espera a que detecte tu IP...")
    ciudad, temp, hora = obtener_datos()

st.divider()
c1, c2 = st.columns(2)
c1.metric("📍 Vives en", ciudad)
c2.metric("🌡️ Temperatura", f"{temp} °C")

st.subheader(f"🕒 Tu hora exacta: {hora}")
st.success(f"💡 **Consejo de Miguel:** ¡Disfruta de este momento en {ciudad}!")
