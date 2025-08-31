import streamlit as st
import os

st.set_page_config(page_title="Plataforma Lamela C.F.", layout="wide", initial_sidebar_state="collapsed")

# --- Estilos globales ---
st.markdown("""
<style>
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 6rem !important;
        padding-right: 6rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    .main {
        padding: 0 !important;
    }

    header, footer {
        visibility: hidden;
    }

    .boton-app {
        display: block;
        text-align: center;
        background-color: #f9f9f9;
        padding: 24px 16px;
        border-radius: 16px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        font-size: 1.1rem;
        font-weight: bold;
        border-left: 6px solid #000000;
        transition: all 0.2s ease-in-out;
        width: 100%;
        color: #000000 !important;
        text-decoration: none !important;
    }

    .boton-app:hover {
        background-color: #e0e0e0;
        transform: scale(1.02);
        cursor: pointer;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Cabecera ---
col_logo, col_titulo = st.columns([1, 5], gap="small")

with col_logo:
    escudo_path = os.path.join(os.path.dirname(__file__), "escudo.png")
    st.image(escudo_path, width=100)

with col_titulo:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 100px;'>
            <h1 style='margin: 0 ; margin-left: 6rem; font-size: 3rem;'> Plataforma de Datos del Lamela C.F.</h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #555; font-size: 1.2rem;'>Bienvenido. Selecciona una sección para comenzar.</p>", unsafe_allow_html=True)

# --- Botones (sin navegación, todos iguales) ---
botones = [
    "⚽ Partidos y Clasificación",
    "📈 Análisis Equipos",
    "👤 Análisis Jugadores",
    "📝 Sanciones Internas",
    "✅ Control de Asistencia",
    "📚 Histórico Entrenamientos"
]

# --- Mostrar botones en filas de 3 con separación entre filas ---
for i in range(0, len(botones), 3):
    if i == 3:
        # Añadir espacio antes de la segunda fila
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    for col, index in zip([col1, col2, col3], [i, i+1, i+2]):
        if index < len(botones):
            with col:
                st.markdown(f"<div class='boton-app'>{botones[index]}</div>", unsafe_allow_html=True)


# --- Línea divisoria ---
st.markdown("<hr style='margin-top: 3rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

# --- Visión / resumen ---
st.markdown("""
<div style='max-width: 850px; margin: auto; text-align: center; font-size: 0.88rem; color: #444; line-height: 1.4; padding: 0 1rem;'>
    <h4 style='color: #000;'>🧭 ¿Qué es esta plataforma?</h4>
    <p>Una herramienta creada para <strong>profesionalizar el mejor club de la comarca</strong>, con datos que apoyan cada decisión deportiva y organizativa.</p>
    <p>Ofrece una visión centralizada para seguir la evolución del club, analizar rivales, gestionar entrenamientos, asistencia y sanciones.</p>
    <p>Es una plataforma viva, diseñada para crecer junto al equipo. <em>Porque cada dato cuenta, y cada paso suma.</em></p>
</div>
""", unsafe_allow_html=True)
