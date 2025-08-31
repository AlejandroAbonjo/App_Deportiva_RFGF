import pandas as pd

# Cargar los archivos
goles_df = pd.read_csv("C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\goles.csv")
partidos_df = pd.read_csv("C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Partidos.csv")
competiciones_df = pd.read_csv("C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Todas_Competiciones.csv")

# Función para normalizar nombres de equipo
def limpiar_equipo(nombre):
    if pd.isna(nombre):
        return ""
    return nombre.replace('"', '').strip().upper()

def calcular_puntos(goles_local, goles_visitante):
    if goles_local > goles_visitante:
        return 3, 0
    elif goles_local < goles_visitante:
        return 0, 3
    else:
        return 1, 1

# Normalizar nombres
goles_df["equipo"] = goles_df["equipo"].apply(limpiar_equipo)
partidos_df["equipo_local"] = partidos_df["equipo_local"].apply(limpiar_equipo)
partidos_df["equipo_visitante"] = partidos_df["equipo_visitante"].apply(limpiar_equipo)

# Unir partidos con competiciones
partidos_completos = partidos_df.merge(
    competiciones_df,
    how="left",
    on=["cod_competicion", "cod_grupo"]
)

# Contar goles por cod_acta y equipo
goles_contados = goles_df.groupby(["cod_acta", "equipo"]).size().reset_index(name="goles")

# Asignar goles a equipos local y visitante
partidos_completos = partidos_completos.merge(
    goles_contados,
    how="left",
    left_on=["cod_acta", "equipo_local"],
    right_on=["cod_acta", "equipo"]
).rename(columns={"goles": "goles_local"}).drop(columns=["equipo"])

partidos_completos = partidos_completos.merge(
    goles_contados,
    how="left",
    left_on=["cod_acta", "equipo_visitante"],
    right_on=["cod_acta", "equipo"]
).rename(columns={"goles": "goles_visitante"}).drop(columns=["equipo"])

# Rellenar nulos con 0
partidos_completos["goles_local"] = partidos_completos["goles_local"].fillna(0).astype(int)
partidos_completos["goles_visitante"] = partidos_completos["goles_visitante"].fillna(0).astype(int)

# Calcular resultado
partidos_completos["resultado"] = partidos_completos["goles_local"].astype(str) + "-" + partidos_completos["goles_visitante"].astype(str)

# Guardar resultados de partidos
partidos_completos[[
    "categoria", "competicion", "grupo", "jornada", "fecha", "hora", "estadio",
    "superficie", "árbitro", "equipo_local", "equipo_visitante",
    "goles_local", "goles_visitante", "resultado", "link_acta"
]].to_csv("resultados_partidos.csv", index=False)

# Calcular puntos y rival
local = partidos_completos.copy()
local["equipo"] = local["equipo_local"]
local["rival"] = local["equipo_visitante"]
local["local_visitante"] = "local"
local["puntos"] = local.apply(lambda row: calcular_puntos(row["goles_local"], row["goles_visitante"])[0], axis=1)

visitante = partidos_completos.copy()
visitante["equipo"] = visitante["equipo_visitante"]
visitante["rival"] = visitante["equipo_local"]
visitante["local_visitante"] = "visitante"
visitante["puntos"] = visitante.apply(lambda row: calcular_puntos(row["goles_local"], row["goles_visitante"])[1], axis=1)

# Selección y unión
local = local[["categoria", "competicion", "grupo", "jornada", "equipo", "rival", "local_visitante", "puntos"]]
visitante = visitante[["categoria", "competicion", "grupo", "jornada", "equipo", "rival", "local_visitante", "puntos"]]
puntos_df = pd.concat([local, visitante], ignore_index=True)

# Guardar puntos
puntos_df.to_csv("puntos.csv", index=False)
