# =============================================================================
# scraper.py — Scraper de relojes desde Chrono24
# =============================================================================
# Abre un navegador real (invisible), navega por los listados de Chrono24,
# extrae los datos de cada reloj y los guarda en data/watches.db (SQLite).
#
# USO:
#   pip install -r requirements_scraper.txt
#   playwright install chromium
#   python scraper.py
#
# CONFIGURACIÓN:
#   Cambia TARGET_RECORDS y MARCA_URL abajo para scrapear más registros
#   o marcas distintas.
# =============================================================================

import asyncio
import sqlite3
import re
import os
from datetime import datetime
from playwright.async_api import async_playwright

# --- Configuración ---
TARGET_RECORDS = 100          # Cuántos relojes queremos recoger
DELAY_ENTRE_PAGINAS = 3       # Segundos entre páginas (no ser agresivo)
DELAY_ENTRE_LISTADOS = 1.5    # Segundos entre listados individuales
DB_PATH = 'data/watches.db'

# URL base de Chrono24 — cambia 'rolex' por otra marca si quieres
MARCA_URL = 'https://www.chrono24.com/rolex/index.htm'


# =============================================================================
# BASE DE DATOS
# =============================================================================

def init_db():
    """Crea la base de datos y la tabla si no existen todavía."""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS relojes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            marca            TEXT,
            modelo           TEXT,
            referencia       TEXT,
            año              INTEGER,
            precio           REAL,
            moneda           TEXT,
            estado           TEXT,
            material         TEXT,
            diametro_mm      INTEGER,
            caja             INTEGER,  -- 1 = tiene caja, 0 = no, NULL = desconocido
            papeles          INTEGER,  -- 1 = tiene papeles, 0 = no, NULL = desconocido
            ubicacion        TEXT,
            tipo_vendedor    TEXT,     -- 'privado' o 'comerciante'
            url              TEXT UNIQUE,
            fecha_scraping   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn


