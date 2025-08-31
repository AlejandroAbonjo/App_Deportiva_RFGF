
import pandas as pd

def generar_participacion(path_jugadores, path_sustituciones, path_partidos, path_competiciones, output_path):
    jugadores_df = pd.read_csv(path_jugadores)
    sustituciones_df = pd.read_csv(path_sustituciones)
    partidos_df = pd.read_csv(path_partidos)
    competiciones_df = pd.read_csv(path_competiciones)

    # Preparar partidos con info de competiciones
    partidos_comp = partidos_df.merge(
        competiciones_df,
        on=["cod_competicion", "cod_grupo"],
        how="left"
    )[["cod_acta", "jornada", "equipo_local", "equipo_visitante", "categoria", "competicion", "grupo"]]

    equipos = []
    for _, row in partidos_comp.iterrows():
        equipos.append({
            "cod_acta": row["cod_acta"],
            "jornada": row["jornada"],
            "categoria": row["categoria"],
            "competicion": row["competicion"],
            "grupo": row["grupo"],
            "equipo": row["equipo_local"],
            "rival": row["equipo_visitante"],
            "local_visitante": "local"
        })
        equipos.append({
            "cod_acta": row["cod_acta"],
            "jornada": row["jornada"],
            "categoria": row["categoria"],
            "competicion": row["competicion"],
            "grupo": row["grupo"],
            "equipo": row["equipo_visitante"],
            "rival": row["equipo_local"],
            "local_visitante": "visitante"
        })
    equipos_df = pd.DataFrame(equipos)

    jugadores_df["status"] = jugadores_df["status"].str.lower()

    sustituciones_df["num_sustitucion"] = sustituciones_df.sort_values(by=["cod_acta", "equipo", "minuto"])        .groupby(["cod_acta", "equipo"]).cumcount() + 1

    entradas = sustituciones_df.rename(columns={"jugador_entra": "jugador", "minuto": "minuto_entra"})[
        ["cod_acta", "equipo", "jugador", "minuto_entra"]
    ]

    salidas = sustituciones_df[["cod_acta", "equipo", "jugador_sale", "minuto"]].rename(
        columns={"jugador_sale": "jugador", "minuto": "minuto_sale"}
    )

    jugadores = jugadores_df.merge(entradas, on=["cod_acta", "equipo", "jugador"], how="left")
    jugadores = jugadores.merge(salidas, on=["cod_acta", "equipo", "jugador"], how="left")

    def tipo_participacion(row):
        if row["status"] == "titular":
            return "titular todo partido" if pd.isna(row["minuto_sale"]) else "titular sustituido"
        else:
            return "suplente participa" if pd.notna(row["minuto_entra"]) else "suplente no participa"

    def calcular_minutos(row):
        if row["status"] == "titular":
            return 90 if pd.isna(row["minuto_sale"]) else int(row["minuto_sale"])
        else:
            return 90 - int(row["minuto_entra"]) if pd.notna(row["minuto_entra"]) else 0

    jugadores["tipo_participacion"] = jugadores.apply(tipo_participacion, axis=1)
    jugadores["minutos_jugados"] = jugadores.apply(calcular_minutos, axis=1)

    jugadores = jugadores.merge(equipos_df, on=["cod_acta", "equipo"], how="left")

    jugadores["dorsal"] = jugadores["numero"]
    jugadores["jugador"] = jugadores["jugador"].str.replace(r"^\d+\s-\s", "", regex=True)

    jugadores["jornada"] = jugadores["jornada"].astype("Int64")

    participacion_final = jugadores[[
        "categoria", "competicion", "grupo", "jornada", "cod_acta", "equipo", "rival",
        "local_visitante", "dorsal", "jugador", "status", "tipo_participacion", "minutos_jugados"
    ]]

    participacion_final.to_csv(output_path, index=False)
    print(f"Archivo guardado en {output_path}")


generar_participacion(
    path_jugadores="C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\jugadores.csv",
    path_sustituciones="C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\sustituciones.csv",
    path_partidos="C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Partidos.csv",
    path_competiciones="C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Todas_Competiciones.csv",
    output_path="participacion.csv"
)
