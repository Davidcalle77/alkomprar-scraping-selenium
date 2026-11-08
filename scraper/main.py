import json
import time
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.extractor import extraer_datos_alkomprar

URL = "https://www.alkomprar.com/celular-samsung-galaxy-a27-256gb-5g-negro/p/8806099361082"
SALIDA = "docs/datos.json"


def crear_driver():
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opciones)


def main():
    driver = crear_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        time.sleep(5)  # deja cargar los precios dinámicos
        datos = extraer_datos_alkomprar(driver, URL)
    finally:
        driver.quit()

    datos["fecha_consulta"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(json.dumps(datos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
