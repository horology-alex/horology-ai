import pandas as pd
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

print("📂 Cargando dataset...")
with open('data/watches_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("🔧 Preparando features...")
features = []
for watch in data:
    f = {
        'año': watch.get('identidad', {}).get('año') or 2000,
        'caja': 1 if watch.get('estado', {}).get('tiene_caja') else 0,
        'papeles': 1 if watch.get('estado', {}).get('tiene_papeles') else 0,
        'rayaduras': 1 if watch.get('estado', {}).get('tiene_rayaduras_visibles') else 0,
        'pulido': 1 if watch.get('estado', {}).get('pulido') else 0,
        'precio': watch.get('precio', {}).get('precio_anuncio', 0)
    }
    
    # Estado
    estado = watch.get('estado', {}).get('estado_global', '') or ''
    estado_map = {'como nuevo': 3, 'muy bueno': 2, 'bueno': 1, 'aceptable': 0}
    f['estado_num'] = estado_map.get(estado.lower(), 1)
    
    # Material
    material = watch.get('identidad', {}).get('material') or ''
    material = str(material).lower()
    if 'oro' in material and 'bicolor' not in material:
        f['material_num'] = 1
    elif 'bicolor' in material:
        f['material_num'] = 2
    else:
        f['material_num'] = 0
    
    # Hulk/Kermit
    ref = watch.get('identidad', {}).get('referencia') or ''
    apodo = watch.get('identidad', {}).get('apodo') or ''
    ref = str(ref)
    apodo = str(apodo).lower()
    
    f['es_hulk'] = 1 if ('116610lv' in ref.lower() or 'hulk' in apodo) else 0
    f['es_kermit'] = 1 if ('16610lv' in ref.lower() or 'kermit' in apodo) else 0
    
    if f['precio'] > 0:  # Solo añadir si tiene precio válido
        features.append(f)

df = pd.DataFrame(features)

print(f"\n📊 Dataset: {len(df)} relojes")
print(f"\n{df[['año', 'caja', 'papeles', 'estado_num', 'precio']].head()}")

X = df.drop('precio', axis=1)
y = df['precio']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print("\n🤖 Entrenando modelo...")
model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\n✅ Modelo entrenado!")
print(f"\n📈 Métricas:")
print(f"   Error medio: {mae:,.0f}€")
print(f"   Precisión R²: {r2:.1%}")

print(f"\n🎯 Factores más importantes:")
importances = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for _, row in importances.head(5).iterrows():
    print(f"   {row['feature']:15s}: {row['importance']:.1%}")

import pickle
with open('data/pricing_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print(f"\n💾 Modelo guardado")

print(f"\n🧪 Ejemplos de predicción:")
print(f"{'Real':>10s} | {'Predicho':>10s} | {'Diferencia':>12s}")
print("-" * 40)
for real, pred in list(zip(y_test, y_pred))[:5]:
    diff = pred - real
    print(f"{real:>9,.0f}€ | {pred:>9,.0f}€ | {diff:>+10,.0f}€")
