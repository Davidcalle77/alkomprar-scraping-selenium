import json
import re
from selenium.webdriver.common.by import By
from scraper.precios import a_numero


def extraer_datos_alkomprar(driver, url_producto):
    datos = {
        "nombre": None,
        "precio_actual": None,
        "precio_anterior": None,
        "calificacion": None,
        "opiniones": None,
        "url": url_producto,
    }

    # Nombre, calificación y opiniones (datos estructurados JSON-LD)
    for script in driver.find_elements(
        By.CSS_SELECTOR, "script[type='application/ld+json']"
    ):
        try:
            info = json.loads(script.get_attribute("innerHTML"))
        except Exception:
            continue
        for item in (info if isinstance(info, list) else [info]):
            if isinstance(item, dict) and item.get("@type") == "Product":
                datos["nombre"] = item.get("name")
                rating = item.get("aggregateRating", {})
                datos["calificacion"] = rating.get("ratingValue")
                datos["opiniones"] = rating.get("reviewCount")

    if not datos["nombre"]:
        datos["nombre"] = driver.find_element(By.TAG_NAME, "h1").text.strip()

    # Precios: se buscan por cómo se ven (el tachado es el anterior)
    js = r"""
    const out = [];
    document.querySelectorAll('body *').forEach(el => {
      if (el.children.length > 0) return;
      const t = (el.textContent || '').trim();
      if (!/^\$\s?\d{1,3}(\.\d{3})+(\s*hoy)?$/i.test(t)) return;
      let tachado = false, p = el;
      while (p && p !== document.body) {
        if (['DEL','S','STRIKE'].includes(p.tagName) ||
            getComputedStyle(p).textDecorationLine.includes('line-through')) tachado = true;
        p = p.parentElement;
      }
      out.push({texto: t, tachado: tachado,
                tam: parseFloat(getComputedStyle(el).fontSize),
                visible: el.offsetParent !== null});
    });
    return out;
    """
    precios = [p for p in driver.execute_script(js) if p["visible"]]
    print("Precios encontrados:", precios)

    tachados = [p for p in precios if p["tachado"]]
    normales = [p for p in precios if not p["tachado"]]

    if tachados:
        datos["precio_anterior"] = a_numero(tachados[0]["texto"])

    # Porcentaje de descuento que muestra la página (ej. "-27%")
    texto_pagina = driver.find_element(By.TAG_NAME, "body").text
    m = re.search(r"-\s?(\d{1,2})\s?%", texto_pagina)
    pct_pagina = int(m.group(1)) if m else None
    print("Descuento que muestra la página:", pct_pagina)

    valores = sorted({a_numero(p["texto"]) for p in normales if a_numero(p["texto"])})
    anterior = datos["precio_anterior"]

    if anterior:
        valores = [v for v in valores if v < anterior]

    if valores and anterior and pct_pagina:
        # Corregido: se eliminó el guion extra y se ajustó '* 100 - pct_pagina'
        datos["precio_actual"] = min(
            valores, key=lambda v: abs((anterior - v) / anterior * 100 - pct_pagina)
        )
    elif valores:
        datos["precio_actual"] = max(valores)

    return datos
