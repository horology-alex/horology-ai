from flask import Flask, request, jsonify, send_from_directory
import pickle
import json
import pandas as pd

app = Flask(__name__)

# Cargar modelo y encoders
print("🚀 Cargando modelo...")
with open('data/pricing_model_full.pkl', 'rb') as f:
    model = pickle.load(f)

with open('data/encoders.json', 'r') as f:
    encoders = json.load(f)

df = pd.read_csv('data/rolex_dataset.csv')

print("✅ Modelo cargado y listo (6 features)")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    models = list(set(encoders['model'].values()))
    models.sort()
    return jsonify({'models': models})

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        # Datos del reloj
        modelo = data['modelo']
        año = int(data['año'])
        estado = data['estado']
        material = data['material']
        caja = 1 if data.get('caja', False) else 0
        papeles = 1 if data.get('papeles', False) else 0

        # Codificar categorías
        modelo_encoded = list(encoders['model'].keys())[list(encoders['model'].values()).index(modelo)]
        estado_encoded = list(encoders['condition'].keys())[list(encoders['condition'].values()).index(estado)]
        material_encoded = list(encoders['material'].keys())[list(encoders['material'].values()).index(material)]

        # Construir vector con 6 features
        X = [[
            int(modelo_encoded),
            año,
            int(estado_encoded),
            int(material_encoded),
            caja,
            papeles
        ]]

        # Fair value con la configuración actual
        precio_predicho = float(model.predict(X)[0])

        # Precio base: mismo reloj pero sin caja ni papeles
        X_base = [[
            int(modelo_encoded),
            año,
            int(estado_encoded),
            int(material_encoded),
            0,
            0
        ]]
        precio_base = float(model.predict(X_base)[0])

        # Impacto de caja
        X_sin_caja = [[
            int(modelo_encoded),
            año,
            int(estado_encoded),
            int(material_encoded),
            0,
            papeles
        ]]
        precio_sin_caja = float(model.predict(X_sin_caja)[0])
        impacto_caja = precio_predicho - precio_sin_caja if caja else 0

        # Impacto de papeles
        X_sin_papeles = [[
            int(modelo_encoded),
            año,
            int(estado_encoded),
            int(material_encoded),
            caja,
            0
        ]]
        precio_sin_papeles = float(model.predict(X_sin_papeles)[0])
        impacto_papeles = precio_predicho - precio_sin_papeles if papeles else 0

        # Comparación por año
        años_comparar = [año - 5, año, año + 5]
        precios_por_año = []
        for a in años_comparar:
            if 1950 < a < 2027:
                X_año = [[
                    int(modelo_encoded),
                    a,
                    int(estado_encoded),
                    int(material_encoded),
                    caja,
                    papeles
                ]]
                p = float(model.predict(X_año)[0])
                precios_por_año.append({'año': a, 'precio': round(p, 0)})

        # Comparación por estado
        estados_disponibles = ['Unworn', 'Very good', 'Good', 'Fair']
        precios_por_estado = []
        for est in estados_disponibles:
            if est in encoders['condition'].values():
                est_encoded = list(encoders['condition'].keys())[list(encoders['condition'].values()).index(est)]
                X_estado = [[
                    int(modelo_encoded),
                    año,
                    int(est_encoded),
                    int(material_encoded),
                    caja,
                    papeles
                ]]
                p = float(model.predict(X_estado)[0])
                precios_por_estado.append({'estado': est, 'precio': round(p, 0)})

        # Estadísticas del modelo
        df_modelo = df[df['model'] == modelo]
        stats_modelo = {
            'count': len(df_modelo),
            'avg': float(df_modelo['price'].mean()) if len(df_modelo) > 0 else 0,
            'min': float(df_modelo['price'].min()) if len(df_modelo) > 0 else 0,
            'max': float(df_modelo['price'].max()) if len(df_modelo) > 0 else 0
        }

        resultado = {
            'success': True,
            'precio_estimado': round(precio_predicho, 0),
            'precio_base': round(precio_base, 0),
            'rango': {
                'min': round(stats_modelo['min'], 0),
                'max': round(stats_modelo['max'], 0)
            },
            'analisis_impacto': {
                'caja': round(impacto_caja, 0),
                'papeles': round(impacto_papeles, 0)
            },
            'graficos': {
                'por_año': precios_por_año,
                'por_estado': precios_por_estado
            },
            'stats': {
                'relojes_analizados': stats_modelo['count'],
                'precio_promedio_modelo': round(stats_modelo['avg'], 0)
            }
        }

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
