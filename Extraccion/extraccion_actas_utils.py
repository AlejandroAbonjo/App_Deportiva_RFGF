#####################################################################################
### - Importacion de librerias
#####################################################################################

import requests  # Libreria para realizar solicitudes HTTP a paginas web
from bs4 import BeautifulSoup  # Librería para analizar documentos HTML y extraer datos
import os  # Librería para interactuar con el sistema operativo, por ejemplo, para crear carpetas
import pandas as pd  # Librería para manipular datos y trabajar con estructuras como DataFrames
import time  # Librería para manejar tiempos y pausas
import random  # Librería para generar valores aleatorios
import re  # Librería para trabajar con expresiones regulares
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys

def extraer_jugadores(soup,cod_acta):

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Función para extraer los nombres y números de los jugadores de una tabla
    def extract_players(table, team, status):
        players = []
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                number = cols[0].text.strip()
                name = cols[1].text.strip()
                players.append((number, name, team, status))
        return players

    # Extraer los jugadores para ambos equipos
    tables = soup.find_all('table', class_='table table-striped table-hover' , width= '100%')

    # Local team
    local_titulares_table = tables[0]
    local_suplentes_table = tables[1]

    # Visitor team
    visitor_titulares_table = tables[3]
    visitor_suplentes_table = tables[4]

    local_titulares_players = extract_players(local_titulares_table, equipo_local, "Titular")
    local_suplentes_players = extract_players(local_suplentes_table, equipo_local, "Suplente")
    visitor_titulares_players = extract_players(visitor_titulares_table, equipo_visitante, "Titular")
    visitor_suplentes_players = extract_players(visitor_suplentes_table, equipo_visitante, "Suplente")

    # Crear dataframes para ambos equipos
    df_local_titulares = pd.DataFrame(local_titulares_players, columns=['numero', 'jugador', 'equipo', 'status'])
    df_local_suplentes = pd.DataFrame(local_suplentes_players, columns=['numero', 'jugador', 'equipo', 'status'])
    df_visitor_titulares = pd.DataFrame(visitor_titulares_players, columns=['numero', 'jugador', 'equipo', 'status'])
    df_visitor_suplentes = pd.DataFrame(visitor_suplentes_players, columns=['numero', 'jugador', 'equipo', 'status'])

    # Unir todos los jugadores en un solo dataframe
    df_all_players = pd.concat([df_local_titulares, df_local_suplentes, df_visitor_titulares, df_visitor_suplentes], ignore_index=True)
    df_all_players['cod_acta']=cod_acta

    return df_all_players



def extraer_cuerpo_tecnico(soup,cod_acta):
    cuerpo_tecnico = []

    # Equipos
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Buscar todas las secciones de "dashboard-stat grey"
    bloques_equipo = soup.find_all('div', class_='dashboard-stat grey')

    for bloque in bloques_equipo:
        # Intentar encontrar el nombre del equipo dentro del bloque
        nombre_equipo = None
        numero = bloque.find('div', class_='number')
        if numero:
            nombre_equipo = numero.text.strip()

        # Verificamos si coincide con uno de los dos equipos
        if nombre_equipo in [equipo_local, equipo_visitante]:
            h5s = bloque.find_all('h5', class_='font_responsive')
            for h5 in h5s:
                texto = h5.get_text(strip=True)
                if ':' in texto:
                    rol, nombre = texto.split(':', 1)
                    rol = rol.replace('ENCGDO. MATERIAL', 'Encargado Material') \
                             .replace('DEL. Equipo', 'Delegado') \
                             .replace('ENTRENADOR', 'Entrenador') \
                             .replace('AUXILIAR', 'Auxiliar') \
                             .strip()
                    nombre = nombre.strip()
                    cuerpo_tecnico.append((rol, nombre, nombre_equipo))

    df_tecnicos = pd.DataFrame(cuerpo_tecnico, columns=['rol', 'nombre', 'equipo'])
    df_tecnicos['cod_acta'] = cod_acta

    return df_tecnicos


def extraer_goles(soup, cod_acta, df_jugadores):
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    goals = []
    gl = 0  # goles local
    gv = 0  # goles visitante

    goal_rows = soup.find_all('tr')

    for row in goal_rows:
        row_str = str(row)

        # Detectar tipo de gol
        if 'lgolpp' in row_str:
            tipo = 'Propia Puerta'
        elif 'lpenalti' in row_str:
            tipo = 'Penalti'
        elif 'lgol' in row_str:
            tipo = 'Normal'
        else:
            continue

        cells = row.find_all('td')
        if len(cells) > 1:
            minuto = cells[1].find('span', class_='font-blue').text.strip("()'")
            jugador = cells[1].text.split(')')[-1].strip()

            # Determinar equipo del jugador
            equipo_jugador_df = df_jugadores[df_jugadores['jugador'].str.upper() == jugador.upper()]
            if equipo_jugador_df.empty:
                equipo_jugador = 'Desconocido'
                equipo = 'Desconocido'
            else:
                equipo_jugador = equipo_jugador_df.iloc[0]['equipo']
                equipo = (
                    equipo_visitante if (tipo == 'Propia Puerta' and equipo_jugador == equipo_local)
                    else equipo_local if (tipo == 'Propia Puerta' and equipo_jugador == equipo_visitante)
                    else equipo_jugador
                )

            # Actualizar marcador
            if equipo == equipo_local:
                gl += 1
            elif equipo == equipo_visitante:
                gv += 1

            marcador = f"{gl}-{gv}"
            goals.append([minuto, jugador, tipo, equipo, marcador])

    df_goals = pd.DataFrame(goals, columns=['minuto', 'jugador', 'tipo_gol', 'equipo', 'marcador'])
    df_goals['cod_acta'] = cod_acta

    return df_goals

