# =============================================================================
# api.py — Servidor principal de Horology.AI
# =============================================================================
# Este archivo es el "cerebro" de la aplicación. Hace dos cosas:
#   1. Sirve la página web (index.html) cuando alguien abre la URL de la app
#   2. Responde a las peticiones del frontend con predicciones de precio
#
# Cuando arranca, carga tres archivos de la carpeta data/:
#   - pricing_model.pkl  → el modelo de Machine Learning ya entrenado
#   - encoders.json      → lista de todos los modelos/materiales/estados disponibles
#   - dataset_stats.json → estadísticas globales del dataset (81.725 relojes)
#
# Endpoints disponibles:
#   GET  /              → devuelve la página web (index.html)
#   GET  /api/models    → devuelve la lista de modelos Rolex disponibles
#   POST /api/predict   → recibe los datos de un reloj y devuelve el precio estimado
# =============================================================================

import os
import json
import pickle
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# --- Carga de datos al arrancar el servidor ---
print("Loading model...")
with open('data/pricing_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('data/encoders.json', 'r') as f:
    encoders = json.load(f)

with open('data/dataset_stats.json', 'r') as f:
    dataset_stats = json.load(f)

print("Model ready.")

# --- Conversión de estado (texto) a número ---
# El modelo fue entrenado con números, no con palabras.
# Esta tabla convierte el estado que manda el frontend al número correspondiente.
# Mayor número = mejor estado del reloj.
ESTADO_MAP = {
    'Unworn': 3, 'New': 3,       # Nuevo / sin estrenar
    'Very good': 2,               # Muy bueno
    'Good': 1, 'Incomplete': 1, 'Unknown': 1,  # Bueno
    'Fair': 0, 'Poor': 0,        # Regular / malo
}

# Materiales que se consideran "oro puro"
GOLD_MATERIALS = {'Yellow gold', 'White gold', 'Red gold', 'Rose gold', 'Platinum'}
# Materiales que son combinación acero+oro
BICOLOR_MATERIALS = {'Gold/Steel'}


def material_to_num(material):
    """Convierte el material a un número: 0=acero, 1=oro, 2=bicolor."""
    if material in GOLD_MATERIALS:
        return 1
    elif material in BICOLOR_MATERIALS:
        return 2
    return 0  # acero u otros


def build_features(modelo, año, estado, material, caja, papeles):
    """
    Construye el vector de 9 características que necesita el modelo ML.
    El orden importa — tiene que coincidir exactamente con cómo fue entrenado.
    [año, caja, papeles, rayaduras, pulido, estado_num, material_num, es_hulk, es_kermit]
    """
    estado_num = ESTADO_MAP.get(estado, 1)
    material_num = material_to_num(material)
    # Detecta variantes especiales por nombre o referencia
    es_hulk = 1 if '116610lv' in modelo.lower() or 'hulk' in modelo.lower() else 0
    es_kermit = 1 if '16610lv' in modelo.lower() or 'kermit' in modelo.lower() else 0
    # rayaduras y pulido se fijan a 0 (no los recoge el frontend)
    return [[año, caja, papeles, 0, 0, estado_num, material_num, es_hulk, es_kermit]]


def predict_price(modelo, año, estado, material, caja, papeles):
    """Llama al modelo y devuelve el precio predicho como float."""
    return float(model.predict(build_features(modelo, año, estado, material, caja, papeles))[0])


# --- Rutas web ---

@app.route('/')
def home():
    """Sirve la página principal (index.html)."""
    return send_from_directory('.', 'index.html')


@app.route('/api/models', methods=['GET'])
def get_models():
    """Devuelve la lista ordenada de modelos Rolex para poblar el desplegable."""
    models = sorted(encoders['model'].values())
    return jsonify({'models': models})


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Recibe los datos de un reloj en formato JSON y devuelve:
      - precio_estimado: precio predicho con la configuración actual
      - precio_base:     precio sin caja ni papeles (referencia)
      - rango:           min/max estimado del mercado (±18%)
      - analisis_impacto: cuánto suman la caja y los papeles al precio
      - graficos:        datos para los gráficos de año y estado
      - stats:           estadísticas globales del dataset
    """
    try:
        data = request.json
        modelo = data['modelo']
        año = int(data['año'])
        estado = data['estado']
        material = data['material']
        caja = 1 if data.get('caja', False) else 0
        papeles = 1 if data.get('papeles', False) else 0

        # Precio principal
        precio = predict_price(modelo, año, estado, material, caja, papeles)
        # Precio sin accesorios (referencia base)
        precio_base = predict_price(modelo, año, estado, material, 0, 0)

        # Cuánto aporta cada accesorio al precio
        impacto_caja = precio - predict_price(modelo, año, estado, material, 0, papeles) if caja else 0
        impacto_papeles = precio - predict_price(modelo, año, estado, material, caja, 0) if papeles else 0

        # Datos para el gráfico de evolución por año (año-5, año actual, año+5)
        años = [a for a in [año - 5, año, año + 5] if 1950 < a < 2027]
        precios_por_año = [
            {'año': a, 'precio': round(predict_price(modelo, a, estado, material, caja, papeles), 0)}
            for a in años
        ]

        # Datos para el gráfico de comparación por estado
        precios_por_estado = [
            {'estado': est, 'precio': round(predict_price(modelo, año, est, material, caja, papeles), 0)}
            for est in ['Unworn', 'Very good', 'Good', 'Fair']
        ]

        return jsonify({
            'success': True,
            'precio_estimado': round(precio, 0),
            'precio_base': round(precio_base, 0),
            'rango': {
                'min': round(precio * 0.82, 0),
                'max': round(precio * 1.18, 0),
            },
            'analisis_impacto': {
                'caja': round(impacto_caja, 0),
                'papeles': round(impacto_papeles, 0),
            },
            'graficos': {
                'por_año': precios_por_año,
                'por_estado': precios_por_estado,
            },
            'stats': {
                'relojes_analizados': dataset_stats['total_watches'],
                'precio_promedio_modelo': round(dataset_stats['avg_price'], 0),
            },
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # En local usa el puerto 5001; en producción (Render/Railway) usa el PORT del entorno
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
