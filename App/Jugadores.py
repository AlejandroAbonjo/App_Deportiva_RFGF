import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Estilos globales ---
st.markdown("""
<style>
    .block-container { padding: 0 !important; }
    .main { padding: 0 !important; }
    header, footer { visibility: hidden; }
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

# --- Funciones auxiliares ---
@st.cache_data
def load_eventos():
    base_dir = os.path.dirname(__file__)
    ruta = os.path.join(base_dir, "Data", "Eventos_partidos.csv")
    return pd.read_csv(ruta)

@st.cache_data
def load_participacion():
    base_dir = os.path.dirname(__file__)
    ruta = os.path.join(base_dir, "Data", "participacion.csv")
    return pd.read_csv(ruta)

@st.cache_data
def load_resultados():
    base_dir = os.path.dirname(__file__)
    ruta = os.path.join(base_dir, "Data", "resultados_partidos.csv")
    return pd.read_csv(ruta)

def kpi_box(label, value):
    st.markdown(f"""
        <div class='kpi-box'>
            <div style='font-size: 0.85rem; color: #555;'>{label}</div>
            <div style='font-size: 1.4rem; font-weight: bold; color: #222;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Carga de datos ---
eventos_df = load_eventos()
participacion_df = load_participacion()
resultados_df = load_resultados()

# --- Sidebar de filtros ---
st.sidebar.title("Filtros")

# 1) Temporada
temporada_sel = st.sidebar.selectbox("📆 Temporada", sorted(resultados_df["temporada"].unique()))

# 2) Competición (filtrada por temporada)
competicion_sel = st.sidebar.selectbox(
    "🏆 Competición",
    sorted(resultados_df[resultados_df["temporada"] == temporada_sel]["competicion"].unique())
)

# 3) Grupo (filtrado por temporada + competición)
grupo_sel = st.sidebar.selectbox(
    "📁 Grupo",
    sorted(resultados_df[
        (resultados_df["temporada"] == temporada_sel) &
        (resultados_df["competicion"] == competicion_sel)
    ]["grupo"].unique())
)

# 4) Equipo (filtrado por temporada + competición + grupo)
equipos_locales = resultados_df[
    (resultados_df["temporada"] == temporada_sel) &
    (resultados_df["competicion"] == competicion_sel) &
    (resultados_df["grupo"] == grupo_sel)
]["equipo_local"].unique()

equipos_visitantes = resultados_df[
    (resultados_df["temporada"] == temporada_sel) &
    (resultados_df["competicion"] == competicion_sel) &
    (resultados_df["grupo"] == grupo_sel)
]["equipo_visitante"].unique()

equipos_filtrados = sorted(set(equipos_locales).union(set(equipos_visitantes)))
equipo_sel = st.sidebar.selectbox("👥 Equipo", equipos_filtrados)

# 5) Jugador (filtrado por temporada + equipo)
jugadores_filtrados = sorted(
    participacion_df[
        (participacion_df["temporada"] == temporada_sel) &
        (participacion_df["equipo"] == equipo_sel)
    ]["jugador"].unique()
)
jugador_sel = st.sidebar.selectbox("🧍 Jugador", jugadores_filtrados)


# --- Colores personalizados ---
colores_personalizados = ['#FFD700', '#000000', '#808000', '#FFEB3B', '#333333']


# =========================
# FILA 1: KPIs de resumen
# =========================
st.markdown(f"## 📋 Resumen de {jugador_sel}")

part_jugador = participacion_df[(participacion_df["equipo"] == equipo_sel) & 
                                (participacion_df["jugador"] == jugador_sel)]

partidos = part_jugador["cod_acta"].nunique()
minutos = part_jugador["minutos_jugados"].sum()
titular = part_jugador[part_jugador["tipo_participacion"].str.contains("titular", case=False, na=False)].shape[0]
suplente = part_jugador[part_jugador["tipo_participacion"].str.contains("suplente", case=False, na=False)].shape[0]

goles = eventos_df[(eventos_df["evento"] == "gol") & (eventos_df["jugador"] == jugador_sel)].shape[0]
amarillas = eventos_df[(eventos_df["evento"] == "tarjeta amarilla") & (eventos_df["jugador"] == jugador_sel)].shape[0]
rojas = eventos_df[(eventos_df["evento"] == "tarjeta roja") & (eventos_df["jugador"] == jugador_sel)].shape[0]

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_box("📅 Partidos", partidos)
with c2: kpi_box("🕒 Minutos", minutos)
with c3: kpi_box("🏁 Titular", titular)
with c4: kpi_box("🔄 Suplente", suplente)

c5, c6, c7 = st.columns(3)
with c5: kpi_box("⚽ Goles", goles)
with c6: kpi_box("🟨 Amarillas", amarillas)
with c7: kpi_box("🟥 Rojas", rojas)


# =========================
# FILA 2: GOLES
# =========================
st.markdown("## ⚽ Goles")

goles_jugador = eventos_df[(eventos_df["evento"] == "gol") & 
                           (eventos_df["jugador"] == jugador_sel)].copy()

# Excluir goles en propia puerta
goles_validos = goles_jugador[goles_jugador["tipo_gol"].str.lower() != "propia puerta"]

if goles_validos.empty:
    st.info("Este jugador no ha marcado goles válidos (sin contar en propia puerta).")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_tipo = px.pie(
            goles_validos, 
            names="tipo_gol", 
            title="Distribución por tipo", 
            color_discrete_sequence=colores_personalizados
        )
        fig_tipo.update_layout(height=350, width=350, margin=dict(t=50, b=50))
        st.plotly_chart(fig_tipo, use_container_width=True)

    with col2:
        goles_validos["parte"] = goles_validos["parte"].fillna("Desconocido")
        fig_parte = px.pie(
            goles_validos, 
            names="parte", 
            title="Goles por parte", 
            color_discrete_sequence=colores_personalizados
        )
        fig_parte.update_layout(height=350, width=350, margin=dict(t=50, b=50))
        st.plotly_chart(fig_parte, use_container_width=True)

    with col3:
        goles_local = goles_validos[(goles_validos["equipo_local"] == equipo_sel)].shape[0]
        goles_visit = goles_validos[(goles_validos["equipo_visitante"] == equipo_sel)].shape[0]
        fig_condicion = px.pie(
            names=["Local", "Visitante"],
            values=[goles_local, goles_visit],
            title="Condición al marcar",
            color_discrete_sequence=colores_personalizados
        )
        fig_condicion.update_layout(height=350, width=350, margin=dict(t=50, b=50))
        st.plotly_chart(fig_condicion, use_container_width=True)

    # Evolución de goles por jornada (barras)
    st.markdown("#### 📊 Evolución de goles por jornada")
    goles_jornada = goles_validos.groupby("jornada").size().reset_index(name="Goles")

    fig_evol = px.bar(
        goles_jornada,
        x="jornada", y="Goles",
        title="Evolución por jornada",
        color_discrete_sequence=["#FFD700"]
    )
    fig_evol.update_traces(width=0.8)
    fig_evol.update_layout(
        height=400,
        xaxis=dict(
            range=[1, 30],      # 🔒 eje fijo de 1 a 30
            dtick=1,            # ticks cada jornada
            tick0=1,            # empieza en 1
            tickmode="linear"   # forzamos que sean enteros consecutivos
        ),
        yaxis_title="Goles"
    )
    st.plotly_chart(fig_evol, use_container_width=True)



# =========================
# FILA 3: SANCIONES
# =========================
st.markdown("## 🟥 Sanciones")

sanciones_jugador = eventos_df[(eventos_df["jugador"] == jugador_sel) & 
                               (eventos_df["evento"].isin(["tarjeta amarilla","tarjeta roja"]))]
if sanciones_jugador.empty:
    st.info("Este jugador no tiene sanciones registradas.")
else:
    df_evol = sanciones_jugador.groupby(["jornada","evento"]).size().reset_index(name="Tarjetas")
    fig_evol = px.bar(df_evol, x="jornada", y="Tarjetas", color="evento",
                      barmode="group",
                      color_discrete_map={"tarjeta amarilla":"#FFD700","tarjeta roja":"#FF0000"})
    fig_evol.update_traces(width=0.8)
    fig_evol.update_layout(height=400, xaxis=dict(range=[1,30], dtick=1), yaxis_title="Tarjetas")
    st.plotly_chart(fig_evol, use_container_width=True)


# =========================
# FILA 4: PARTICIPACIÓN
# =========================
st.markdown("## 🧍‍♂️ Participación")

if part_jugador.empty:
    st.info("No hay datos de participación para este jugador.")
else:
    col1, col2 = st.columns(2)

    with col1:
        fig_min = px.bar(part_jugador, x="jornada", y="minutos_jugados", 
                         title="Minutos jugados por jornada", color_discrete_sequence=["#000000"])
        fig_min.update_layout(height=400, xaxis=dict(range=[1,30], dtick=1), margin=dict(t=50, b=50))
        st.plotly_chart(fig_min, use_container_width=True)

    with col2:
        fig_tipo = px.histogram(part_jugador, x="tipo_participacion", 
                                color_discrete_sequence=["#FFD700"])
        fig_tipo.update_layout(title="Distribución de participaciones",
                               height=400, margin=dict(t=50, b=50))
        st.plotly_chart(fig_tipo, use_container_width=True)