def extraer_sanciones(soup, cod_acta,df_jugadores, df_cuerpo_tecnico):
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    match_details = soup.find('h5', class_='font-grey-cascade').text.strip()
    jornada = match_details.split('Jornada')[1].split()[0]

    cards = []
    card_rows = soup.find_all('tr')

    for row in card_rows:
        if 'tarj_amar.gif' in str(row) or 'tarj_roja.gif' in str(row):
            cells = row.find_all('td')
            if len(cells) > 1:
                tipo = 'Amarilla' if 'tarj_amar.gif' in str(row) else 'Roja'
                minuto = cells[1].find('span', class_='font-blue').text.strip("()'")
                jugador = cells[1].text.split(')')[-1].strip()

                # Buscar equipo
                equipo_jugador_df = df_jugadores[df_jugadores['jugador'].str.upper() == jugador.upper()]
                equipo_tecnico_df = df_cuerpo_tecnico[df_cuerpo_tecnico['nombre'].str.upper() == jugador.upper()]
                if not equipo_jugador_df.empty:
                    equipo = equipo_jugador_df.iloc[0]['equipo']
                elif not equipo_tecnico_df.empty:
                    equipo = equipo_tecnico_df.iloc[0]['equipo']
                else:
                    equipo = 'Desconocido'


                cards.append([jornada, minuto, jugador, tipo, equipo])

    df_cards = pd.DataFrame(cards, columns=['jornada', 'minuto', 'jugador', 'tipo_tarjeta', 'equipo'])
    df_cards['cod_acta'] = cod_acta
    return df_cards


def extraer_sustituciones(soup, cod_acta, df_jugadores):
    substitutions = []
    f = 2

    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()
    player_in = ''
    player_out = ''
    minuto = 0

    for table in soup.find_all("table", class_="table table-striped table-hover"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 3:
                if f % 2 == 0:
                    player_in = cells[1].text.strip()
                else:
                    player = cells[1].text.strip()
                    try:
                        partes = player.split(") ")
                        minuto = int(partes[0][1:-1].replace("'", ""))
                        player_out = partes[1].strip()
                    except:
                        minuto = 0
                        player_out = player.strip()

                    # Buscar equipo
                    equipo = 'Desconocido'
                    for nombre in [player_in, player_out]:
                        df_match = df_jugadores[df_jugadores['jugador'].str.upper() == nombre.upper()]
                        if not df_match.empty:
                            equipo = df_match.iloc[0]['equipo']
                            break

                    substitutions.append({
                        "jugador_entra": player_in,
                        "jugador_sale": player_out,
                        "minuto": minuto,
                        "equipo": equipo,
                        "cod_acta": cod_acta
                    })
                f += 1

    df_substitutions = pd.DataFrame(substitutions)

    return df_substitutions



def procesar_acta(cod_acta):

    # Configuración del navegador (modo headless para no abrir ventana)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")

    # Iniciar el driver
    driver = webdriver.Chrome(options=options)

    url = "https://www.futgal.es/pnfg/NPcd/NFG_CmpPartido?cod_primaria=1000120&CodActa="+cod_acta+"&cod_acta="+cod_acta
    driver.get(url)

    print(url)

    # Esperar a que cargue la sección de goles
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fa-futbol-o"))
    )

    # Extraer HTML ya renderizado
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Rutas de salida
    rutas = {
        "jugadores": "./jugadores.csv",
        "cuerpo_tecnico": "./cuerpo_tecnico.csv",
        "goles": "./goles.csv",
        "sanciones": "./sanciones.csv",
        "sustituciones": "./sustituciones.csv"
    }

    # Extraer los datos
    df_jugadores = extraer_jugadores(soup,cod_acta)
    df_cuerpo_tecnico = extraer_cuerpo_tecnico(soup,cod_acta)
    df_goles = extraer_goles(soup, cod_acta, df_jugadores)
    df_sanciones = extraer_sanciones(soup, cod_acta, df_jugadores, df_cuerpo_tecnico)
    df_sustituciones=extraer_sustituciones(soup,cod_acta, df_jugadores)

    # Asociar cada dataframe a su clave
    nuevos_dfs = {
        "jugadores": df_jugadores,
        "cuerpo_tecnico": df_cuerpo_tecnico,
        "goles": df_goles,
        "sanciones": df_sanciones,
        "sustituciones": df_sustituciones
    }

    for clave, df_nuevo in nuevos_dfs.items():
            ruta = rutas[clave]

            # Si el fichero no existe, crear directamente
            if not os.path.exists(ruta):
                df_nuevo.to_csv(ruta, index=False)
                continue

            # Si existe, leerlo y comprobar cod_acta
            try:
                df_existente = pd.read_csv(ruta)
            except pd.errors.EmptyDataError:
                df_existente = pd.DataFrame(columns=df_nuevo.columns)

            if cod_acta in df_existente['cod_acta'].astype(str).values:
                continue

            # Añadir y guardar
            df_comb = pd.concat([df_existente, df_nuevo], ignore_index=True).drop_duplicates()
            df_comb.to_csv(ruta, index=False)