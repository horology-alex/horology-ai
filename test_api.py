import requests

API_URL = "http://localhost:5000"

print("🧪 TESTING HOROLOGY.IA API\n")

print("1️⃣ Health Check...")
r = requests.get(f"{API_URL}/health")
print(f"   {r.json()}\n")

print("2️⃣ Hulk 2020 Full Set...")
r = requests.post(f"{API_URL}/valorar", json={
    "referencia": "116610LV",
    "año": 2020,
    "tiene_caja": True,
    "tiene_papeles": True,
    "estado": "como nuevo"
})
result = r.json()
print(f"   Precio: {result['precio_estimado']:,.0f}€\n")

print("3️⃣ Submariner 1990 sin nada...")
r = requests.post(f"{API_URL}/valorar", json={
    "referencia": "16610",
    "año": 1990,
    "tiene_caja": False,
    "tiene_papeles": False,
    "estado": "bueno"
})
result = r.json()
print(f"   Precio: {result['precio_estimado']:,.0f}€\n")

print("✅ Tests completados!")
