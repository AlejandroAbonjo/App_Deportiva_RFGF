import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- Estilos globales ---
st.markdown("""
<style>
    .block-container {
        padding: 0 !important;
    }
    .main {
        padding: 0 !important;
    }
    header, footer {
        visibility: hidden;
    }
    .kpi-box {
        background-color: #f9f9f9;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 8px;
        border-left: 5px solid #000000; /* azul suave o el color corporativo que prefieras */
    }
</style>
""", unsafe_allow_html=True)

# --- Funciones auxiliares ---
@st.cache_data
def load_eventos():
    return pd.read_csv("C:/Users/alejandro.abonjo/Documents/RFGF/Procesamiento/Eventos_partidos.csv")

@st.cache_data
def load_participacion():
    return pd.read_csv("C:/Users/alejandro.abonjo/Documents/RFGF/Procesamiento/participacion.csv")

@st.cache_data
def load_puntos():
    return pd.read_csv("C:/Users/alejandro.abonjo/Documents/RFGF/Procesamiento/puntos.csv")

@st.cache_data
def load_resultados():
    return pd.read_csv("C:/Users/alejandro.abonjo/Documents/RFGF/Procesamiento/resultados_partidos.csv")

# --- Carga de datos ---
eventos_df = load_eventos()
participacion_df = load_participacion()
puntos_df = load_puntos()
resultados_df = load_resultados()

# --- Sidebar de filtros ---
st.sidebar.title("Filtros")
competicion_sel = st.sidebar.selectbox("🏆 Competición", sorted(resultados_df["competicion"].unique()))
grupo_sel = st.sidebar.selectbox("📁 Grupo", sorted(resultados_df[resultados_df["competicion"] == competicion_sel]["grupo"].unique()))
equipos_locales = resultados_df[(resultados_df["competicion"] == competicion_sel) & (resultados_df["grupo"] == grupo_sel)]["equipo_local"].unique()
equipos_visitantes = resultados_df[(resultados_df["competicion"] == competicion_sel) & (resultados_df["grupo"] == grupo_sel)]["equipo_visitante"].unique()
equipos_filtrados = sorted(set(equipos_locales).union(set(equipos_visitantes)))
equipo_sel = st.sidebar.selectbox("👥 Equipo", equipos_filtrados)

# --- Fila 1: escudo arriba a la derecha ---
fila1_col1, fila1_col2 = st.columns([10, 1.75])
with fila1_col1:
    pestanas = st.radio("Navegación", ["Resumen", "Análisis Goles", "Análisis Sanciones", "Análisis Sustituciones","Análisis Participación"], horizontal=True, label_visibility="collapsed")
with fila1_col2:
    st.image("escudo.png", width=50)

# --- Fila 2: texto centrado debajo ---
fila2_col1, fila2_col2 = st.columns([10, 3.5])
with fila2_col2:
    st.markdown("""
        <div style='text-align:center; font-size: 0.85rem; color: #555; margin-top: -0.5rem;'>
        Plataforma de datos del club</div>
    """, unsafe_allow_html=True)

