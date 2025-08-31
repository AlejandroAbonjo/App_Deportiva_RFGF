import pandas as pd
from extraccion_actas_utils import *


# Leer el archivo CSV
df = pd.read_csv("Listado_Partidos.csv")

# Asegurar que la columna cod_acta existe
if 'cod_acta' in df.columns:
    lista_cod_acta = df['cod_acta'].dropna().astype(str).unique().tolist()
else:
    print("La columna 'cod_acta' no existe en el archivo.")

for cod_acta in lista_cod_acta:
    print(f"\n Procesando acta {cod_acta}\n")
    procesar_acta(cod_acta)
