"""
RE-EJECUCIÓN DE PRUEBAS CRÍTICAS: Validación de quick wins
Pruebas: #2 (support), #3 (recommendation), #7 (resiliencia), #8 (edge case)
"""

import sys
import os
import json
import time
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', newline='')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.app_factory import AppFactory

def rerun_critical_tests():
    """Re-ejecuta pruebas 2, 3, 7, 8 después de quick wins"""
    
    print("\n" + "="*80)
    print("RE-EJECUCIÓN: VALIDACIÓN DE QUICK WINS")
    print("="*80)
    print("\nPruebas a re-ejecutar:")
    print("  #2: Support - Enriquecimiento de metadata")
    print("  #3: Recommendation - Fuzzy matching en products")
    print("  #7: Resiliencia - Latencia y reintentos")
    print("  #8: Edge case - Respuesta para input largo")
    
    # Inicializar componentes
    print("\n[INICIALIZANDO COMPONENTES]")
    try:
        components = AppFactory.create_components()
        chat_service = components.chat_service
        print("✓ Componentes listos")
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    
    results = {}
    
    # PRUEBA #2: Support - Metadata enriquecida
    print("\n" + "="*80)
    print("PRUEBA #2: SUPPORT - METADATA ENRIQUECIDA")
    print("="*80)
    
    user_msg = "Tengo un problema con mi cuenta, no puedo acceder"
    start = time.time()
    try:
        response = chat_service.process_message(user_msg, "C001")
        elapsed = time.time() - start
        
        # Verificar que customer_id está en metadata
        has_customer_id = "customer_id" in response.metadata
        has_customer_name = "customer_name" in response.metadata
        has_open_tickets = "open_tickets_count" in response.metadata
        
        print(f"Intent: {response.intent}")
        print(f"Metadata keys: {list(response.metadata.keys())}")
        print(f"✓ customer_id present: {has_customer_id}")
        print(f"✓ customer_name present: {has_customer_name}")
        print(f"✓ open_tickets_count present: {has_open_tickets}")
        print(f"Tiempo: {elapsed:.2f}s")
        
        status = "PASS" if (has_customer_id and has_customer_name and has_open_tickets) else "PARTIAL"
        results["test_2"] = {
            "status": status,
            "elapsed": elapsed,
            "improvements": {
                "customer_id": has_customer_id,
                "customer_name": has_customer_name,
                "open_tickets_count": has_open_tickets
            },
            "metadata": response.metadata
        }
        print(f"\nResultado: {status}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results["test_2"] = {"status": "FAIL", "error": str(e)}
    
    # PRUEBA #3: Recommendation - Fuzzy matching en productos
    print("\n" + "="*80)
    print("PRUEBA #3: RECOMMENDATION - FUZZY MATCHING PRODUCTOS")
    print("="*80)
    
    user_msg = "Necesito un laptop para desarrollo y programación"
    start = time.time()
    try:
        response = chat_service.process_message(user_msg, "test_user_03")
        elapsed = time.time() - start
        
        # Verificar que products_mentioned NO está vacío (main improvement)
        products_mentioned = response.metadata.get("products_mentioned", [])
        has_products = len(products_mentioned) > 0
        
        print(f"Intent: {response.intent}")
        print(f"Products mentioned: {products_mentioned}")
        print(f"Cantidad: {len(products_mentioned)}")
        print(f"✓ Products detected (fuzzy matching): {has_products}")
        print(f"Tiempo: {elapsed:.2f}s")
        
        status = "PASS" if has_products else "PARTIAL"
        results["test_3"] = {
            "status": status,
            "elapsed": elapsed,
            "products_mentioned": products_mentioned,
            "improvement": "Cambio de exact matching a fuzzy matching"
        }
        print(f"\nResultado: {status}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results["test_3"] = {"status": "FAIL", "error": str(e)}
    
    # PRUEBA #7: Resiliencia - Detectar "urgente" como support
    print("\n" + "="*80)
    print("PRUEBA #7: RESILIENCIA - MEJORA DE KEYWORDS")
    print("="*80)
    
    user_msg = "Tengo un problema urgente, ¿puede ayudarme?"
    start = time.time()
    try:
        response = chat_service.process_message(user_msg, "test_user_07")
        elapsed = time.time() - start
        
        # Ahora debería detectar 'support' en lugar de 'general' gracias a "urgente"
        is_support = response.intent == "support"
        
        print(f"Intent: {response.intent} (esperado: support)")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"✓ Detectó support (keyword 'urgente'): {is_support}")
        print(f"Tiempo: {elapsed:.2f}s")
        
        status = "PASS" if is_support else "PARTIAL"
        results["test_7"] = {
            "status": status,
            "elapsed": elapsed,
            "intent_detected": response.intent,
            "improvement": "Agregó keywords: urgente, crítico, grave, fallo"
        }
        print(f"\nResultado: {status}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results["test_7"] = {"status": "FAIL", "error": str(e)}
    
    # PRUEBA #8: Edge case - respuesta para input largo/multi-intención
    print("\n" + "="*80)
    print("PRUEBA #8: EDGE CASE - INPUT LARGO/MULTI")
    print("="*80)
    
    user_msg = """
    Tengo varios problemas: primero, mi laptop no arranca; segundo, 
    los productos que vieron en el catálogo están fuera de stock; 
    y tercero, quiero saber si hay una política de descuentos por volumen. 
    También me gustaría reportar un problema con la facturación del mes pasado.
    ¿Pueden ayudarme con todo esto?
    """
    start = time.time()
    try:
        response = chat_service.process_message(user_msg, "test_user_08")
        elapsed = time.time() - start
        
        # Verificar respuesta no está truncada
        response_length = len(response.message)
        input_length = len(user_msg)
        ratio = response_length / input_length if input_length > 0 else 0
        
        print(f"Intent: {response.intent}")
        print(f"Input length: {input_length} chars")
        print(f"Response length: {response_length} chars")
        print(f"Ratio: {ratio:.2%}")
        print(f"Respuesta suficiente: {response_length > 100}")
        print(f"Tiempo: {elapsed:.2f}s")
        
        # Ahora debería > 79 chars (mejora sobre antes)
        status = "PASS" if response_length > 100 else "PARTIAL"
        results["test_8"] = {
            "status": status,
            "elapsed": elapsed,
            "input_length": input_length,
            "response_length": response_length,
            "ratio": ratio,
            "note": "Focus en multi-intención → observar si respuesta es coherente"
        }
        print(f"\nResultado: {status}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        results["test_8"] = {"status": "FAIL", "error": str(e)}
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE RE-EJECUCIÓN")
    print("="*80)
    
    statuses = [r.get("status") for r in results.values()]
    pass_count = statuses.count("PASS")
    partial_count = statuses.count("PARTIAL")
    fail_count = statuses.count("FAIL")
    
    print(f"\n✓ PASS:    {pass_count}/4")
    print(f"⚠ PARTIAL: {partial_count}/4")
    print(f"✗ FAIL:    {fail_count}/4")
    
    print("\nMejoras validadas:")
    print(f"  #2 Support metadata: {results['test_2'].get('status')}")
    print(f"  #3 Product fuzzy match: {results['test_3'].get('status')}")
    print(f"  #7 Keyword detection: {results['test_7'].get('status')}")
    print(f"  #8 Edge case response: {results['test_8'].get('status')}")
    
    # Guardar resultados
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(project_root, "informes", "revalidacion")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_file = os.path.join(
        output_dir,
        f"{timestamp}_revalidacion_resultados_quick_wins_v01.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados guardados en: {output_file}")
    
    return results

if __name__ == "__main__":
    results = rerun_critical_tests()
    
    if results:
        passed_all = all(r.get("status") == "PASS" for r in results.values())
        print("\n" + "="*80)
        if passed_all:
            print("✓ VALIDACIÓN EXITOSA: Todos los quick wins funcionan")
        else:
            print("⚠ VALIDACIÓN PARCIAL: Algunos quick wins necesitan ajuste")
        print("="*80)
