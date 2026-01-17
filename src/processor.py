import json
import requests
from src.prompt import get_prompt_with_examples

OLLAMA_URL = "http://localhost:11434/api/generate"

def process_listing(listing_text):
    """Procesa un anuncio usando Ollama (local)"""
    try:
        prompt = get_prompt_with_examples(listing_text)
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
        )
        
        result = json.loads(response.json()['response'])
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_listing = """
    Rolex Submariner Date 16800
    Año: 1983
    Estado: Usado (Bueno)
    Presenta señales visibles de uso
    Con estuche original, sin documentos
    Revisado diciembre 2025
    Precio: 8.450€
    Italia
    """
    
    print("Procesando anuncio con Ollama (local)...")
    result = process_listing(test_listing)
    if result:
        print("\n✓ Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n✗ Error al procesar")
