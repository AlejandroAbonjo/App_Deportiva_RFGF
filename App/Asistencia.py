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
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBy2T1etnowIRf1l5zP3kXBfs54uKkDlm5pvKdsoyFByi3fYLaNEOLGc1kTJPj6g/pub?gid=1878989803&single=true&output=csv"
    return pd.read_csv(url)


df = load_data()

# --- Configuración inicial ---
st.set_page_config(page_title="Control de Asistencia", layout="wide")

# --- Título principal y botón refrescar ---
col_titulo, col_boton = st.columns([8,1])
with col_titulo:
    st.title("📊 Control de Asistencia a Entrenamientos")
with col_boton:
    if st.button("🔄 Refrescar"):
        st.cache_data.clear()



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
    margin=dict(l=200, r=50, t=50, b=50),
    xaxis_title="Entrenamientos",
    yaxis_title="",
    yaxis=dict(tickfont=dict(size=10))
)

st.plotly_chart(fig_jugadores, use_container_width=True)




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


# --- Evolución individual de asistencia (todos los jugadores) ---
st.markdown("<br><h4>📈 Evolución acumulada por jugador</h4>", unsafe_allow_html=True)

# Crear DataFrame acumulado por jugador
df_evolucion = df_asistencia.set_index(df_asistencia.columns[0])[sesiones]

# Calcular acumulado y % por sesión
evolucion_pct = df_evolucion.cumsum(axis=1).div(range(1, len(sesiones)+1), axis=1) * 100

# Pasar a formato largo para graficar
df_long = evolucion_pct.reset_index().melt(
    id_vars=df_asistencia.columns[0],
    var_name="Sesión",
    value_name="% Acumulado"
)
df_long.rename(columns={df_asistencia.columns[0]: "Jugador"}, inplace=True)

# Gráfico de líneas
fig_evol = px.line(
    df_long,
    x="Sesión", y="% Acumulado",
    color="Jugador",
    markers=True,
    title="Evolución acumulada de asistencia por jugador"
)

fig_evol.update_layout(
    yaxis=dict(range=[0, 100]),
    height=700,
    margin=dict(l=50, r=30, t=50, b=50)
)

st.plotly_chart(fig_evol, use_container_width=True)



col1, col2 = st.columns([3, 1])  # ancho relativo: col1 más grande que col2

with col1:
    st.caption("Desarrollado  para el control de asistencia del equipo")

with col2:
    st.markdown(
        """
        <div style='text-align:right; font-size:0.85rem; color:#555;'>
            📂 <a href="https://docs.google.com/spreadsheets/d/1cUcmpeq6Dw32KDCiqmBuw6YlPkBFKt3t/edit?gid=1878989803#gid=1878989803" target="_blank">
            Abrir hoja en Google Sheets
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
