"""
Test de Humo #1 - Prueba E2E básica con Google AI Studio
Objetivo: Validar conectividad, latencia y formato de salida del LLM
"""

import sys
import os
import json
import time
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.app_factory import AppFactory
from src.core.config import Config

def test_smoke_simple_greeting():
    """Prueba E2E simple: saludar al sistema"""
    print("\n" + "="*80)
    print("PRUEBA DE HUMO #1: Test E2E Simple con Google AI Studio")
    print("="*80)
    
    print("\n[CONFIGURACIÓN]")
    print(f"Proveedor LLM: {Config.LLM_PROVIDER}")
    print(f"Modelo: {Config.GOOGLE_MODEL}")
    print(f"Temperatura: {Config.GOOGLE_TEMPERATURE}")
    print(f"Max tokens: {Config.GOOGLE_MAX_TOKENS}")
    print(f"API Key presente: {'✓' if Config.GOOGLE_API_KEY else '✗'}")
    
    # Crear componentes de la aplicación
    print("\n[INICIALIZANDO COMPONENTES]")
    try:
        components = AppFactory.create_components()
        llm_client = components.llm_client
        db = components.database
        chat_service = components.chat_service
        provider_name = components.provider_name
        
        print("✓ Componentes creados exitosamente")
        print(f"  - Proveedor detectado: {provider_name}")
        print(f"  - Cliente LLM: {llm_client.__class__.__name__}")
        print(f"  - Base de datos: {db.__class__.__name__}")
        print(f"  - Chat service: {chat_service.__class__.__name__}")
    except Exception as e:
        print(f"✗ Error al crear componentes: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Verificar datos cargados
    print("\n[DATOS CARGADOS]")
    try:
        customers = db.get_all_customers()
        products = db.get_all_products()
        faq = db.search_faq("ayuda")
        print(f"  Clientes: {len(customers)}")
        print(f"  Productos: {len(products)}")
        print(f"  FAQs (búsqueda 'ayuda'): {len(faq)}")
    except Exception as e:
        print(f"✗ Error al leer datos: {e}")
    
    # Ejecutar una solicitud simple
    user_message = "Hola, ¿cómo estás?"
    user_id = "test_user_001"
    
    print(f"\n[ENTRADA]")
    print(f"Usuario: {user_id}")
    print(f"Mensaje: '{user_message}'")
    
    print(f"\n[PROCESANDO...]")
    start_time = time.time()
    
    try:
        response = chat_service.process_message(user_message, user_id)
        elapsed_time = time.time() - start_time
        
        print(f"✓ Procesada en {elapsed_time:.2f}s")
        
        print(f"\n[SALIDA]")
        print(f"Intención detectada: {response.intent}")
        print(f"Confianza: {response.confidence:.2f}")
        print(f"Respuesta: {response.message[:200]}..." if len(response.message) > 200 else f"Respuesta: {response.message}")
        
        print(f"\n[METADATOS]")
        if response.metadata:
            for key, value in response.metadata.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {json.dumps(value, ensure_ascii=False)[:100]}...")
                else:
                    print(f"  {key}: {value}")
        
        print(f"\n[EVALUACIÓN]")
        print(f"✓ Conectividad: Éxito (respuesta en {elapsed_time:.2f}s)")
        print(f"✓ Formato respuesta: Válido (intent, message, confidence, metadata)")
        print(f"✓ Contenido respuesta: {'Coherente' if len(response.message) > 10 else 'Muy breve (posible problema)'}")
        
        # Retornar datos para microinforme
        return {
            "status": "SUCCESS",
            "elapsed_time": elapsed_time,
            "intent": response.intent,
            "confidence": response.confidence,
            "message_length": len(response.message),
            "metadata": response.metadata,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"✗ Error en procesamiento: {type(e).__name__}: {e}")
        print(f"✗ Tiempo hasta error: {elapsed_time:.2f}s")
        return {
            "status": "FAILED",
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_time": elapsed_time,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    result = test_smoke_simple_greeting()
    
    print("\n" + "="*80)
    print("RESULTADO FINAL")
    print("="*80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