# --- Función para mostrar una caja de KPI ---
def kpi_box(label, value):
    st.markdown(f"""
        <div class='kpi-box'>
            <div style='font-size: 0.85rem; color: #555;'>{label}</div>
            <div style='font-size: 1.4rem; font-weight: bold; color: #222;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)



# --- Función para convertir número a ordinal ---
def ordinal(n):
    return f"{n}º" if isinstance(n, int) else n

# --- Colores personalizados para gráficas ---
colores_personalizados = ['#FFD700', '#000000', '#808000', '#FFEB3B', '#333333']


# --- Aquí seguiría el código para otras pestañas como Resumen, Sanciones y Sustituciones ---


# --- Página RESUMEN ---
if pestanas == "Resumen":
    st.markdown("### 📋 Resumen del equipo")

    # --- Datos base del equipo ---
    partidos_equipo = resultados_df[(resultados_df["equipo_local"] == equipo_sel) | (resultados_df["equipo_visitante"] == equipo_sel)].copy()
    es_local = partidos_equipo["equipo_local"] == equipo_sel
    partidos_equipo["GF"] = partidos_equipo["goles_local"].where(es_local, partidos_equipo["goles_visitante"])
    partidos_equipo["GC"] = partidos_equipo["goles_visitante"].where(es_local, partidos_equipo["goles_local"])
    partidos_equipo["Resultado"] = partidos_equipo.apply(lambda row: "G" if row["GF"] > row["GC"] else ("E" if row["GF"] == row["GC"] else "P"), axis=1)
    PJ = len(partidos_equipo)
    PG = (partidos_equipo["Resultado"] == "G").sum()
    PE = (partidos_equipo["Resultado"] == "E").sum()
    PP = (partidos_equipo["Resultado"] == "P").sum()
    GF = partidos_equipo["GF"].sum()
    GC = partidos_equipo["GC"].sum()
    DG = GF - GC

    puntos_equipo = puntos_df[puntos_df["equipo"] == equipo_sel]["puntos"].sum()
    tabla = puntos_df.groupby("equipo")["puntos"].sum().reset_index()
    tabla["pos"] = tabla["puntos"].rank(method="min", ascending=False).astype(int)
    pos_num = tabla[tabla["equipo"] == equipo_sel]["pos"].values[0] if equipo_sel in tabla["equipo"].values else "-"
    posicion = ordinal(pos_num)

    # --- KPIs generales ---
    # --- Evolución posición (en construcción) ---
    st.markdown("##### 📉 Evolución de la posición")
    st.info("Estamos trabajando en esta funcionalidad. Pronto podrás ver cómo ha evolucionado el equipo jornada a jornada.")

    # --- Rendimiento general
    st.markdown("#### 🎯 Rendimiento General")
    col1, col2 = st.columns(2)
    with col1:
        kpi_box("📈 Posición", posicion)
    with col2:
        kpi_box("🎯 Puntos", puntos_equipo)

    col3, col4 = st.columns(2)
    with col3:
        kpi_box("📅 PJ", PJ)
    with col4:
        kpi_box("📊 PG / PE / PP", f"{PG} / {PE} / {PP}")

    col5, col6, col7 = st.columns(3)
    with col5:
        kpi_box("🥅 GF", GF)
    with col6:
        kpi_box("🛡️ GC", GC)
    with col7:
        kpi_box("⚖️ DG", DG)

    # --- Disciplina ---
    cod_actas_equipo = set(participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"].unique())
    amarillas = eventos_df[(eventos_df["evento"] == "tarjeta amarilla") & (eventos_df["equipo"] == equipo_sel)].shape[0]
    rojas = eventos_df[(eventos_df["evento"] == "tarjeta roja") & (eventos_df["equipo"] == equipo_sel)].shape[0]
    provocadas_amarillas = eventos_df[(eventos_df["evento"] == "tarjeta amarilla") & (eventos_df["cod_acta"].isin(cod_actas_equipo)) & (eventos_df["equipo"] != equipo_sel)].shape[0]
    provocadas_rojas = eventos_df[(eventos_df["evento"] == "tarjeta roja") & (eventos_df["cod_acta"].isin(cod_actas_equipo)) & (eventos_df["equipo"] != equipo_sel)].shape[0]

    st.markdown("#### 🟥 Disciplina")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_box("🟨 Amarillas", amarillas)
    with c2:
        kpi_box("🟥 Rojas", rojas)
    with c3:
        kpi_box("🧲 Amarillas Provocadas", provocadas_amarillas)
    with c4:
        kpi_box("🧲 Rojas Provocadas", provocadas_rojas)

    # --- Racha y rendimiento ---
    st.markdown("#### 🔥 Racha y rendimiento")
    ultimos = partidos_equipo.sort_values(by="jornada", ascending=False).head(5)["Resultado"]
    simbolos = {"G": "🟢", "E": "🟡", "P": "🔴"}
    racha = ''.join([simbolos.get(r, "❔") for r in ultimos])
    pct_victorias = round((PG / PJ) * 100, 1) if PJ else 0
    porterias_cero = (partidos_equipo["GC"] == 0).sum()
    pct_port_cero = round((porterias_cero / PJ) * 100, 1) if PJ else 0
    media_GF = round(GF / PJ, 2) if PJ else 0
    media_GC = round(GC / PJ, 2) if PJ else 0

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f"""
        <div class='kpi-box'>
            <div style='font-size: 0.85rem; color: #888;'>🧩 Últimos 5</div>
            <div style='font-size: 1.1rem; font-weight: bold; letter-spacing: 3px;'>{racha}</div>
        </div>
    """, unsafe_allow_html=True)
    with c6:
        kpi_box("✅ % Victorias", f"{pct_victorias}%")
    with c7:
        kpi_box("🧤 % Port. Cero", f"{pct_port_cero}%")
    with c8:
        kpi_box("📊 GF/GC por PJ", f"{media_GF} / {media_GC}")

    # --- Balance local/visitante ---
    st.markdown("#### 🏠 Balance local/visitante")
    local = resultados_df[resultados_df["equipo_local"] == equipo_sel].copy()
    visitante = resultados_df[resultados_df["equipo_visitante"] == equipo_sel].copy()
    vict_local = (local["goles_local"] > local["goles_visitante"]).sum()
    der_visit = (visitante["goles_local"] > visitante["goles_visitante"]).sum()
    pj_local = len(local)
    pj_visitante = len(visitante)
    pct_vict_local = round((vict_local / pj_local) * 100, 1) if pj_local else 0
    pct_derrot_visit = round((der_visit / pj_visitante) * 100, 1) if pj_visitante else 0
    pts_local = puntos_df[(puntos_df["equipo"] == equipo_sel) & (puntos_df["local_visitante"] == "local")]["puntos"].sum()
    pts_visit = puntos_df[(puntos_df["equipo"] == equipo_sel) & (puntos_df["local_visitante"] == "visitante")]["puntos"].sum()
    gc_local = local["goles_visitante"].sum()
    gc_visit = visitante["goles_local"].sum()

    c9, c10, c11, c12 = st.columns(4)
    with c9:
        kpi_box("📊 % Vic Loc/Vis", f"{pct_vict_local}% / {round((visitante['goles_visitante'] > visitante['goles_local']).sum() / pj_visitante * 100, 1) if pj_visitante else 0}%")
    with c10:
        kpi_box("🎯 Pts Loc/Vis", f"{pts_local} / {pts_visit}")
        
    with c11:
        kpi_box("⚽ GF Loc/Vis", f"{local['goles_local'].sum()} / {visitante['goles_visitante'].sum()}")
    with c12:
        kpi_box("🛡️ GC Loc/Vis", f"{gc_local} / {gc_visit}")


# --- Página ANÁLISIS GOLES ---
elif pestanas == "Análisis Goles":
    st.markdown("### ⚽ Goles Marcados")

    goles_equipo = eventos_df[(eventos_df["evento"] == "gol") & (eventos_df["equipo"] == equipo_sel)].copy()

    tipo_map = {
        "penalti": "Penalti",
        "penalty": "Penalti",
        "propia puerta": "Propia puerta",
        "autogol": "Propia puerta",
        "normal": "Normal"
    }

    if "tipo_gol" in goles_equipo.columns:
        goles_equipo["tipo"] = goles_equipo["tipo_gol"].map(tipo_map).fillna("Normal")
    else:
        goles_equipo["tipo"] = "Normal"

    col_g1, col_g2, col_g3 = st.columns([1, 1, 1])

    with col_g1:
        fig_tipo = px.pie(goles_equipo, names="tipo", title="Distribución por tipo de gol", color_discrete_sequence=colores_personalizados)
        fig_tipo.update_layout(height=300, width=300)
        st.plotly_chart(fig_tipo, use_container_width=True, key='pie_tipo')

    with col_g2:
        fig_parte = px.pie(goles_equipo, names="parte", title="Goles por parte (1ª o 2ª mitad)", color_discrete_sequence=colores_personalizados)
        fig_parte.update_layout(height=300, width=300)
        st.plotly_chart(fig_parte, use_container_width=True, key='pie_parte')

    with col_g3:
        goles_local = eventos_df[(eventos_df["evento"] == "gol") & (eventos_df["equipo"] == equipo_sel) & (eventos_df["equipo_local"] == equipo_sel)].shape[0]
        goles_visit = eventos_df[(eventos_df["evento"] == "gol") & (eventos_df["equipo"] == equipo_sel) & (eventos_df["equipo_visitante"] == equipo_sel)].shape[0]
        fig_condicion = px.pie(
            names=["Local", "Visitante"],
            values=[goles_local, goles_visit],
            title="Goles como local vs visitante",
            color_discrete_sequence=colores_personalizados
        )
        fig_condicion.update_layout(height=300, width=300)
        st.plotly_chart(fig_condicion, use_container_width=True, key='pie_condicion')


    # --- Fila extra: Goles RECIBIDOS ---
    st.markdown("### 🛡️ Goles recibidos")

    # Filtrar goles en contra por cod_actas del equipo
    cod_actas_equipo = set(participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"])
    goles_contra_df = eventos_df[
        (eventos_df["evento"] == "gol") &
        (eventos_df["equipo"] != equipo_sel) &
        (eventos_df["cod_acta"].isin(cod_actas_equipo))
    ].copy()

    # Tipo de gol
    if "tipo_gol" in goles_contra_df.columns:
        goles_contra_df["tipo"] = goles_contra_df["tipo_gol"].map(tipo_map).fillna("Normal")
    else:
        goles_contra_df["tipo"] = "Normal"

    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])

    with col_r1:
        fig_tipo_recibido = px.pie(
            goles_contra_df,
            names="tipo",
            title="Tipo de gol recibido",
            color_discrete_sequence=colores_personalizados
        )
        fig_tipo_recibido.update_layout(height=300, width=300)
        st.plotly_chart(fig_tipo_recibido, use_container_width=False)

    with col_r2:
        fig_parte_recibida = px.pie(
            goles_contra_df,
            names="parte",
            title="Parte en que se recibió",
            color_discrete_sequence=colores_personalizados
        )
        fig_parte_recibida.update_layout(height=300, width=300)
        st.plotly_chart(fig_parte_recibida, use_container_width=False)

    with col_r3:
        goles_contra_df["condicion"] = goles_contra_df.apply(
            lambda row: "Local" if row["equipo_visitante"] == equipo_sel else "Visitante", axis=1
        )
        fig_condicion_recibida = px.pie(
            goles_contra_df,
            names="condicion",
            title="Condición al recibir el gol",
            color_discrete_sequence=colores_personalizados
        )
        fig_condicion_recibida.update_layout(height=300, width=300)
        st.plotly_chart(fig_condicion_recibida, use_container_width=False)

    col_g4, col_g5 = st.columns([1, 1])

    def clasificar_minuto(minuto):
        try:
            m = int(str(minuto).replace("'", "").split('+')[0])
            if m <= 15:
                return "0-15"
            elif m <= 30:
                return "16-30"
            elif m <= 45:
                return "31-45"
            elif m <= 60:
                return "46-60"
            elif m <= 75:
                return "61-75"
            else:
                return "76-90+"
        except:
            return "Desconocido"

    # --- Goles a favor y en contra por tramo ---
    eventos_df["tramo"] = eventos_df["minuto"].apply(clasificar_minuto)

    goles_favor = eventos_df[(eventos_df["evento"] == "gol") & (eventos_df["equipo"] == equipo_sel)]
    favor_tramos = goles_favor.groupby("tramo").size().reset_index(name="Goles a favor")

    cod_actas_equipo = set(participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"])
    goles_contra = eventos_df[(eventos_df["evento"] == "gol") & 
                            (eventos_df["equipo"] != equipo_sel) & 
                            (eventos_df["cod_acta"].isin(cod_actas_equipo))]
    contra_tramos = goles_contra.groupby("tramo").size().reset_index(name="Goles en contra")

    tramos_merged = pd.merge(favor_tramos, contra_tramos, on="tramo", how="outer").fillna(0)
    tramos_merged = tramos_merged.sort_values("tramo")

    fig_tramos = px.bar(
        tramos_merged.melt(id_vars="tramo", value_vars=["Goles a favor", "Goles en contra"], 
                        var_name="Tipo", value_name="Cantidad"),
        x="tramo", y="Cantidad", color="Tipo", barmode="group",
        title="Goles a favor y en contra por tramo de minutos",
        color_discrete_map={
            "Goles a favor": "#FFD700",   # Amarillo
            "Goles en contra": "#000000"  # Negro
        }
    )
    fig_tramos.update_layout(height=350, width=400, margin=dict(t=40, b=40))
    with col_g4:
        st.plotly_chart(fig_tramos, use_container_width=False)

    # --- Máximos goleadores ---
    # Excluir goles en propia puerta
    goleadores_validos = goles_equipo[goles_equipo["tipo"] != "Propia puerta"]
    goleadores_df = goleadores_validos["jugador"].value_counts().reset_index()
    goleadores_df.columns = ["Jugador", "Goles"]
    goleadores_df = goleadores_df.sort_values("Goles", ascending=True)

    fig_goleadores = px.bar(
        goleadores_df,
        x="Goles", y="Jugador", orientation="h", title="Máximos goleadores del equipo",
        color_discrete_sequence=colores_personalizados
    )
    fig_goleadores.update_layout(height=350, width=400, margin=dict(t=40, b=40))

    with col_g5:
        st.plotly_chart(fig_goleadores, use_container_width=False)





elif pestanas == "Análisis Sanciones":
    st.markdown("### 🟥 Análisis de Sanciones")

    # --- Filtrar eventos de sanciones del equipo seleccionado ---
    sanciones_df = eventos_df[eventos_df["evento"].isin(["tarjeta amarilla", "tarjeta roja"])].copy()
    sanciones_equipo = sanciones_df[sanciones_df["equipo"] == equipo_sel]
    cod_actas_equipo = set(participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"].unique())
    provocadas_df = sanciones_df[(sanciones_df["cod_acta"].isin(cod_actas_equipo)) & (sanciones_df["equipo"] != equipo_sel)]

    # --- 1. Resumen general ---
    total_amarillas = (sanciones_equipo["evento"] == "tarjeta amarilla").sum()
    total_rojas = (sanciones_equipo["evento"] == "tarjeta roja").sum()
    provocadas_amarillas = (provocadas_df["evento"] == "tarjeta amarilla").sum()
    provocadas_rojas = (provocadas_df["evento"] == "tarjeta roja").sum()
    partidos_jugados = participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"].nunique()
    amarillas_por_partido = round(total_amarillas / partidos_jugados, 2) if partidos_jugados else 0
    rojas_por_partido = round(total_rojas / partidos_jugados, 2) if partidos_jugados else 0

    st.markdown("#### 📊 Resumen general de sanciones")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_box("🟨 TA", total_amarillas)
    with c2:
        kpi_box("🟥 TR", total_rojas)
    with c3:
        kpi_box("🟨 TA Provocadas", provocadas_amarillas)
    with c4:
        kpi_box("🟥 TR Provocadas", provocadas_rojas)

    c5, c6 = st.columns(2)
    with c5:
        kpi_box("🟨 TA / PJ", amarillas_por_partido)
    with c6:
        kpi_box("🟥 TR / PJ", rojas_por_partido)

    # --- 2. Jugadores más sancionados ---
    st.markdown("#### 🧍‍♂️ Jugadores más sancionados")
    jugadores_sanciones = sanciones_equipo.groupby(["jugador", "evento"]).size().unstack(fill_value=0)
    jugadores_sanciones = jugadores_sanciones.sort_values(by="tarjeta amarilla", ascending=True)
    fig_jugadores = px.bar(
        jugadores_sanciones,
        orientation="h",
        barmode="stack",
        title="Tarjetas por jugador",
        color_discrete_map={"tarjeta amarilla": "#FFD700", "tarjeta roja": "#FF0000"},
    )
    fig_jugadores.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig_jugadores, use_container_width=True)


    # --- 3 y 4 combinados: Distribución de tarjetas ---
    st.markdown("#### 🧭 Distribución de tarjetas")

    col_dist1, col_dist2 = st.columns(2)

    # --- Por parte del partido ---
    with col_dist1:
        st.markdown("##### 🕒 Por parte del partido")
        parte_data = sanciones_equipo.groupby(["parte", "evento"]).size().unstack(fill_value=0).reset_index()
        parte_data["total"] = parte_data["tarjeta amarilla"] + parte_data["tarjeta roja"]

        fig_parte = px.pie(
            parte_data,
            names="parte",
            values="total",
            color_discrete_sequence=colores_personalizados,
            custom_data=["tarjeta amarilla", "tarjeta roja"]
        )
        fig_parte.update_traces(
            hovertemplate="Parte: %{label}<br>🟨 Amarillas: %{customdata[0]}<br>🟥 Rojas: %{customdata[1]}<extra></extra>"
        )
        fig_parte.update_layout(height=300, width=300)
        st.plotly_chart(fig_parte, use_container_width=False)

    # --- Por condición del equipo ---
    with col_dist2:
        st.markdown("##### 🏟️ Por condición del equipo")
        sanciones_equipo["condicion"] = sanciones_equipo.apply(
            lambda row: "Local" if row["equipo_local"] == equipo_sel else "Visitante", axis=1
        )
        condicion_data = sanciones_equipo.groupby(["condicion", "evento"]).size().unstack(fill_value=0).reset_index()
        condicion_data["total"] = condicion_data["tarjeta amarilla"] + condicion_data["tarjeta roja"]

        fig_condicion = px.pie(
            condicion_data,
            names="condicion",
            values="total",
            color_discrete_sequence=colores_personalizados,
            custom_data=["tarjeta amarilla", "tarjeta roja"]
        )
        fig_condicion.update_traces(
            hovertemplate="Condición: %{label}<br>🟨 Amarillas: %{customdata[0]}<br>🟥 Rojas: %{customdata[1]}<extra></extra>"
        )
        fig_condicion.update_layout(height=300, width=300)
        st.plotly_chart(fig_condicion, use_container_width=False)



    # --- 5. Evolución por jornada ---
    st.markdown("#### 📈 Evolución de tarjetas por jornada")
    if "jornada" in resultados_df.columns:
        sanciones_equipo["jornada"] = sanciones_equipo["jornada"].astype(int)
        sanciones_por_jornada = sanciones_equipo.groupby(["jornada", "evento"]).size().unstack(fill_value=0).reset_index()
        fig_evol = px.bar(
            sanciones_por_jornada,
            x="jornada",
            y=["tarjeta amarilla", "tarjeta roja"],
            barmode="group",
            title="Tarjetas por jornada",
            color_discrete_map={"tarjeta amarilla": "#FFD700", "tarjeta roja": "#FF0000"}
        )
        fig_evol.update_layout(height=500)
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("No hay información de jornadas disponible para mostrar evolución.")

    # --- Comparativa por equipo ---
    st.markdown("#### 🏆 Comparativa con el resto de equipos")

    # Filtramos solo equipos que estén en la competición y grupo seleccionados
    equipos_en_grupo = resultados_df[
        (resultados_df["competicion"] == competicion_sel) &
        (resultados_df["grupo"] == grupo_sel)
    ][["equipo_local", "equipo_visitante"]].melt(value_name="equipo")["equipo"].unique()

    sanciones_liga = eventos_df[
        (eventos_df["evento"].isin(["tarjeta amarilla", "tarjeta roja"])) &
        (eventos_df["equipo"].isin(equipos_en_grupo))
    ]

    # Agrupar por equipo
    equipos_sanciones = sanciones_liga.groupby(["equipo", "evento"]).size().unstack(fill_value=0)
    equipos_sanciones = equipos_sanciones.sort_values(by="tarjeta amarilla", ascending=True)

    # Crear gráfico
    fig_equipos = px.bar(
        equipos_sanciones,
        orientation="h",
        barmode="stack",
        title="Tarjetas por equipo en la liga",
        color_discrete_map={
            "tarjeta amarilla": "#FFD700",  # Amarilla
            "tarjeta roja": "#FF0000"       # Roja
        }
    )
    fig_equipos.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_equipos, use_container_width=True)



elif pestanas == "Análisis Sustituciones":
    st.markdown("### 🔁 Análisis de Sustituciones")

    # --- Filtrado dinámico según selección ---
    sust_df = eventos_df[eventos_df["evento"].str.lower() == "sustitucion"].copy()
    sust_df["minuto"] = pd.to_numeric(sust_df["minuto"], errors="coerce")  # asegurar numérico

    # Filtramos por competición y grupo
    codigos_filtrados = set(participacion_df[participacion_df["equipo"] == equipo_sel]["cod_acta"].unique())

    sust_df_equipo = sust_df[sust_df["cod_acta"].isin(codigos_filtrados)]

    # Filtramos por equipo seleccionado
    sust_equipo = sust_df_equipo[sust_df["equipo"] == equipo_sel].copy()

    total_sustituciones = len(sust_equipo)
    sust_por_partido = round(total_sustituciones / sust_equipo["cod_acta"].nunique(), 2) if total_sustituciones else 0
    minuto_medio = round(sust_equipo["minuto"].mean(skipna=True), 1) if total_sustituciones else 0

    primeros_minutos = sust_equipo.groupby("cod_acta")["minuto"].min()
    ultimos_minutos = sust_equipo.groupby("cod_acta")["minuto"].max()
    media_primera = round(primeros_minutos.mean(), 1) if not primeros_minutos.empty else 0
    media_ultima = round(ultimos_minutos.mean(), 1) if not ultimos_minutos.empty else 0

    # --- KPIs generales ---
    st.markdown("#### 📊 Resumen de sustituciones")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_box("🔁 Sust/Partido", sust_por_partido)
    with c2:
        kpi_box("⏱️ Minuto medio", minuto_medio)
    with c3:
        kpi_box("⏱️ Min. primera", media_primera)
    with c4:
        kpi_box("⏱️ Min. última", media_ultima)


    # --- 3. Jugadores más sustituidos y más que entran ---
    st.markdown("#### 👥 Jugadores más implicados")

    col1, col2 = st.columns(2)

    with col1:
        top_sale = sust_equipo["jugador_sale"].value_counts().nlargest(10).reset_index()
        top_sale.columns = ["Jugador", "Veces"]
        fig_sale = px.bar(top_sale, x="Veces", y="Jugador", orientation="h", title="Jugadores que más salen", color_discrete_sequence=colores_personalizados)
        fig_sale.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_sale, use_container_width=True)

    with col2:
        top_entra = sust_equipo["jugador_entra"].value_counts().nlargest(10).reset_index()
        top_entra.columns = ["Jugador", "Veces"]
        fig_entra = px.bar(top_entra, x="Veces", y="Jugador", orientation="h", title="Jugadores que más entran", color_discrete_sequence=colores_personalizados)
        fig_entra.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_entra, use_container_width=True)

    # --- 4. Evolución por jornada ---
    st.markdown("#### 📈 Sustituciones por jornada")
    sust_equipo["jornada"] = sust_equipo["jornada"].astype(int)
    subs_jornada = sust_equipo.groupby("jornada").size().reset_index(name="Sustituciones")
    fig_jornada = px.line(subs_jornada, x="jornada", y="Sustituciones", markers=True, line_shape="spline")
    fig_jornada.update_layout(height=300, xaxis_title="Jornada", yaxis_title="Sustituciones",yaxis_range=[0, 5])
    st.plotly_chart(fig_jornada, use_container_width=True)

    # --- 5. Comparativa con otros equipos ---
    st.markdown("#### 🏆 Comparativa con el grupo")

    equipos_grupo = resultados_df[
        (resultados_df["competicion"] == competicion_sel) &
        (resultados_df["grupo"] == grupo_sel)
    ][["equipo_local", "equipo_visitante"]].melt(value_name="equipo")["equipo"].unique()

    sust_grupo = sust_df[sust_df["equipo"].isin(equipos_grupo)].copy()
    top_equipos = sust_grupo["equipo"].value_counts().sort_values(ascending=True).reset_index()
    top_equipos.columns = ["Equipo", "Sustituciones"]

    fig_eq = px.bar(top_equipos, x="Sustituciones", y="Equipo", orientation="h", color_discrete_sequence=colores_personalizados)
    fig_eq.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_eq, use_container_width=True)

    # --- 6. Combinaciones más repetidas ---
    st.markdown("#### 🔁 Combinaciones más repetidas")

    combinaciones = sust_equipo.groupby(["jugador_sale", "jugador_entra"]).size().reset_index(name="Veces")
    combinaciones = combinaciones.sort_values("Veces", ascending=False).head(10)

    st.dataframe(combinaciones, use_container_width=True)

elif pestanas == "Análisis Participación":
    st.markdown("### 🧍‍♂️ Análisis de Participación")

    # --- Filtrado de participación del equipo ---
    participacion_equipo = participacion_df[participacion_df["equipo"] == equipo_sel].copy()

    # --- KPIs resumen ---
    st.markdown("#### 📊 Resumen general")
    total_jugadores = participacion_equipo["jugador"].nunique()
    partidos_disputados = participacion_equipo["cod_acta"].nunique()
    media_jugadores_por_partido = round(len(participacion_equipo) / partidos_disputados, 2) if partidos_disputados else 0

    minutos_por_jugador = participacion_equipo.groupby("jugador")["minutos_jugados"].sum()
    jugador_top_minutos = minutos_por_jugador.idxmax()
    max_minutos = minutos_por_jugador.max()

    titularidades = participacion_equipo[participacion_equipo["tipo_participacion"].str.contains("titular", case=False, na=False)]
    jugador_top_titular = titularidades["jugador"].value_counts().idxmax()
    max_titularidades = titularidades["jugador"].value_counts().max()

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_box("👥 Jugadores utilizados", total_jugadores)
    with c2:
        kpi_box(f"🕒 Más minutos ({jugador_top_minutos})", max_minutos)
    with c3:
        kpi_box(f"🏁 Más titularidades ({jugador_top_titular})", max_titularidades)

    # --- Minutos por jugador ---
    st.markdown("#### 🕒 Jugadores con más minutos")
    top_minutos = minutos_por_jugador.sort_values(ascending=True).reset_index().rename(columns={"minutos_jugados": "Minutos"})
    fig_min = px.bar(top_minutos, x="Minutos", y="jugador", orientation="h", color_discrete_sequence=colores_personalizados)
    fig_min.update_layout(height=550)
    st.plotly_chart(fig_min, use_container_width=True)

    # --- Titularidades vs suplencias ---
    st.markdown("#### 🏁 Titularidades y suplencias")
    conteo_titular = titularidades["jugador"].value_counts().reset_index()
    conteo_titular.columns = ["Jugador", "Titular"]
    fig_titular = px.bar(conteo_titular.sort_values("Titular"), x="Titular", y="Jugador", orientation="h", title="Titularidades por jugador", color_discrete_sequence=["#000000"])
    fig_titular.update_layout(height=550)
    st.plotly_chart(fig_titular, use_container_width=True)

    # --- Participaciones totales ---
    st.markdown("#### 👣 Participaciones totales")
    presencias = participacion_equipo.groupby("jugador")["cod_acta"].nunique().reset_index(name="Partidos")
    fig_presencias = px.bar(presencias.sort_values("Partidos", ascending=True), x="Partidos", y="jugador", orientation="h", color_discrete_sequence=colores_personalizados)
    fig_presencias.update_layout(height=550)
    st.plotly_chart(fig_presencias, use_container_width=True)

    # Heatmap de participacion

    mapa_participacion = {
        "no convocado": 0,
        "suplente no participa": 1,
        "suplente participa": 2,
        "titular sustituido": 3,
        "titular todo partido": 4
    }

    # Crear combinaciones jugador-jornada
    jugadores = participacion_equipo["jugador"].unique()
    jornadas = participacion_equipo["jornada"].unique()
    full_index = pd.MultiIndex.from_product([jugadores, jornadas], names=["jugador", "jornada"])
    df_full = pd.DataFrame(index=full_index).reset_index()

    # Unir con datos reales
    participacion_real = participacion_equipo[["jugador", "jornada", "tipo_participacion"]]
    df_merge = df_full.merge(participacion_real, on=["jugador", "jornada"], how="left")

    # Rellenar valores ausentes con "no convocado"
    df_merge["tipo_participacion"] = df_merge["tipo_participacion"].fillna("no convocado")

    # Mapear a valores numéricos
    df_merge["participacion_valor"] = df_merge["tipo_participacion"].map(mapa_participacion)

    # Pivot para heatmap
    heatmap_df = df_merge.pivot(index="jugador", columns="jornada", values="participacion_valor")

    # Crear heatmap Plotly
    import plotly.graph_objects as go

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        zmin=0,
        zmax=4,
        colorscale=[
            [0.0, "gray"],      # No convocado
            [0.25, "black"],    # Suplente no participa
            [0.5, "#555500"],   # Suplente participa
            [0.75, "#dddd00"],  # Titular sustituido
            [1.0, "yellow"]     # Titular todo partido
        ],
        colorbar=dict(
            title="",
            tickvals=[0, 1, 2, 3, 4],
            ticktext=[
                "0 - No convocado",
                "1 - Suplente no participa",
                "2 - Suplente participa",
                "3 - Titular sustituido",
                "4 - Titular todo partido"
            ],
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.25
        )
    ))

    fig.update_layout(
        title="Tipo de participación por jugador y jornada",
        height=700,
        margin=dict(t=50, b=120)
    )

    st.plotly_chart(fig, use_container_width=True)
