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
from urllib.parse import urlparse, parse_qs


# 👉 Función para sacar todos los grupos de una determinada competicion a partir del cod_competicion
def extraer_grupos_competicion(cod_competicion):
    # Configurar Chrome para que no use el perfil por defecto
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")  # Opcional: para no abrir ventana
    options.add_argument("--user-data-dir=/tmp/selenium_profile")  # Perfil temporal nuevo

    # Iniciar el driver
    driver = webdriver.Chrome(options=options)

    # Abrir la página
    url = "https://www.futgal.es/pnfg/NPcd/NFG_Mov_LstGruposCompeticion?cod_primaria=&buscar=1&codcompeticion="+cod_competicion+"&rt=1"
    driver.get(url)

    # Esperar que cargue el div con los grupos
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Grupos Competicion"))
    )

    # Extraer HTML ya renderizado
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Obtener la competicion (está dentro de un <strong> dentro de un <a class="list-group-item active">)
    competicion_tag = soup.select_one('#Grupos\\ Competicion .list-group-item.active strong')
    competicion = competicion_tag.text.strip() if competicion_tag else "Desconocida"


    # Buscar enlaces de grupo
    grupo_div = soup.find("div", id="Grupos Competicion")
    rows = []

    if grupo_div:
        for a in grupo_div.find_all("a", class_="list-group-item"):
            strong = a.find("strong")
            href = a.get("href")
            if strong and href and href != "javascript:;":
                full_url = requests.compat.urljoin(url, href)
                match = re.search(r"cod_primaria=(\d+)&CodCompeticion=(\d+)&CodGrupo=(\d+)", full_url)
                if match:
                    cod_primaria, cod_competicion, cod_grupo = match.groups()
                    rows.append({
                        "cod_primaria": cod_primaria,
                        "cod_competicion": cod_competicion,
                        "competicion": competicion,
                        "cod_grupo": cod_grupo,
                        "grupo": strong.text.strip()
                    })

    return pd.DataFrame(rows), competicion







# 👉 A partir del link de la temporada, extraes todas las competiciones posibles
def extraccion_competiciones(url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # Actívalo si quieres

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "list-group-item"))
        )

        elementos = driver.find_elements(By.CLASS_NAME, "list-group-item")
        resultados = []
        categoria_actual = None

        for el in elementos:
            clase = el.get_attribute("class")
            texto = el.text.strip()

            if "active" in clase:
                categoria_actual = texto
            else:
                href = el.get_attribute("href")
                if not href:
                    continue

                enlace = "https://www.futgal.es/pnfg/" + href if not href.startswith("http") else href
                parsed = urlparse(enlace)
                params = parse_qs(parsed.query)
                cod_competicion = params.get("codcompeticion", [""])[0]

                resultados.append({
                    "cod_competicion": cod_competicion,
                    "categoria": categoria_actual or "SIN_CATEGORIA",
                    "nombre_competicion": texto,
                    "url": enlace
                })

        return pd.DataFrame(resultados)

    finally:
        driver.quit()



# 👉 Extraer todos los partidos de una determinada competicion
def extraccion_jornada(cod_competicion, cod_grupo, cod_temporada, jornada):
    url = ('https://www.futgal.es/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120'
           f'&CodCompeticion={cod_competicion}'
           f'&CodGrupo={cod_grupo}'
           f'&CodTemporada={cod_temporada}'
           f'&CodJornada={jornada}')

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-data-dir=/tmp/selenium_profile')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # espera a que cargue el JS

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Buscar número de jornada real
    jornada_text = soup.find("div", class_="col-sm-12", style="text-align:center")
    if jornada_text:
        match = re.search(r"Jornada\s+(\d+)", jornada_text.get_text())
        if match:
            jornada = int(match.group(1))

    # Buscar partidos
    partidos_raw = soup.find_all("table", width="100%")
    partidos = []

    for partido in partidos_raw:
        equipos = partido.find_all("div", class_=["font_widgetL", "font_widgetV"])
        enlace_acta = partido.find("a", title="Acta del partido")
        fecha_tag = partido.find_all("span", class_="horario")
        info_extra = partido.find("td", colspan="9")

        if len(equipos) == 2 :
            local = equipos[0].get_text(strip=True)
            visitante = equipos[1].get_text(strip=True)
            link_acta = "https://www.futgal.es" + enlace_acta.get("href") if enlace_acta else ""
            cod_acta_match = re.search(r"CodActa=(\d+)", link_acta)
            cod_acta = cod_acta_match.group(1) if cod_acta_match else ""

            # Fecha y hora
            fecha = fecha_tag[0].get_text(strip=True) if len(fecha_tag) > 0 else ""
            hora = fecha_tag[1].get_text(strip=True) if len(fecha_tag) > 1 else ""

            # Estadio
            estadio_tag = info_extra.find("a")
            estadio = estadio_tag.get_text(strip=True) if estadio_tag else ""

            # Extra info
            raw_text = info_extra.get_text(separator="\n")

            # Superficie
            superficie = next((line.replace("-", "").strip() for line in raw_text.split("\n") if "Hierba" in line or "Tierra" in line), "")

            # Árbitro
            arbitro = ""
            if info_extra:
                texto_limpio = info_extra.get_text(separator="\n")
                lineas = [line.strip() for line in texto_limpio.split("\n") if line.strip()]
                for i, linea in enumerate(lineas):
                    if "Árbitro:" in linea and i + 1 < len(lineas):
                        arbitro = lineas[i + 1].strip().strip('"')
                        break

            partidos.append({
                "cod_temporada": cod_temporada,
                "cod_competicion": cod_competicion,
                "cod_grupo":cod_grupo,
                "jornada": jornada,
                "fecha": fecha,
                "hora": hora,
                "estadio": estadio,
                "superficie": superficie,
                "árbitro": arbitro,
                "equipo_local": local,
                "equipo_visitante": visitante,
                "cod_acta": cod_acta,
                "link_acta": link_acta
            })

    df = pd.DataFrame(partidos)
    return df
