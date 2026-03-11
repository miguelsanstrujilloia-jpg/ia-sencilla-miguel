import streamlit as st
import requests
from datetime import datetime
import pytz

# Configuración de la pestaña del navegador
st.set_page_config(page_title="IA de Miguel", page_icon="🤖")

# El título que me has pedido
st.title("🤖 IA inteligente sencilla de miguel")

def obtener_datos_por_ip():
    try:
        # Detecta ciudad y coordenadas por la conexión a internet
        geo_res = requests.get('https://ipapi.co/json/', timeout=3).json()
        ciudad = geo_res.get('city', 'tu ubicación')
        lat = geo_res.get('latitude', 39.5693)
        lon = geo_res.get('longitude', 2.6502)
        
        # Pide el clima real basado en esas coordenadas
        clima_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        clima_res = requests.get(clima_url, timeout=3).json()
        temp = clima_res['current_weather']['temperature']
        
        return ciudad, temp
    except:
        return None, None

st.write(f"¡Hola! Analizando tu conexión...")

ciudad, temperatura = obtener_datos_por_ip()

if ciudad and temperatura:
    st.metric(label=f"Temperatura en {ciudad}", value=f"{temperatura} °C")
    st.write(f"📍 Veo que estás cerca de **{ciudad}**.")
else:
    st.warning("No he podido detectar tu ubicación exacta, pero el sistema está activo.")

# Botones de funciones
col1, col2 = st.columns(2)

with col1:
    if st.button('🕒 Ver Hora Local'):
        zona = pytz.timezone('Europe/Madrid')
        st.success(f"Son las {datetime.now(zona).strftime('%H:%M:%S')}")

with col2:
    if st.button('📅 Ver Fecha'):
        st.info(f"Hoy es {datetime.now().strftime('%d/%m/%Y')}")

st.write("---")
st.caption("Creado por Miguel - Esta IA es inteligente y sencilla.")