def guardar_reloj(conn, datos):
    """Inserta un reloj en la base de datos. Ignora duplicados (misma URL)."""
    try:
        conn.execute('''
            INSERT OR IGNORE INTO relojes
            (marca, modelo, referencia, año, precio, moneda, estado, material,
             diametro_mm, caja, papeles, ubicacion, tipo_vendedor, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos.get('marca'),
            datos.get('modelo'),
            datos.get('referencia'),
            datos.get('año'),
            datos.get('precio'),
            datos.get('moneda'),
            datos.get('estado'),
            datos.get('material'),
            datos.get('diametro_mm'),
            datos.get('caja'),
            datos.get('papeles'),
            datos.get('ubicacion'),
            datos.get('tipo_vendedor'),
            datos.get('url'),
        ))
        conn.commit()
        return conn.execute('SELECT changes()').fetchone()[0] > 0
    except Exception as e:
        print(f"  Error guardando en BD: {e}")
        return False


# =============================================================================
# PARSEO DE DATOS
# =============================================================================

def parsear_precio(texto):
    """Extrae el número de un texto tipo '12.500 €' o 'EUR 12,500'."""
    if not texto:
        return None, None
    moneda = None
    if '€' in texto or 'EUR' in texto:
        moneda = 'EUR'
    elif '$' in texto or 'USD' in texto:
        moneda = 'USD'
    elif '£' in texto or 'GBP' in texto:
        moneda = 'GBP'
    numeros = re.sub(r'[^\d]', '', texto)
    return float(numeros) if numeros else None, moneda


def parsear_año(texto):
    """Extrae el año de un texto como 'Año: 2019' o '2019'."""
    if not texto:
        return None
    match = re.search(r'(19|20)\d{2}', texto)
    return int(match.group()) if match else None


def parsear_caja_papeles(texto):
    """
    Detecta si tiene caja y papeles a partir de un texto descriptivo.
    Devuelve (caja, papeles) como 0/1/None.
    """
    if not texto:
        return None, None
    t = texto.lower()
    caja = None
    papeles = None
    if 'original box' in t or 'con caja' in t:
        caja = 1
    elif 'no original box' in t or 'sin caja' in t:
        caja = 0
    if 'original papers' in t or 'con papeles' in t or 'with papers' in t:
        papeles = 1
    elif 'no original papers' in t or 'sin papeles' in t or 'no papers' in t:
        papeles = 0
    return caja, papeles


# =============================================================================
# SCRAPING
# =============================================================================

async def extraer_datos_listado(page, url):
    """
    Abre la página de un anuncio individual y extrae todos los campos.
    Devuelve un diccionario con los datos del reloj.
    """
    datos = {'url': url}
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(1)

        # --- Título / Modelo ---
        for selector in ['h1.wt-article-title', 'h1[class*="title"]', 'h1']:
            el = await page.query_selector(selector)
            if el:
                datos['modelo'] = (await el.inner_text()).strip()
                break

        # --- Precio ---
        for selector in ['.js-price', '.price-value', '[class*="price"]']:
            el = await page.query_selector(selector)
            if el:
                texto = (await el.inner_text()).strip()
                datos['precio'], datos['moneda'] = parsear_precio(texto)
                if datos['precio']:
                    break

        # --- Detalles técnicos (tabla de specs) ---
        # Chrono24 muestra los detalles en filas clave-valor
        filas = await page.query_selector_all('.js-attribute-row, [class*="attribute-row"], .details-list li')
        for fila in filas:
            texto = (await fila.inner_text()).lower().strip()

            if 'year' in texto or 'año' in texto:
                datos['año'] = parsear_año(texto)

            elif 'condition' in texto or 'estado' in texto:
                partes = texto.split('\n')
                datos['estado'] = partes[-1].strip() if len(partes) > 1 else texto

            elif 'case material' in texto or 'material' in texto:
                partes = texto.split('\n')
                datos['material'] = partes[-1].strip() if len(partes) > 1 else texto

            elif 'case size' in texto or 'diameter' in texto or 'diámetro' in texto:
                numeros = re.search(r'\d+', texto)
                if numeros:
                    datos['diametro_mm'] = int(numeros.group())

            elif 'reference' in texto or 'referencia' in texto or 'ref.' in texto:
                partes = texto.split('\n')
                datos['referencia'] = partes[-1].strip() if len(partes) > 1 else texto

            elif 'scope of delivery' in texto or 'includes' in texto or 'entrega' in texto:
                caja, papeles = parsear_caja_papeles(texto)
                datos['caja'] = caja
                datos['papeles'] = papeles

        # --- Ubicación y tipo de vendedor ---
        for selector in ['.seller-location', '[class*="location"]', '.location']:
            el = await page.query_selector(selector)
            if el:
                datos['ubicacion'] = (await el.inner_text()).strip()
                break

        for selector in ['.seller-badge', '[class*="dealer"]', '[class*="private"]']:
            el = await page.query_selector(selector)
            if el:
                texto = (await el.inner_text()).lower().strip()
                datos['tipo_vendedor'] = 'comerciante' if 'dealer' in texto else 'privado'
                break

        # Marca por defecto (se puede hacer dinámico si se scrapean otras marcas)
        datos['marca'] = 'Rolex'

    except Exception as e:
        print(f"  Error extrayendo {url}: {e}")

    return datos


async def obtener_urls_listados(page, pagina_num):
    """
    Navega a una página de resultados y devuelve las URLs de los anuncios.
    """
    url = f'{MARCA_URL}?pageSize=30&p={pagina_num}'
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(DELAY_ENTRE_PAGINAS)

        # Chrono24 usa enlaces en las tarjetas de listado
        # El selector puede variar — ajustar si no funciona
        enlaces = await page.query_selector_all(
            'a.js-article-item, a[class*="article-item"], .article-item a.js-article-link'
        )

        urls = []
        for enlace in enlaces:
            href = await enlace.get_attribute('href')
            if href and '/watches/' in href:
                if href.startswith('/'):
                    href = 'https://www.chrono24.com' + href
                if href not in urls:
                    urls.append(href)

        return urls

    except Exception as e:
        print(f"  Error obteniendo página {pagina_num}: {e}")
        return []


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

async def main():
    print("=" * 60)
    print("HOROLOGY.AI — Scraper de Chrono24")
    print("=" * 60)

    conn = init_db()
    total_guardados = 0
    pagina = 1

    async with async_playwright() as p:
        print("\nAbriendo navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='en-US',
        )
        page_listado = await context.new_page()
        page_detalle = await context.new_page()

        print(f"Objetivo: {TARGET_RECORDS} relojes\n")

        while total_guardados < TARGET_RECORDS:
            print(f"Página {pagina} de resultados...")
            urls = await obtener_urls_listados(page_listado, pagina)

            if not urls:
                print("No se encontraron más anuncios. Fin.")
                break

            print(f"  {len(urls)} anuncios encontrados en esta página")

            for i, url in enumerate(urls):
                if total_guardados >= TARGET_RECORDS:
                    break

                print(f"  [{total_guardados + 1}/{TARGET_RECORDS}] Extrayendo: {url[:60]}...")
                datos = await extraer_datos_listado(page_detalle, url)

                if datos.get('precio') and datos.get('modelo'):
                    guardado = guardar_reloj(conn, datos)
                    if guardado:
                        total_guardados += 1
                        print(f"    ✓ {datos.get('modelo', '?')[:40]} — {datos.get('precio', '?')} {datos.get('moneda', '')}")
                    else:
                        print(f"    · Duplicado, ignorado")
                else:
                    print(f"    ✗ Datos insuficientes, ignorado")

                await asyncio.sleep(DELAY_ENTRE_LISTADOS)

            pagina += 1

        await browser.close()

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"Scraping completado: {total_guardados} relojes guardados")
    print(f"Base de datos: {DB_PATH}")
    print(f"{'=' * 60}")

    # Muestra resumen de lo guardado
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute('SELECT COUNT(*) FROM relojes').fetchone()[0]
    precio_medio = conn.execute('SELECT AVG(precio) FROM relojes WHERE precio IS NOT NULL').fetchone()[0]
    print(f"\nTotal en BD: {total} relojes")
    if precio_medio:
        print(f"Precio medio: {precio_medio:,.0f} {''}")
    conn.close()


if __name__ == '__main__':
    asyncio.run(main())
