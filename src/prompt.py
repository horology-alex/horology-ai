TRAINING_EXAMPLES = [
    {
        "input": """Rolex Submariner Date "Kermit" 16610LV
Año: 2007
Estado: Como nuevo y sin estrenar
Sin arañazos ni abolladuras, no pulido
Con estuche original y documentos originales
Precio: 66.032€
Ubicación: Estados Unidos, Miami
Comerciante profesional""",
        "output": {
            "identidad": {"marca": "Rolex", "modelo": "Submariner Date", "referencia": "16610LV", "apodo": "Kermit", "año": 2007, "tamaño_mm": 40, "material": "acero"},
            "estado": {"estado_global": "como nuevo", "tiene_caja": True, "tiene_papeles": True, "faltan_eslabones": None, "tiene_rayaduras_visibles": False, "pulido": False, "ultimo_servicio": "no se indica"},
            "precio": {"precio_anuncio": 66032, "moneda": "EUR", "ubicacion_vendedor": "Estados Unidos, Miami", "tipo_vendedor": "comerciante profesional"}
        }
    },
    {
        "input": """Rolex Submariner Date 116610LV Hulk
Año: 2018
Como nuevo, con estuche original, sin documentos
Presenta señales de uso muy leves apenas perceptibles
Precio: 15.500€
España, vendedor privado""",
        "output": {
            "identidad": {"marca": "Rolex", "modelo": "Submariner Date", "referencia": "116610LV", "apodo": "Hulk", "año": 2018, "tamaño_mm": 40, "material": "acero"},
            "estado": {"estado_global": "muy bueno", "tiene_caja": True, "tiene_papeles": False, "faltan_eslabones": None, "tiene_rayaduras_visibles": True, "pulido": False, "ultimo_servicio": "no se indica"},
            "precio": {"precio_anuncio": 15500, "moneda": "EUR", "ubicacion_vendedor": "España", "tipo_vendedor": "vendedor privado"}
        }
    }
]

SYSTEM_PROMPT = """Eres un experto en relojería. Extrae información de anuncios y devuelve JSON estructurado.

REGLAS:
- "full set" → tiene_caja=true, tiene_papeles=true
- "ligeras señales" o "hairlines" → tiene_rayaduras_visibles=true
- "never polished" → pulido=false
- Si no se menciona → null
- Si hay contradicción, prioriza la descripción del vendedor

APODOS: 116610LV=Hulk, 16610LV=Kermit, 126610LV=Starbucks

Responde SOLO con JSON válido."""

def get_prompt_with_examples(listing_text):
    examples_text = "\n\n".join([
        f"EJEMPLO {i+1}:\nINPUT:\n{ex['input']}\n\nOUTPUT:\n{ex['output']}"
        for i, ex in enumerate(TRAINING_EXAMPLES)
    ])
    
    return f"""{SYSTEM_PROMPT}

{examples_text}

Ahora procesa:

INPUT:
{listing_text}

OUTPUT (solo JSON):"""
