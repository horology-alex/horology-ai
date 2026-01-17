import asyncio
import json
from playwright.async_api import async_playwright
from src.processor import process_listing

async def scrape_chrono24(max_listings=5):
    """Scrapea anuncios de Submariner en Chrono24"""
    
    async with async_playwright() as p:
        print("🌐 Abriendo navegador...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000  # Más lento, más humano
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Timeout más largo
        page.set_default_timeout(60000)
        
        url = "https://www.chrono24.es/rolex/submariner-date--mod981.htm"
        print(f"📍 Navegando a Chrono24 (puede tardar 30-60s)...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            print("✓ Página cargada")
        except Exception as e:
            print(f"❌ Error cargando página: {e}")
            await browser.close()
            return []
        
        listings = []
        
        print(f"🔍 Buscando anuncios...\n")
        
        # Scroll para cargar contenido
        await page.evaluate("window.scrollTo(0, 1000)")
        await asyncio.sleep(2)
        
        # Extrae links
        links = await page.query_selector_all('a[href*="submariner"]')
        print(f"Encontrados {len(links)} links")
        
        urls_visited = set()
        
        for i, link in enumerate(links[:max_listings * 3], 1):  # Intenta más por si fallan
            try:
                href = await link.get_attribute('href')
                if not href or 'id' not in href or href in urls_visited:
                    continue
                
                urls_visited.add(href)
                
                full_url = f"https://www.chrono24.es{href}" if href.startswith('/') else href
                
                print(f"[{len(listings)+1}/{max_listings}] Extrayendo: {href[:50]}...")
                
                await page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                
                # Extrae texto
                content = await page.content()
                
                # Texto simplificado
                title = await page.query_selector('h1')
                title_text = await title.inner_text() if title else ""
                
                body = await page.query_selector('body')
                body_text = await body.inner_text() if body else ""
                
                listing_text = f"{title_text}\n{body_text[:2000]}"
                
                print(f"✓ Extraído ({len(listing_text)} caracteres)")
                listings.append(listing_text)
                
                if len(listings) >= max_listings:
                    break
                
                # Vuelve atrás
                await page.go_back(wait_until="domcontentloaded")
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"⚠️  Error en anuncio: {str(e)[:50]}")
                continue
        
        await browser.close()
        return listings

async def main():
    raw_listings = await scrape_chrono24(max_listings=3)  # Solo 3 para probar
    
    if not raw_listings:
        print("❌ No se pudieron extraer anuncios")
        return
    
    print(f"\n✓ {len(raw_listings)} anuncios extraídos")
    print("\n🤖 Procesando con IA...\n")
    
    results = []
    for i, listing in enumerate(raw_listings, 1):
        print(f"[{i}/{len(raw_listings)}] Procesando con IA...")
        result = process_listing(listing)
        if result:
            results.append(result)
            ref = result['identidad']['referencia']
            precio = result['precio']['precio_anuncio']
            print(f"✓ {ref} - {precio}€\n")
    
    with open('data/scraped_watches.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ {len(results)} relojes guardados en data/scraped_watches.json")

if __name__ == "__main__":
    asyncio.run(main())
