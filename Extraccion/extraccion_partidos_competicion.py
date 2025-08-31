import pandas as pd
from tabulate import tabulate
from extraccion_competiciones_utils import *

cod_temporada=20
# Cargar el CSV
df = pd.read_csv("Listado_Todas_Competiciones.csv")

# Paso 1: Mostrar categorías únicas numeradas
categorias_unicas = sorted(df['categoria'].unique())
df_categorias = pd.DataFrame({
    "Número": list(range(1, len(categorias_unicas) + 1)),
    "Categoría": categorias_unicas
})
print("🎯 Categorías disponibles:\n")
print(tabulate(df_categorias, headers='keys', tablefmt='fancy_grid', showindex=False))

try:
    # Paso 2: Selección de categoría
    seleccion_categoria = int(input("\nIntroduce el número de la categoría que deseas filtrar: "))
    if 1 <= seleccion_categoria <= len(categorias_unicas):
        categoria_elegida = categorias_unicas[seleccion_categoria - 1]

        # Paso 3: Mostrar competiciones únicas numeradas
        df_competiciones_filtrado = (
            df[df['categoria'] == categoria_elegida][['cod_competicion', 'competicion']]
            .drop_duplicates()
            .sort_values(by='competicion')
            .reset_index(drop=True)
        )
        df_competiciones_filtrado.insert(0, "Número", df_competiciones_filtrado.index + 1)

        print(f"\n✅ Competiciones para la categoría: {categoria_elegida}\n")
        print(tabulate(df_competiciones_filtrado, headers='keys', tablefmt='fancy_grid', showindex=False))

        # Paso 4: Selección de competición
        seleccion_competicion = int(input("\nIntroduce el número de la competición que deseas ver: "))
        if 1 <= seleccion_competicion <= len(df_competiciones_filtrado):
            cod_competicion = df_competiciones_filtrado.loc[seleccion_competicion - 1, 'cod_competicion']
            df_competicion = df[df['cod_competicion'] == cod_competicion]

            # Paso 5: Mostrar grupos únicos numerados
            df_grupos = (
                df_competicion[['cod_grupo', 'grupo']]
                .drop_duplicates()
                .sort_values(by='grupo')
                .reset_index(drop=True)
            )
            df_grupos.insert(0, "Número", df_grupos.index + 1)

            print(f"\n📋 Grupos de la competición seleccionada (cod_competicion = {cod_competicion}):\n")
            print(tabulate(df_grupos, headers='keys', tablefmt='fancy_grid', showindex=False))

            # Paso 6: Selección de grupo
            seleccion_grupo = int(input("\nIntroduce el número del grupo que deseas seleccionar: "))
            if 1 <= seleccion_grupo <= len(df_grupos):
                cod_grupo = df_grupos.loc[seleccion_grupo - 1, 'cod_grupo']
            else:
                print("❌ Número de grupo fuera de rango.")
        else:
            print("❌ Número de competición fuera de rango.")
    else:
        print("❌ Número de categoría fuera de rango.")
except ValueError:
    print("❌ Entrada no válida. Por favor, introduce un número.")


# Lista para guardar los DataFrames de cada jornada
dfs_jornadas = []

for jornada in range(1, 40):  # de la 1 a la 34 inclusive
    print(f"Extrayendo jornada {jornada}...")
    df_jornada = extraccion_jornada(cod_competicion, cod_grupo, cod_temporada, jornada)
    dfs_jornadas.append(df_jornada)

# Unir todo en un único DataFrame
df_todas_jornadas = pd.concat(dfs_jornadas, ignore_index=True)

# Guardar si quieres
df_todas_jornadas.to_csv('./Listado_Partidos.csv', index=False)