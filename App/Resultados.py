import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt



# --- Estilos globales: sin márgenes, encabezado fijo y sidebar desplazada ---
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
</style>
""", unsafe_allow_html=True)




# --- Funciones auxiliares ---
@st.cache_data
def load_eventos():
    base_dir = os.path.dirname(__file__)
    ruta = os.path.join(base_dir, "Data", "Eventos_partidos.csv")
    return pd.read_csv(ruta)

@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    ruta = os.path.join(base_dir, "Data", "resultados_partidos.csv")
    return pd.read_csv(ruta)

def normalizar_equipo(nombre):
    return nombre.upper()\
        .replace(".", "")\
        .replace(",", "")\
        .replace("Á", "A")\
        .replace("É", "E")\
        .replace("Í", "I")\
        .replace("Ó", "O")\
        .replace("Ú", "U")\
        .replace("'", "")\
        .replace('"', "")

# --- Funciones auxiliares ---
def mostrar_eventos_lineas(eventos):
    eventos = eventos.copy()
    eventos["minuto_num"] = eventos["minuto"].apply(lambda x: int(str(x).replace("'", "").replace("+", "")) if pd.notna(x) else 0)
    eventos = eventos.sort_values("minuto_num")

    for _, row in eventos.iterrows():
        tipo = row["evento"]
        minuto = row["minuto"]
        equipo = row["equipo"]

        if tipo == "gol":
            desc = f"⚽ Gol de {row['jugador']}"
        elif tipo == "tarjeta amarilla":
            desc = f"🟨 Amarilla a {row['jugador']}"
        elif tipo == "tarjeta roja":
            desc = f"🟥 Roja a {row['jugador']}"
        elif tipo == "sustitucion":
            desc = f"🔁 Entra {row['jugador_entra']} por {row['jugador_sale']}"
        else:
            desc = "❓ Evento desconocido"

        st.markdown(f"<div style='font-size: 0.75rem; margin-bottom: 2px;'>⏱️ {minuto}' - {desc} <span style='color: #888;'>({equipo})</span></div>", unsafe_allow_html=True)


def mostrar_escudo(nombre_equipo):
    base_dir = os.path.dirname(__file__)
    nombre_archivo = normalizar_equipo(nombre_equipo) + ".png"
    ruta = os.path.join(base_dir,"Data/Escudos", nombre_archivo)
    if os.path.exists(ruta):
        st.image(ruta, width=40)
    else:
        st.markdown("⚪", unsafe_allow_html=True)

# --- App ---
df = load_data()
eventos_df = load_eventos()

# Sidebar de filtros
competiciones = sorted(df["competicion"].unique())
grupos = sorted(df["grupo"].unique())
jornadas = sorted(df["jornada"].unique())

competicion_sel = st.sidebar.selectbox("🏆 Competición", competiciones)
grupo_sel = st.sidebar.selectbox("📁 Grupo", grupos)
jornada_sel = st.sidebar.selectbox("🗓️ Jornada", jornadas)

# Filtrar partidos
filtros_df = df[
    (df["competicion"] == competicion_sel) &
    (df["grupo"] == grupo_sel) &
    (df["jornada"] == jornada_sel)
]

# --- Fila 1: escudo arriba a la derecha ---
fila1_col1, fila1_col2 = st.columns([10, 1.75])
with fila1_col1:
    pagina = st.radio(
    "Navegación",
    options=["Partidos", "Clasificación", "Evolución temporada"],
    horizontal=True,
    label_visibility="collapsed"
)
with fila1_col2:
    base_dir = os.path.dirname(__file__)  # carpeta donde está Resultados.py
    ruta = os.path.join(base_dir, "escudo.png")
    st.image(ruta, width=50)

# --- Fila 2: texto centrado debajo ---

fila1_col1, fila1_col2 = st.columns([10, 3.5])
with fila1_col2:
    st.markdown(
        "<div style='text-align:center; font-size: 0.85rem; color: #555; margin-top: -0.5rem;'>"
        "Plataforma de datos del club</div>",
        unsafe_allow_html=True
    )


# Menú
st.markdown("<hr style='margin-top: 0rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

# Contenido por pestaña
if pagina == "Partidos":
    # KPIs base
    total_partidos = len(filtros_df)
    goles_totales = filtros_df["goles_local"].sum() + filtros_df["goles_visitante"].sum()
    media_goles = round(goles_totales / total_partidos, 2) if total_partidos else 0

    victorias_local = (filtros_df["goles_local"] > filtros_df["goles_visitante"]).sum()
    victorias_visitante = (filtros_df["goles_local"] < filtros_df["goles_visitante"]).sum()
    empates = (filtros_df["goles_local"] == filtros_df["goles_visitante"]).sum()

    goles_por_equipo = pd.concat([
        filtros_df[["equipo_local", "goles_local"]].rename(columns={"equipo_local": "equipo", "goles_local": "goles"}),
        filtros_df[["equipo_visitante", "goles_visitante"]].rename(columns={"equipo_visitante": "equipo", "goles_visitante": "goles"})
    ])
    conteo_goles = goles_por_equipo.groupby("equipo")["goles"].sum()
    max_goles = conteo_goles.max()
    equipos_top = conteo_goles[conteo_goles == max_goles].index.tolist()
    top_goleador = ", ".join(equipos_top) + f" ({max_goles} goles)"

    porterias_cero = (
        (filtros_df["goles_visitante"] == 0).sum() +
        (filtros_df["goles_local"] == 0).sum()
    )

    filtros_df["total_goles"] = filtros_df["goles_local"] + filtros_df["goles_visitante"]
    partido_max_goles = filtros_df.loc[filtros_df["total_goles"].idxmax()]
    partido_top = f"{partido_max_goles['equipo_local']} {partido_max_goles['goles_local']}-{partido_max_goles['goles_visitante']} {partido_max_goles['equipo_visitante']}"

    # Título
    st.markdown(f"""
    <h3 style='margin-top: -1rem; margin-bottom: 0.2rem;'>📋 Resultados · Jornada {jornada_sel}</h3>
    <h4 style='margin-top: -1rem; color: grey; font-weight: normal;'>{competicion_sel} · {grupo_sel}</h4>
    """, unsafe_allow_html=True)

    # Mostrar resumen
    with st.expander("📊 Resumen de jornada", expanded=False):
        col_kpi, col_plot = st.columns([2, 1])
        with col_kpi:
            st.markdown(f"""
            - 🔢 **Partidos**: {total_partidos}  
            - 🎯 **Goles totales**: {goles_totales}  
            - ⚖️ **Media goles/partido**: {media_goles}  
            - 🥇 **Equipo más goleador**: {top_goleador}    
            - 🧤 **Porterías a cero**: {porterias_cero}  
            - 🔥 **Partido con más goles**: {partido_top}
            """)

        with col_plot:
            fig, ax = plt.subplots(figsize=(3.2, 2.4))
            resultados = [victorias_local, empates, victorias_visitante]
            etiquetas = ["Local", "Empate", "Visitante"]
            colores = ["#8BC34A", "#FFB74D", "#64B5F6"]
            barras = ax.bar(etiquetas, resultados, color=colores, edgecolor="none")
            ax.set_title("Distribución de resultados", fontsize=10)
            ax.tick_params(axis='both', labelsize=9)
            ax.set_ylim(0, max(resultados) + 1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            for barra in barras:
                yval = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=9)
            st.pyplot(fig)

    # Mostrar partidos
    for _, row in filtros_df.iterrows():
        st.markdown("---")
        empty,esc1, resultado, esc2 = st.columns([0.65,0.5, 2, 1], gap="small")
        with empty:
            pass  # espacio en blanco
        with esc1:
            st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
            mostrar_escudo(row["equipo_local"])
            st.markdown("</div>", unsafe_allow_html=True)
        with resultado:
            st.markdown(
                f"<h5 style='text-align:center; margin: 5px 0; margin-top:40px'> {row['goles_local']} - {row['goles_visitante']}</h5>",
                unsafe_allow_html=True
            )
        with esc2:
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            mostrar_escudo(row["equipo_visitante"])
            st.markdown("</div>", unsafe_allow_html=True)

        nom1, espacio, nom2 = st.columns([2, 1, 2], gap="small")
        with nom1:
            st.markdown(f"<div style='text-align:center; font-size: 0.85rem; margin-top:-20px;'><b>{row['equipo_local']}</b></div>", unsafe_allow_html=True)
        with espacio:
            st.markdown("<div style='height: 1px;'>&nbsp;</div>", unsafe_allow_html=True)
        with nom2:
            st.markdown(f"<div style='text-align:center; font-size: 0.85rem; margin-top:-20px;'><b>{row['equipo_visitante']}</b></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align:center; font-size: 0.85rem; color: #444; margin-top: 10px;'>
            🗓️ {row['fecha']} {row['hora']} |
            📍 {row['estadio']} |
            🌱 {row['superficie']} |
            🧑‍⚖️ {row['árbitro']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align:center; font-size: 0.85rem; color: #555; margin-top: 2px;'>
            📄 <a href="{row['link_acta']}" target="_blank">Ver acta del partido</a>
        </div>
        """, unsafe_allow_html=True)

        eventos_partido = eventos_df[
            (eventos_df["categoria"] == row["categoria"]) &
            (eventos_df["competicion"] == row["competicion"]) &
            (eventos_df["grupo"] == row["grupo"]) &
            (eventos_df["jornada"].astype(str) == str(row["jornada"])) &
            (eventos_df["equipo_local"] == row["equipo_local"]) &
            (eventos_df["equipo_visitante"] == row["equipo_visitante"])]

        if not eventos_partido.empty:
            with st.expander("📋 Ver eventos del partido"):
                mostrar_eventos_lineas(eventos_partido)


    st.markdown("---")
    st.caption("Desarrollado con ❤️ por tu app de análisis RFGF")
