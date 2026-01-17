import pickle
import pandas as pd

# Cargar modelo
with open('data/pricing_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predecir_precio(año, tiene_caja, tiene_papeles, estado, material='acero', es_hulk=False):
    """Predice el precio de un Submariner"""
    
    # Estado a número
    estado_map = {'como nuevo': 3, 'muy bueno': 2, 'bueno': 1, 'aceptable': 0}
    estado_num = estado_map.get(estado.lower(), 1)
    
    # Material a número
    if 'oro' in material.lower() and 'bicolor' not in material.lower():
        material_num = 1
    elif 'bicolor' in material.lower():
        material_num = 2
    else:
        material_num = 0
    
    # Crear features
    features = pd.DataFrame([{
        'año': año,
        'caja': 1 if tiene_caja else 0,
        'papeles': 1 if tiene_papeles else 0,
        'rayaduras': 0,
        'pulido': 0,
        'estado_num': estado_num,
        'material_num': material_num,
        'es_hulk': 1 if es_hulk else 0,
        'es_kermit': 0
    }])
    
    precio = model.predict(features)[0]
    return precio

# EJEMPLOS DE USO
print("🔮 PREDICTOR DE PRECIOS - HOROLOGY.IA\n")

ejemplos = [
    {"año": 2020, "tiene_caja": True, "tiene_papeles": True, "estado": "como nuevo", "es_hulk": True},
    {"año": 2018, "tiene_caja": True, "tiene_papeles": False, "estado": "muy bueno", "es_hulk": True},
    {"año": 1990, "tiene_caja": False, "tiene_papeles": False, "estado": "bueno", "material": "acero"},
    {"año": 2000, "tiene_caja": True, "tiene_papeles": True, "estado": "muy bueno", "material": "oro"}
]

for i, ej in enumerate(ejemplos, 1):
    precio = predecir_precio(**ej)
    print(f"Ejemplo {i}:")
    print(f"  Año: {ej['año']}, Caja: {ej['tiene_caja']}, Papeles: {ej['tiene_papeles']}")
    print(f"  Estado: {ej['estado']}, Material: {ej.get('material', 'acero')}")
    print(f"  → Precio estimado: {precio:,.0f}€\n")
