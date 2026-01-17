import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
MODEL = "gpt-4o-mini"

WATCH_SCHEMA = {
    "identidad": {
        "marca": "",
        "modelo": "",
        "referencia": "",
        "apodo": "",
        "año": None,
        "tamaño_mm": None,
        "material": ""
    },
    "estado": {
        "estado_global": "",
        "tiene_caja": None,
        "tiene_papeles": None,
        "faltan_eslabones": None,
        "tiene_rayaduras_visibles": None,
        "pulido": None,
        "ultimo_servicio": ""
    },
    "precio": {
        "precio_anuncio": None,
        "moneda": "",
        "ubicacion_vendedor": "",
        "tipo_vendedor": ""
    }
}
