import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import json

print("🚀 HOROLOGY.IA - Entrenamiento SIMPLE (6 features)")

# Cargar datos
print("\n📂 Cargando datos...")
df = pd.read_csv('data/rolex_dataset.csv')
print(f"✓ {len(df)} relojes cargados")

# Limpiar datos
print("\n🧹 Limpiando datos...")
df = df[df['price'].notna()]
df = df[df['price'] > 0]
print(f"✓ {len(df)} relojes después de filtrar precios inválidos")

# Extraer caja y papeles CON LÓGICA CORRECTA
df['has_box'] = df['scope of delivery'].fillna('').str.contains('Original box', case=False, regex=False) & ~df['scope of delivery'].fillna('').str.contains('No original box', case=False, regex=False)
df['has_box'] = df['has_box'].astype(int)

df['has_papers'] = df['scope of delivery'].fillna('').str.contains('original papers', case=False, regex=False) & ~df['scope of delivery'].fillna('').str.contains('no original papers', case=False, regex=False)
df['has_papers'] = df['has_papers'].astype(int)

# Verificar distribución
print("\n📊 Distribución caja/papeles:")
print(df.groupby(['has_box', 'has_papers'])['price'].agg(['mean', 'count']))

# Limpiar año
df['year of production'] = pd.to_numeric(df['year of production'], errors='coerce')
df['year of production'] = df['year of production'].fillna(df['year of production'].median())

# Rellenar categorías faltantes
df['condition'] = df['condition'].fillna('Unknown')
df['case material'] = df['case material'].fillna('Unknown')

print(f"✓ Dataset final: {len(df)} relojes")

# Preparar features SIMPLES (solo 6)
features = [
    'model',
    'year of production',
    'condition',
    'case material',
    'has_box',
    'has_papers'
]

X = df[features].copy()
y = df['price']

# Encoders para categorías
le_model = LabelEncoder()
le_condition = LabelEncoder()
le_material = LabelEncoder()

X['model_encoded'] = le_model.fit_transform(X['model'])
X['condition_encoded'] = le_condition.fit_transform(X['condition'])
X['material_encoded'] = le_material.fit_transform(X['case material'])

# Vector final de features (6 columnas)
X_encoded = X[[
    'model_encoded',
    'year of production',
    'condition_encoded',
    'material_encoded',
    'has_box',
    'has_papers'
]]

print("\n📊 Dividiendo datos...")
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

print("\n🤖 Entrenando Random Forest (300 árboles, 6 features)...")
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=20,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"\n✓ R² Score: {score:.4f}")

print("\n💾 Guardando modelo...")
with open('data/pricing_model_full.pkl', 'wb') as f:
    pickle.dump(model, f)

# Guardar encoders
encoders = {
    'model': {str(i): label for i, label in enumerate(le_model.classes_)},
    'condition': {str(i): label for i, label in enumerate(le_condition.classes_)},
    'material': {str(i): label for i, label in enumerate(le_material.classes_)}
}

with open('data/encoders.json', 'w') as f:
    json.dump(encoders, f, indent=2)

print("\n📈 Análisis de Impacto:")
feature_names = [
    'Modelo',
    'Año',
    'Estado',
    'Material',
    'Caja',
    'Papeles'
]
importance = model.feature_importances_
for name, imp in zip(feature_names, importance):
    print(f"  • {name}: {imp*100:.1f}%")

# Estadísticas
stats = {
    'total_watches': len(df),
    'avg_price': float(df['price'].mean()),
    'median_price': float(df['price'].median()),
    'features_used': len(feature_names)
}

with open('data/dataset_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("\n✅ Entrenamiento SIMPLE terminado!")
print(f"📊 {len(df)} relojes | 💰 Precio promedio: {stats['avg_price']:.0f}€")
print(f"🎯 {len(feature_names)} features (sin valores arbitrarios)")
