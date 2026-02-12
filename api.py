import os
import json
import pickle
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

print("Loading model...")
with open('data/pricing_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('data/encoders.json', 'r') as f:
    encoders = json.load(f)

with open('data/dataset_stats.json', 'r') as f:
    dataset_stats = json.load(f)

print("Model ready.")

# Estado string → número (training used Spanish labels)
ESTADO_MAP = {
    'Unworn': 3, 'New': 3,
    'Very good': 2,
    'Good': 1, 'Incomplete': 1, 'Unknown': 1,
    'Fair': 0, 'Poor': 0,
}

GOLD_MATERIALS = {'Yellow gold', 'White gold', 'Red gold', 'Rose gold', 'Platinum'}
BICOLOR_MATERIALS = {'Gold/Steel'}


def material_to_num(material):
    if material in GOLD_MATERIALS:
        return 1
    elif material in BICOLOR_MATERIALS:
        return 2
    return 0


def build_features(modelo, año, estado, material, caja, papeles):
    estado_num = ESTADO_MAP.get(estado, 1)
    material_num = material_to_num(material)
    es_hulk = 1 if '116610lv' in modelo.lower() or 'hulk' in modelo.lower() else 0
    es_kermit = 1 if '16610lv' in modelo.lower() or 'kermit' in modelo.lower() else 0
    return [[año, caja, papeles, 0, 0, estado_num, material_num, es_hulk, es_kermit]]


def predict_price(modelo, año, estado, material, caja, papeles):
    return float(model.predict(build_features(modelo, año, estado, material, caja, papeles))[0])


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/api/models', methods=['GET'])
def get_models():
    models = sorted(encoders['model'].values())
    return jsonify({'models': models})


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        modelo = data['modelo']
        año = int(data['año'])
        estado = data['estado']
        material = data['material']
        caja = 1 if data.get('caja', False) else 0
        papeles = 1 if data.get('papeles', False) else 0

        precio = predict_price(modelo, año, estado, material, caja, papeles)
        precio_base = predict_price(modelo, año, estado, material, 0, 0)

        impacto_caja = precio - predict_price(modelo, año, estado, material, 0, papeles) if caja else 0
        impacto_papeles = precio - predict_price(modelo, año, estado, material, caja, 0) if papeles else 0

        años = [a for a in [año - 5, año, año + 5] if 1950 < a < 2027]
        precios_por_año = [
            {'año': a, 'precio': round(predict_price(modelo, a, estado, material, caja, papeles), 0)}
            for a in años
        ]

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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
