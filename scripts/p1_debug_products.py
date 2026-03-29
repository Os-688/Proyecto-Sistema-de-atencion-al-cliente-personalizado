"""
P1 INVESTIGATION: Product Extraction Debug
Objetivo: Descubrir por qué products_mentioned=[] en recomendaciones
"""

import sys
import os
import json

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', newline='')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.app_factory import AppFactory
from src.infrastructure.database_sim import DatabaseSimulator
from difflib import SequenceMatcher

def debug_product_extraction():
    """Investiga por qué fuzzy matching no detecta productos"""
    
    print("\n" + "="*80)
    print("P1 INVESTIGATION: PRODUCT EXTRACTION DEBUG")
    print("="*80)
    
    # Inicializar
    components = AppFactory.create_components()
    chat_service = components.chat_service
    database = DatabaseSimulator()
    
    # PASO 1: Listar productos disponibles
    print("\n[PASO 1]: PRODUCTOS DISPONIBLES EN BD")
    print("-"*80)
    
    products = database.get_products()
    print(f"Total productos: {len(products)}")
    for i, p in enumerate(products, 1):
        print(f"  {i}. {p['name']:<30} (${p['price']:<8}) - {p['category']}")
    
    # PASO 2: Enviar recomendación y capturar respuesta EXACTA
    print("\n[PASO 2]: CAPTURAR RESPUESTA DEL LLM")
    print("-"*80)
    
    test_input = "Necesito un laptop para desarrollo y programación"
    print(f"Entrada: '{test_input}'")
    
    response = chat_service.process_message(test_input, "test_user_debug")
    print(f"\nIntent: {response.intent}")
    print(f"Respuesta LLM (EXACTA):")
    print(f"  {response.message}")
    print(f"\nMetadata:")
    print(f"  products_mentioned: {response.metadata.get('products_mentioned', [])}")
    
    # PASO 3: Análisis manual de matching
    print("\n[PASO 3]: ANÁLISIS MANUAL DE FUZZY MATCHING")
    print("-"*80)
    
    response_text = response.message
    response_lower = response_text.lower()
    response_tokens = response_lower.split()
    
    print(f"Response tokens: {response_tokens[:20]}... ({len(response_tokens)} total)")
    print(f"\nAnálisis por producto:")
    
    for product in products:
        product_name = product['name']
        product_name_lower = product_name.lower()
        product_tokens = product_name_lower.split()
        
        # 1. Búsqueda exacta
        exact_match = product_name_lower in response_lower
        
        # 2. Búsqueda fuzzy
        fuzzy_matches = []
        for prod_token in product_tokens:
            best_match = (0, None)
            for resp_word in response_tokens:
                similarity = SequenceMatcher(None, prod_token, resp_word).ratio()
                if similarity > best_match[0]:
                    best_match = (similarity, resp_word)
            if best_match[0] > 0:
                fuzzy_matches.append({
                    "token": prod_token,
                    "best_match": best_match[1],
                    "score": best_match[0]
                })
        
        print(f"\n  Producto: '{product_name}'")
        print(f"    Exact match: {exact_match}")
        
        if fuzzy_matches:
            max_score = max(m['score'] for m in fuzzy_matches)
            print(f"    Fuzzy matches:")
            for m in fuzzy_matches:
                threshold_85 = "✓" if m['score'] > 0.85 else "✗"
                threshold_70 = "✓" if m['score'] > 0.70 else "✗"
                print(f"      '{m['token']}' vs '{m['best_match']}': {m['score']:.2f} " +
                      f"(0.85: {threshold_85}, 0.70: {threshold_70})")
            print(f"    Max fuzzy score: {max_score:.2f}")
        else:
            print(f"    Fuzzy matches: NINGUNO")
    
    # PASO 4: Propuestas de fix
    print("\n[PASO 4]: PROPUESTAS DE FIX")
    print("-"*80)
    
    print("""
Opciones para mejorar product extraction:

1. SUBSTRING SIMPLE (más tolerante):
   └─ Buscar si el producto aparece como substring en respuesta
   └─ Ejemplo: "laptop" en "Dell Laptop para desarrollo"
   └─ Ventaja: Simple, rápido
   └─ Desventaja: Falsos positivos

2. TF-IDF + Cosine Similarity:
   └─ Calcular similitud entre producto y chunks de respuesta
   └─ Ventaja: Semánticamente correcto
   └─ Desventaja: Más lento, requiere scikit-learn

3. NER (Named Entity Recognition):
   └─ Extraer entidades desde respuesta LLM
   └─ Ventaja: Preciso, maneja variaciones
   └─ Desventaja: Requiere modelo adicional

4. FUZZY MATCHING CON MEJOR THRESHOLD:
   └─ Usar fuzzywuzzy o difflib con token_set_ratio
   └─ Ventaja: Balance entre precisión y tolerancia
   └─ Desventaja: Tuning de threshold

5. LLM-BASED EXTRACTION:
   └─ Pedirle al LLM "qué productos mencionaste?"
   └─ Ventaja: Preciso, entiende contexto
   └─ Desventaja: Extra API call

RECOMENDACIÓN: Empezar con #1 (substring simple) + #2 (TF-IDF)
    """)
    
    # PASO 5: Propuesta inmediata - Substring simple
    print("\n[PASO 5]: TEST RÁPIDO - SUBSTRING SIMPLE")
    print("-"*80)
    
    print("Resultados con substring matching (case-insensitive):")
    mentioned_substring = []
    for product in products:
        product_name_lower = product['name'].lower()
        if product_name_lower in response_lower:
            mentioned_substring.append(product['name'])
            print(f"  ✓ {product['name']}")
    
    print(f"\nTotal encontrado: {len(mentioned_substring)}")
    print(f"Problema: Pueden haber falsos positivos (e.g., 'Dell' aparece en varias descripciones)")

if __name__ == "__main__":
    debug_product_extraction()
