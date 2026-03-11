import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder # Nueva librería para la zona horaria

# Configuración de la pestaña
st.set_page_config(page_title="IA de Miguel", page_icon="🤖")

st.title("🤖 ia inteligente sencilla de miguel")

def obtener_datos_completos():
    try:
        # 1. Detectar ubicación y coordenadas por IP
        geo_res = requests.get('https://ipapi.co/json/', timeout=3).json()
        ciudad = geo_res.get('city', 'tu ubicación')
        lat = geo_res.get('latitude', 39.5693)
        lon = geo_res.get('longitude', 2.6502)
        
        # 2. Detectar la Zona Horaria exacta según las coordenadas
        tf = TimezoneFinder()
        nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona_local = pytz.timezone(nombre_zona)
        hora_local = datetime.now(zona_local).strftime('%H:%M:%S')
        
        # 3. Pedir clima detallado
        clima_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        clima_res = requests.get(clima_url, timeout=3).json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']
        
        # Diccionario de consejos
        info_clima = {
            0: ("Despejado ☀️", "¡Día genial! Gafas de sol listas."),
            1: ("Casi despejado 🌤️", "Buen tiempo para pasear."),
            3: ("Nublado ☁️", "Día gris, ideal para un café."),
            61: ("Lluvia 🌧️", "Coge el paraguas, Miguel avisa."),
            95: ("Tormenta ⛈️", "Mejor quédate en casa.")
        }
        estado, consejo = info_clima.get(codigo, ("Variable 🌈", "Disfruta del día."))
        
        return ciudad, temp, estado, consejo, hora_local
    except:
        return "Desconocida", "--", "N/A", "Sin conexión", "--:--:--"

st.write("---")
ciudad, temp, estado, consejo, hora = obtener_datos_completos()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📍 Estás en:", value=ciudad)
with col2:
    st.metric(label="🌡️ Temperatura:", value=f"{temp} °C")

st.info(f"**Estado:** {estado} | **Hora Local:** {hora}")
st.success(f"💡 **Consejo de Miguel:** {consejo}")

st.write("---")
st.caption("ia inteligente sencilla de miguel • Detecta tu ciudad y tu hora estés donde estés.")
