import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuración inicial ---
st.set_page_config(page_title="Control de Asistencia", layout="wide")

# --- Estilos globales ---
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        padding-left: 6rem !important;
        padding-right: 6rem !important;
    }
    header, footer {visibility: hidden;}
    .kpi-box {
        background-color: #f9f9f9;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 8px;
        border-left: 5px solid #000000;
    }
</style>
""", unsafe_allow_html=True)


# --- Función auxiliar para KPI ---
def kpi_box(label, value):
    st.markdown(f"""
        <div class='kpi-box'>
            <div style='font-size: 0.85rem; color: #555;'>{label}</div>
            <div style='font-size: 1.4rem; font-weight: bold; color: #222;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Cargar datos ---
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)   # carpeta donde está Asistencia.py
    ruta = os.path.join(base_dir, "Data", "Control_Asistencia.xlsx")
    return pd.read_excel(ruta)


df = load_data()

# --- Configuración inicial ---
st.set_page_config(page_title="Control de Asistencia", layout="wide")

# --- Título principal ---
st.title("📊 Control de Asistencia a Entrenamientos")


# --- Transformar datos ---
# Jugadores en fila, sesiones en columnas
jugadores = df.iloc[:, 0]
sesiones = df.columns[1:]

# Convertir "x" (falta) en 0 y vacío en 1 (asistió)
df_asistencia = df.copy()
for col in sesiones:
    df_asistencia[col] = df_asistencia[col].apply(lambda x: 0 if str(x).strip().lower() == "x" else 1)

# --- KPIs generales ---
total_sesiones = len(sesiones)
total_jugadores = len(jugadores)
total_registros = total_sesiones * total_jugadores
total_asistencias = df_asistencia[sesiones].sum().sum()
total_faltas = total_registros - total_asistencias
pct_asistencia = round((total_asistencias / total_registros) * 100, 1)

c1, c2, c3 = st.columns(3)
with c1: kpi_box("📅 Total sesiones", total_sesiones)
with c2: kpi_box("👥 Jugadores", total_jugadores)
with c3: kpi_box("✅ Asistencia global", f"{pct_asistencia}%")

# --- % asistencia por jugador ---
st.markdown("<br><h4>📊 Asistencia por jugador</h4>", unsafe_allow_html=True)


# Calcular entrenamientos presentes y porcentaje
asistencias_abs = df_asistencia.set_index(df_asistencia.columns[0])[sesiones].sum(axis=1)
asistencias_pct = round((asistencias_abs / total_sesiones) * 100, 1)

df_plot = pd.DataFrame({
    "Jugador": jugadores,
    "Entrenamientos": asistencias_abs.values,
    "%": asistencias_pct.values
}).sort_values("Entrenamientos", ascending=True)

# Altura dinámica (25px por jugador)
altura = 25 * len(df_plot)

fig_jugadores = px.bar(
    df_plot,
    x="Entrenamientos", y="Jugador",
    orientation="h",
    title="Entrenamientos por jugador",
    color="%",
    color_continuous_scale="Blues",
    hover_data={"%": True, "Entrenamientos": True, "Jugador": True}
)

fig_jugadores.update_layout(
    height=altura,
    width=800,  # ancho compacto
    margin=dict(l=200, r=50, t=50, b=50),
    xaxis_title="Entrenamientos",
    yaxis_title="",
    yaxis=dict(tickfont=dict(size=10))
)

st.plotly_chart(fig_jugadores, use_container_width=False)



# --- Evolución por sesión ---
st.markdown("<br><h4>📈 Evolución por sesión</h4>", unsafe_allow_html=True)
presentes = df_asistencia[sesiones].sum()
ausentes = total_jugadores - presentes
df_sesiones = pd.DataFrame({
    "Sesión": sesiones,
    "Presentes": presentes.values,
    "Ausentes": ausentes.values
})
fig_sesiones = go.Figure(data=[
    go.Bar(name="Presentes", x=df_sesiones["Sesión"], y=df_sesiones["Presentes"], marker_color="green"),
    go.Bar(name="Ausentes", x=df_sesiones["Sesión"], y=df_sesiones["Ausentes"], marker_color="red")
])
fig_sesiones.update_layout(barmode="stack", title="Asistencia por sesión", height=500)
st.plotly_chart(fig_sesiones, use_container_width=True)

# --- Heatmap asistencia ---
# --- Heatmap asistencia ---
st.markdown("<br><h4>🔥 Heatmap de asistencia</h4>", unsafe_allow_html=True)
heatmap_df = df_asistencia.set_index(df_asistencia.columns[0])[sesiones]

fig_heatmap = px.imshow(
    heatmap_df,
    labels=dict(x="Sesión", y="Jugador", color="Asistencia"),
    x=sesiones,
    y=jugadores,
    color_continuous_scale=["red", "green"],
    aspect="auto"
)

fig_heatmap.update_traces(
    hovertemplate="Jugador: %{y}<br>Sesión: %{x}<br>Asistió: %{z}<extra></extra>"
)

# 👇 Aumentamos altura en función del número de jugadores
fig_heatmap.update_layout(
    height=25 * len(jugadores),   # escala dinámica
    margin=dict(l=200, r=50, t=50, b=50),  # margen izq para nombres largos
    yaxis=dict(tickfont=dict(size=10))
)

st.plotly_chart(fig_heatmap, use_container_width=True)


st.caption("Desarrollado con ❤️ para el control de asistencia del equipo")
