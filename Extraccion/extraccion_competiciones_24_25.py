import requests  # Librería para realizar solicitudes HTTP a páginas web
from bs4 import BeautifulSoup  # Librería para analizar documentos HTML y extraer datos
import os  # Librería para interactuar con el sistema operativo, por ejemplo, para crear carpetas
import pandas as pd  # Librería para manipular datos y trabajar con estructuras como DataFrames
import time  # Librería para manejar tiempos y pausas
import random  # Librería para generar valores aleatorios
import re  # Librería para trabajar con expresiones regulares
from urllib.parse import parse_qsl, urljoin, urlparse
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from extraccion_competiciones_utils import *
from urllib.parse import urlparse, parse_qs



# 👉 Extracción de las competiciones de cada año
url= "https://www.futgal.es/pnfg/NPcd/NFG_Mov_LstCompeticiones?cod_primaria=&competicion=1&rt=1"
df_competiciones = extraccion_competiciones(url)

# DataFrame vacío para acumular los resultados
codigos= df_competiciones['cod_competicion'].tolist()
df_grupos = pd.DataFrame()

for codigo in codigos:
    df, competicion = extraer_grupos_competicion(codigo)
    df_grupos = pd.concat([df_grupos, df], ignore_index=True)

df_grupos_enriquecido = df_grupos.merge(
    df_competiciones,
    on="cod_competicion",
    how="left"
)


columnas_finales = [
    "cod_primaria",  # Asumimos que esto se corresponde con cod_temporada
    "categoria",
    "cod_competicion",
    "competicion",
    "cod_grupo",
    "grupo"
]

df_grupos_ordenado = df_grupos_enriquecido[columnas_finales]


# Guardar todo en un solo CSV
file_path = './Listado_Todas_Competiciones.csv'
df_grupos_ordenado.to_csv(file_path, index=False)