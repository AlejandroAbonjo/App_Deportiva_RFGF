import pandas as pd


def limpiar_equipo(nombre):
    if pd.isna(nombre):
        return ""
    return nombre.replace('"', '').strip().upper()


def convertir_minuto(minuto):
    try:
        if isinstance(minuto, str):
            minuto = minuto.replace("'", "").split("+")[0]
        return int(minuto)
    except:
        return 0


def crear_csv_eventos(path_goles, path_sanciones, path_sustituciones, path_partidos, path_competiciones, output_path):
    # Cargar archivos
    goles = pd.read_csv(path_goles)
    sanciones = pd.read_csv(path_sanciones)
    sustituciones = pd.read_csv(path_sustituciones)
    partidos = pd.read_csv(path_partidos)
    competiciones = pd.read_csv(path_competiciones)

    # Normalizar nombres
    for df in [goles, sanciones, sustituciones]:
        df["equipo"] = df["equipo"].apply(limpiar_equipo)
    partidos["equipo_local"] = partidos["equipo_local"].apply(limpiar_equipo)
    partidos["equipo_visitante"] = partidos["equipo_visitante"].apply(limpiar_equipo)

    # Goles
    goles_eventos = goles.copy()
    goles_eventos["evento"] = "gol"
    goles_eventos["jugador_entra"] = None
    goles_eventos["jugador_sale"] = None
    goles_eventos["tipo_gol"] = goles_eventos["tipo_gol"].str.lower()
    goles_eventos["num_sustitucion"] = None
    goles_eventos["minuto_orden"] = goles_eventos["minuto"].apply(convertir_minuto)
    goles_eventos["parte"] = goles_eventos["minuto_orden"].apply(lambda x: 1 if x <= 45 else 2)
    goles_eventos = goles_eventos[["cod_acta", "evento", "minuto", "parte", "jugador", "jugador_entra", "jugador_sale", "equipo", "tipo_gol", "num_sustitucion", "minuto_orden"]]

    # Sanciones
    sanciones_eventos = sanciones.copy()
    sanciones_eventos["evento"] = sanciones_eventos["tipo_tarjeta"].map({"Amarilla": "tarjeta amarilla", "Roja": "tarjeta roja"})
    sanciones_eventos["jugador_entra"] = None
    sanciones_eventos["jugador_sale"] = None
    sanciones_eventos["tipo_gol"] = None
    sanciones_eventos["num_sustitucion"] = None
    sanciones_eventos["minuto_orden"] = sanciones_eventos["minuto"].apply(convertir_minuto)
    sanciones_eventos["parte"] = sanciones_eventos["minuto_orden"].apply(lambda x: 1 if x <= 45 else 2)
    sanciones_eventos = sanciones_eventos[["cod_acta", "evento", "minuto", "parte", "jugador", "jugador_entra", "jugador_sale", "equipo", "tipo_gol", "num_sustitucion", "minuto_orden"]]

    # Sustituciones
    sust_eventos = sustituciones.copy()
    sust_eventos["evento"] = "sustitucion"
    sust_eventos["jugador"] = None
    sust_eventos["tipo_gol"] = None
    sust_eventos["num_sustitucion"] = sust_eventos.groupby(["cod_acta", "equipo"]).cumcount() + 1
    sust_eventos["parte"] = sust_eventos["minuto"].apply(lambda x: 1 if x <= 45 else 2)
    sust_eventos["minuto_orden"] = sust_eventos["minuto"].apply(convertir_minuto)
    sust_eventos = sust_eventos[["cod_acta", "evento", "minuto", "parte", "jugador", "jugador_entra", "jugador_sale", "equipo", "tipo_gol", "num_sustitucion", "minuto_orden"]]

    # Unir eventos
    eventos = pd.concat([goles_eventos, sanciones_eventos, sust_eventos], ignore_index=True)

    # Añadir info partidos y competiciones
    eventos = eventos.merge(partidos[["cod_acta", "jornada", "equipo_local", "equipo_visitante", "cod_competicion", "cod_grupo"]], on="cod_acta", how="left")
    eventos = eventos.merge(competiciones[["cod_competicion", "cod_grupo", "categoria", "competicion", "grupo"]], on=["cod_competicion", "cod_grupo"], how="left")

    # Añadir local_visitante, rival
    eventos["local_visitante"] = eventos.apply(lambda row: "local" if row["equipo"] == row["equipo_local"] else "visitante", axis=1)
    eventos["rival"] = eventos.apply(lambda row: row["equipo_visitante"] if row["local_visitante"] == "local" else row["equipo_local"], axis=1)

    # Ordenar eventos
    eventos = eventos.sort_values(by=["jornada", "cod_acta", "minuto_orden"]).reset_index(drop=True)

    # Calcular resultado parcial por cod_acta minuto a partir de los goles registrados
    goles_ordenados = goles.copy()
    goles_ordenados["minuto_orden"] = goles_ordenados["minuto"].apply(convertir_minuto)
    goles_ordenados = goles_ordenados.sort_values(by=["cod_acta", "minuto_orden"]).reset_index(drop=True)
    goles_ordenados["tipo_gol"] = goles_ordenados["tipo_gol"].str.lower()
    goles_ordenados["gol_local"] = goles_ordenados.apply(lambda row: 1 if row["tipo_gol"] != "propia puerta" and row["equipo"] == partidos.set_index("cod_acta").loc[row["cod_acta"], "equipo_local"] else 0, axis=1)
    goles_ordenados["gol_visitante"] = goles_ordenados.apply(lambda row: 1 if row["tipo_gol"] != "propia puerta" and row["equipo"] == partidos.set_index("cod_acta").loc[row["cod_acta"], "equipo_visitante"] else 0, axis=1)
    goles_ordenados["gol_local"] += goles_ordenados.apply(lambda row: 1 if row["tipo_gol"] == "propia puerta" and row["equipo"] == partidos.set_index("cod_acta").loc[row["cod_acta"], "equipo_visitante"] else 0, axis=1)
    goles_ordenados["gol_visitante"] += goles_ordenados.apply(lambda row: 1 if row["tipo_gol"] == "propia puerta" and row["equipo"] == partidos.set_index("cod_acta").loc[row["cod_acta"], "equipo_local"] else 0, axis=1)
    goles_ordenados["goles_local"] = goles_ordenados.groupby("cod_acta")["gol_local"].cumsum()
    goles_ordenados["goles_visitante"] = goles_ordenados.groupby("cod_acta")["gol_visitante"].cumsum()
    goles_ordenados["resultado_parcial"] = goles_ordenados["goles_local"].astype(str) + "-" + goles_ordenados["goles_visitante"].astype(str)
    goles_resultado = goles_ordenados[["cod_acta", "minuto_orden", "resultado_parcial"]]

    # Asignar resultado parcial al evento más reciente anterior o igual al minuto del evento
    # Crear un diccionario por cod_acta con lista ordenada de (minuto_orden, resultado_parcial)
    goles_dict = (
        goles_resultado
        .sort_values(["cod_acta", "minuto_orden"])
        .groupby("cod_acta")[["minuto_orden", "resultado_parcial"]]
        .apply(lambda df: list(zip(df["minuto_orden"], df["resultado_parcial"])))
        .to_dict()
    )

    # Función que busca el resultado más reciente antes o igual al minuto del evento
    def buscar_resultado_parcial(cod_acta, minuto_orden):
        eventos_partido = goles_dict.get(cod_acta, [])
        resultado = "0-0"
        for min_gol, res in eventos_partido:
            if min_gol <= minuto_orden:
                resultado = res
            else:
                break
        return resultado

    # Aplicar búsqueda al DataFrame de eventos
    eventos["resultado_parcial"] = eventos.apply(
        lambda row: buscar_resultado_parcial(row["cod_acta"], row["minuto_orden"]),
        axis=1
    )


    # Reordenar columnas
    eventos_final = eventos[[
        "categoria", "competicion", "grupo", "jornada", "cod_acta", 
        "equipo_local", "equipo_visitante", "equipo", "rival" , "local_visitante", "evento", "minuto", 
        "parte", "jugador", "tipo_gol", "jugador_entra", "jugador_sale", 
        "num_sustitucion", "resultado_parcial"
    ]]

    # Guardar archivo final
    eventos_final.to_csv(output_path, index=False)
    print(f"Archivo de eventos guardado en: {output_path}")

# Ejemplo de uso:
crear_csv_eventos("C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\goles.csv",
                   "C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\sanciones.csv", 
                   "C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\sustituciones.csv", 
                   "C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Partidos.csv", 
                   "C:\\Users\\alejandro.abonjo\\Documents\\RFGF\\Extraccion\\Listado_Todas_Competiciones.csv", 
                   "Eventos_partidos.csv")