elif pagina == "Clasificación":
    st.markdown(f"""
    <h3 style='margin-top: -1rem; margin-bottom: 0.2rem;'>📈 Clasificación · Hasta la jornada {jornada_sel}</h3>
    <h4 style='margin-top: -1rem; color: grey; font-weight: normal;'>{competicion_sel} · {grupo_sel}</h4>
    """, unsafe_allow_html=True)

    # Filtrar partidos hasta la jornada seleccionada
    df_filtrado = df[
        (df["competicion"] == competicion_sel) &
        (df["grupo"] == grupo_sel) &
        (df["jornada"] <= jornada_sel)
    ]

    # Equipos únicos
    equipos = pd.concat([df_filtrado["equipo_local"], df_filtrado["equipo_visitante"]]).unique()
    clasificacion = pd.DataFrame(equipos, columns=["equipo"])
    clasificacion.set_index("equipo", inplace=True)
    clasificacion[["PJ", "G", "GC", "V", "E", "D", "P"]] = 0

    # Contabilizar estadísticas
    for _, row in df_filtrado.iterrows():
        local = row["equipo_local"]
        visitante = row["equipo_visitante"]
        g_local = row["goles_local"]
        g_visit = row["goles_visitante"]

        # PJ
        clasificacion.at[local, "PJ"] += 1
        clasificacion.at[visitante, "PJ"] += 1

        # Goles
        clasificacion.at[local, "G"] += g_local
        clasificacion.at[local, "GC"] += g_visit
        clasificacion.at[visitante, "G"] += g_visit
        clasificacion.at[visitante, "GC"] += g_local

        # Resultados
        if g_local > g_visit:
            clasificacion.at[local, "V"] += 1
            clasificacion.at[visitante, "D"] += 1
        elif g_local < g_visit:
            clasificacion.at[visitante, "V"] += 1
            clasificacion.at[local, "D"] += 1
        else:
            clasificacion.at[local, "E"] += 1
            clasificacion.at[visitante, "E"] += 1

    # Sistema de puntos
    p_v, p_e, p_d = 3, 1, 0
    clasificacion["P"] = clasificacion["V"] * p_v + clasificacion["E"] * p_e + clasificacion["D"] * p_d
    clasificacion["DG"] = clasificacion["G"] - clasificacion["GC"]

    # Ordenar por clasificación
    clasificacion = clasificacion.sort_values(by=["P", "DG", "G"], ascending=False).reset_index()

    def ordinal(n):
        return f"{n}º"
    
    with st.expander("🗂️ Leyenda de colores", expanded=False):
        st.markdown("""
        <div style='font-size: 0.85rem; line-height: 1.6;'>
            <span style='background-color:#FFD700; padding:2px 6px; border-radius:3px;'>1º</span> 🥇 Lider del grupo<br>
            <span style='background-color:#C8E6C9; padding:2px 6px; border-radius:3px;'>2º</span> 🟢 Fase de ascenso<br>
            <span style='background-color:#BBDEFB; padding:2px 6px; border-radius:3px;'>3º</span> 🔵 Mejor tercero<br>
            <span style='background-color:#FFCDD2; padding:2px 6px; border-radius:3px;'>Últimos</span> 🔴 Descenso
        </div>
        """, unsafe_allow_html=True)

    for idx, row in clasificacion.iterrows():
        if idx == 0:
            bg_color = "#FFD700"
        elif idx == 1:
            bg_color = "#C8E6C9"
        elif idx == 2:
            bg_color = "#BBDEFB"
        elif idx >= len(clasificacion) - 2:
            bg_color = "#FFCDD2"
        else:
            bg_color = "#F5F5F5"

        pos_col, esc_col, info_col = st.columns([0.4, 0.5, 6])

        with pos_col:
            st.markdown(
                f"<div style='text-align:center; font-size: 0.85rem; font-weight:bold; margin-top: 2px;'>{ordinal(idx+1)}</div>",
                unsafe_allow_html=True
            )

        with esc_col:
            nombre_archivo = normalizar_equipo(row["equipo"]) + ".png"
            ruta_escudo = os.path.join("escudos", nombre_archivo)
            if os.path.exists(ruta_escudo):
                st.image(ruta_escudo, width=22)
            else:
                st.markdown("<div style='font-size: 0.7rem;'>⚪</div>", unsafe_allow_html=True)

        with info_col:
            st.markdown(f"""
            <div style='font-size: 0.72rem; line-height: 1.15; font-family: monospace; background-color: {bg_color}; padding: 2px 6px; border-radius: 3px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='font-family: sans-serif; font-weight: 600;'>{row['equipo']}</span>
                    <span>{str(row['P']).rjust(2)} pts</span>
                </div>
                <div>
                    PJ:{str(row['PJ']).rjust(2)} G:{str(row['G']).rjust(2)} GC:{str(row['GC']).rjust(2)} DG:{str(row['DG']).rjust(3)} V:{str(row['V']).rjust(2)} E:{str(row['E']).rjust(2)} D:{str(row['D']).rjust(2)}
                </div>
            </div>
            """, unsafe_allow_html=True)

