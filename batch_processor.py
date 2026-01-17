import json
import csv
from src.processor import process_listing

# 13 anuncios variados de Submariner Date
listings = [
    """Rolex Submariner Date 116610LV Hulk, Año: 2018, Como nuevo, señales leves, con caja sin papeles, 15.500€, España""",
    """Rolex Submariner Date 16800, Año: 1983, Usado bueno, arañazos, con caja sin papeles, revisado dic 2025, 8.450€, Italia""",
    """Rolex Submariner Date 16610, Año: 1992, Usado bueno, sin caja sin papeles, never polished, 7.450€, Italia""",
    """Rolex Submariner Date 16618 oro amarillo azul, Año: 1998, Muy bueno, con caja sin papeles, revisado dic 2025, 24.500€, Barcelona""",
    """Rolex Submariner Date 116610LN, Año: 2011, Muy bueno, sin caja con papeles, 11.900€, Italia""",
    """Rolex Submariner Date Kermit 16610LV, Año: 2007, Como nuevo, full set caja y papeles, 66.032€, Miami""",
    """Rolex Submariner Date 116610LV Hulk, Año: 2019, Nuevo unworn, full set, 20.990€, Alemania""",
    """Rolex Submariner Date 116610LV Hulk, Año: 2020, Muy bueno, polished, con caja sin papeles, 17.604€, USA""",
    """Rolex Submariner Date 116610LN, Año: 2013, Muy bueno, revisado abril 2025, full set, 11.790€, Alemania""",
    """Rolex Submariner Date 16800, Año: 1986, Bueno, patina, con caja y papeles, 9.690€, Alemania""",
    """Rolex Submariner Date 16613 bicolor, Año: 1995, Usado bueno, solo caja, 10.200€, España""",
    """Rolex Submariner Date Kermit 16610LV, Año: 2005, Bueno, sin caja sin papeles, 11.500€, Italia""",
    """Rolex Submariner Date 116610LN, Año: 2015, Muy bueno like new, full set, 10.995€, Holanda"""
]

print(f"🔄 Procesando {len(listings)} anuncios con IA local...\n")

results = []
for i, listing in enumerate(listings, 1):
    print(f"[{i}/{len(listings)}] Procesando...")
    result = process_listing(listing)
    if result:
        results.append(result)
        # Manejo seguro de campos opcionales
        ref = result.get('identidad', {}).get('referencia', 'N/A')
        precio = result.get('precio', {}).get('precio_anuncio', 0)
        año = result.get('identidad', {}).get('año', 'N/A')
        print(f"✓ {ref} ({año}) - {precio}€\n")
    else:
        print(f"✗ Error\n")

# Guardar en CSV
if results:
    with open('data/watches_dataset.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['marca', 'modelo', 'ref', 'apodo', 'año', 'material', 
                      'caja', 'papeles', 'estado', 'rayaduras', 'pulido', 'precio']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                'marca': r.get('identidad', {}).get('marca', ''),
                'modelo': r.get('identidad', {}).get('modelo', ''),
                'ref': r.get('identidad', {}).get('referencia', ''),
                'apodo': r.get('identidad', {}).get('apodo', ''),
                'año': r.get('identidad', {}).get('año', ''),
                'material': r.get('identidad', {}).get('material', ''),
                'caja': r.get('estado', {}).get('tiene_caja', ''),
                'papeles': r.get('estado', {}).get('tiene_papeles', ''),
                'estado': r.get('estado', {}).get('estado_global', ''),
                'rayaduras': r.get('estado', {}).get('tiene_rayaduras_visibles', ''),
                'pulido': r.get('estado', {}).get('pulido', ''),
                'precio': r.get('precio', {}).get('precio_anuncio', 0)
            })
    
    with open('data/watches_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ {len(results)} relojes guardados:")
    print(f"   - data/watches_dataset.csv")
    print(f"   - data/watches_dataset.json")
    
    precios = [r.get('precio', {}).get('precio_anuncio', 0) for r in results if r.get('precio', {}).get('precio_anuncio')]
    if precios:
        print(f"\n📊 Estadísticas:")
        print(f"   Precio medio: {sum(precios)/len(precios):,.0f}€")
        print(f"   Precio min: {min(precios):,.0f}€")
        print(f"   Precio max: {max(precios):,.0f}€")
