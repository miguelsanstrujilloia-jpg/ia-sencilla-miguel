import streamlit as st
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# Configuración visual
st.set_page_config(page_title="IA de Miguel", page_icon="🚀", layout="centered")

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ia inteligente sencilla de miguel")
st.write("---")

def obtener_datos():
    try:
        # NUEVO MOTOR DE UBICACIÓN (Más preciso)
        geo_res = requests.get('http://ip-api.com/json/', timeout=5).json()
        
        # Si el motor detecta la ciudad, la usamos
        if geo_res.get('status') == 'success':
            ciudad = geo_res.get('city')
            lat = geo_res.get('lat')
            lon = geo_res.get('lon')
        else:
            ciudad, lat, lon = "Palma", 39.5693, 2.6502

        # Zona Horaria
        tf = TimezoneFinder()
        nombre_zona = tf.timezone_at(lng=lon, lat=lat) or 'Europe/Madrid'
        zona_local = pytz.timezone(nombre_zona)
        hora_local = datetime.now(zona_local).strftime('%H:%M:%S')

        # Clima
        clima_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        clima_res = requests.get(clima_url).json()
        temp = clima_res['current_weather']['temperature']
        codigo = clima_res['current_weather']['weathercode']

        # Diccionario de consejos
        info_clima = {
            0: ("Despejado ☀️", "¡Día perfecto! Gafas de sol obligatorias."),
            1: ("Casi despejado 🌤️", "Hace buen tiempo, ¡aprovéchalo!"),
            2: ("Nubes y claros ⛅", "Día agradable para pasear."),
            3: ("Nublado ☁️", "Está gris, pero tú dale color al día."),
            61: ("Lluvia 🌧️", "Coge el paraguas, Miguel no quiere que te mojes."),
            95: ("Tormenta ⛈️", "¡Rayos! Mejor quédate a cubierto.")
        }
        estado, consejo = info_clima.get(codigo, ("Variable 🌈", "Disfruta del día."))
        
        return ciudad, temp, estado, consejo, hora_local
    except:
        return "Conectando...", "--", "Desconocido", "Reintentando...", "--:--:--"

# Ejecutar y mostrar
ciudad, temp, estado, consejo, hora = obtener_datos()

# Diseño en columnas
c1, c2 = st.columns(2)
with c1:
    st.metric(label="📍 Ciudad Detectada", value=ciudad)
with c2:
    st.metric(label="🌡️ Temperatura", value=f"{temp} °C")

st.markdown(f"### 🕒 Hora local: `{hora}`")

# Cuadros de información con colores
st.info(f"**Estado del cielo:** {estado}")
st.success(f"💡 **Consejo de Miguel:** {consejo}")

st.write("---")
st.caption("Hecho con ❤️ por Miguel • v3.0 Inteligente y Visual")
