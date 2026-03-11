import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh

# Configuración de página
st.set_page_config(page_title="IA de Miguel - Live", page_icon="⌚", layout="centered")

# Refresco cada 1 segundo para el movimiento constante
st_autorefresh(interval=1000, key="reloj_infinito")

st.title("🚀 ia inteligente sencilla de miguel")

# Función para traducir días al español (opcional, ya que pediste idioma del dispositivo)
# Pero para asegurar que se vea bien, usamos el formato estándar
def obtener_fecha_larga(zona):
    ahora = datetime.now(zona)
    # Formato: Miércoles, 11 de Marzo de 2026
    return ahora.strftime("%A, %d %B %Y")

loc = get_geolocation()

@st.cache_data(ttl=600) # El clima y ciudad solo se actualizan cada 10 min para no saturar
def obtener_datos_estaticos(lat, lon):
    try:
        # Ubicación en idioma del dispositivo
        url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res_geo = requests.get(url_geo, headers={'User-Agent': 'MiguelApp'}).json()
        direccion = res_geo.get('address', {})
        ciudad = direccion.get('city') or direccion.get('town') or direccion.get('village') or "..."
        pais = direccion.get('country', '')

        # Clima
        clima_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']
        
        return ciudad, pais, temp, codigo
    except:
        return "Localizando...", "", "--", 0

st.divider()

if loc:
    lat_r, lon_r = loc['coords']['latitude'], loc['coords']['longitude']
    
    # Datos que no cambian cada segundo (Ciudad, Clima)
    ciudad, pais, temp, codigo = obtener_datos_estaticos(lat_r, lon_r)
    
    # Datos que SÍ cambian cada segundo (Hora y Fecha)
    tf = TimezoneFinder()
    zona_nombre = tf.timezone_at(lng=lon_r, lat=lat_r) or 'Europe/Madrid'
    zona = pytz.timezone(zona_nombre)
    
    hora_actual = datetime.now(zona).strftime('%H:%M:%S')
    fecha_actual = datetime.now(zona).strftime('%d/%m/%Y') # Puedes usar obtener_fecha_larga si prefieres texto

    # Diseño
    col1, col2 = st.columns(2)
    col1.metric("📍 Ubicación", ciudad)
    col2.metric("🌡️ Temperatura", f"{temp} °C")
    
    st.write(f"🌍 **País:** {pais} | 📅 **Fecha:** {fecha_actual}")
    
    # Reloj protagonista
    st.markdown(f"""
        <div style="background-color: #0e1117; padding: 20px; border-radius: 10px; border: 2px solid #4CAF50; text-align: center;">
            <h1 style="color: #4CAF50; margin: 0; font-family: monospace; font-size: 80px;">{hora_actual}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Lógica de consejos
    info_clima = {0: "Despejado ☀️", 1: "Casi despejado 🌤️", 3: "Nublado ☁️", 61: "Lluvia 🌧️"}
    estado = info_clima.get(codigo, "Variable 🌈")
    
    st.info(f"**Estado actual:** {estado}")
    st.success(f"💡 **Consejo de Miguel:** La aplicación se actualizará sola si cambias de ciudad o si pasa el tiempo.")

else:
    st.warning("Cargando reloj y GPS... Por favor, acepta el permiso de ubicación.")

st.divider()
st.caption("Sistema de tiempo real infinito • v3.6")