elif pagina == "Evolución temporada":
    st.markdown(f"""
    <h3 style='margin-top: -1rem; margin-bottom: 0.2rem;'>📈 Evolución de posiciones</h3>
    <h4 style='margin-top: -1rem; color: grey; font-weight: normal;'>{competicion_sel} · {grupo_sel} · hasta jornada {jornada_sel}</h4>
    """, unsafe_allow_html=True)

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import numpy as np

    # Filtrar partidos hasta jornada seleccionada
    df_evo = df[
        (df["competicion"] == competicion_sel) &
        (df["grupo"] == grupo_sel) &
        (df["jornada"] <= jornada_sel)
    ]

    jornadas_disponibles = sorted(df_evo["jornada"].unique())
    evolucion = []

    for j in jornadas_disponibles:
        df_j = df_evo[df_evo["jornada"] <= j]
        equipos_j = pd.concat([df_j["equipo_local"], df_j["equipo_visitante"]]).unique()
        tabla = pd.DataFrame(equipos_j, columns=["equipo"])
        tabla.set_index("equipo", inplace=True)
        tabla[["PJ", "G", "GC", "V", "E", "D", "P"]] = 0

        for _, row in df_j.iterrows():
            l, v = row["equipo_local"], row["equipo_visitante"]
            gl, gv = row["goles_local"], row["goles_visitante"]
            tabla.at[l, "PJ"] += 1
            tabla.at[v, "PJ"] += 1
            tabla.at[l, "G"] += gl
            tabla.at[l, "GC"] += gv
            tabla.at[v, "G"] += gv
            tabla.at[v, "GC"] += gl
            if gl > gv:
                tabla.at[l, "V"] += 1
                tabla.at[v, "D"] += 1
            elif gl < gv:
                tabla.at[v, "V"] += 1
                tabla.at[l, "D"] += 1
            else:
                tabla.at[l, "E"] += 1
                tabla.at[v, "E"] += 1

        tabla["P"] = tabla["V"] * 3 + tabla["E"]
        tabla["DG"] = tabla["G"] - tabla["GC"]
        tabla = tabla.sort_values(by=["P", "DG", "G"], ascending=False)
        tabla["pos"] = range(1, len(tabla) + 1)
        tabla["jornada"] = j
        tabla.reset_index(inplace=True)
        evolucion.append(tabla[["equipo", "jornada", "pos", "P"]])

    evolucion_df = pd.concat(evolucion)
    pivot = evolucion_df.pivot(index="jornada", columns="equipo", values="pos")

    # Selector multiequipo
    equipos_disponibles = list(pivot.columns)
    equipos_seleccionados = st.multiselect("👥 Selecciona equipos a mostrar", equipos_disponibles, default=equipos_disponibles)

    # Generar colores únicos para equipos seleccionados
    cmap = cm.get_cmap('tab20', len(equipos_disponibles))
    colores_dict = {equipo: cm.colors.to_hex(cmap(i)) for i, equipo in enumerate(equipos_disponibles)}

    # Calcular puntos finales
    final_jornada = evolucion_df[evolucion_df["jornada"] == jornada_sel][["equipo", "P"]].sort_values(by="P", ascending=False).reset_index(drop=True)

    # Gráficos en paralelo
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Puntos acumulados")
        puntos_mostrar = final_jornada.sort_values(by="P", ascending=True)
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        colores_barras = [colores_dict.get(e, "#BDBDBD") for e in puntos_mostrar["equipo"]]
        ax2.barh(puntos_mostrar["equipo"], puntos_mostrar["P"], color=colores_barras)
        ax2.set_xlabel("Puntos")
        ax2.set_title("Puntos hasta jornada seleccionada", fontsize=10)
        for i, v in enumerate(puntos_mostrar["P"]):
            ax2.text(v + 0.3, i, str(v), va='center', fontsize=8)
        fig2.tight_layout()
        st.pyplot(fig2)

    with col2:
        st.markdown("#### 📊 Posición por jornada")
        fig, ax = plt.subplots(figsize=(6, 6))
        num_equipos = len(pivot.columns)

        for equipo in equipos_seleccionados:
            if equipo in pivot.columns:
                posiciones_equipo = pivot[equipo].dropna()
                color = colores_dict.get(equipo, "#BDBDBD")
                ax.plot(posiciones_equipo.index, posiciones_equipo, marker='o', linewidth=1.3, label=equipo, color=color)

        # Mostrar solo algunas jornadas para evitar solapamiento
        total_jornadas = len(pivot.index)
        if total_jornadas <= 10:
            salto = 1
        elif total_jornadas <= 20:
            salto = 2
        elif total_jornadas <= 30:
            salto = 3
        else:
            salto = 4

        ax.set_xticks(pivot.index[::salto])
        ax.set_yticks(range(1, num_equipos + 1))
        ax.set_ylim(num_equipos + 0.5, 0.5)
        ax.set_xlabel("Jornada")
        ax.set_ylabel("Posición")
        ax.set_title("Evolución de posiciones", fontsize=10)
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
        fig.tight_layout()
        st.pyplot(fig)

st.markdown("<hr style='margin-top: 0rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

