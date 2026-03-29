================================================================================
DISENO TECNICO P3 - SOPORTE MULTIINTENCION
Arquitectura propuesta para Sprint 2
================================================================================

RESUMEN EJECUTIVO
-------------------------------------------------------------------------------

Problema:
- Mensajes con varias intenciones reciben respuesta corta y generica.

Objetivo:
- Detectar todas las intenciones en un solo mensaje.
- Ejecutar multiples estrategias.
- Entregar una unica respuesta coherente que cubra todo.


ARQUITECTURA PROPUESTA
-------------------------------------------------------------------------------

Flujo actual (una intencion):
1. Clasificar intent principal.
2. Elegir una estrategia.
3. Responder.

Flujo propuesto (multiintencion):
1. Clasificar todas las intenciones.
2. Filtrar por score minimo.
3. Ejecutar varias estrategias.
4. Sintetizar respuesta unificada.
5. Retornar metadata con trazabilidad.


COMPONENTES PRINCIPALES
-------------------------------------------------------------------------------

1) Clasificador multiintencion
- Archivo objetivo: `src/clients/google_ai_studio_client.py`
- Nuevo metodo: `classify_all_intents(user_input)`
- Salida: lista de intents con score y keywords detectadas.

2) Procesador multiestrategia
- Archivo nuevo: `src/application/multi_intent_processor.py`
- Tareas:
  - Ejecutar estrategias por intent significativo.
  - Manejar errores por estrategia sin romper todo el flujo.
  - Consolidar metadata.

3) Sintetizador de respuesta
- Archivo nuevo: `src/application/response_synthesizer.py`
- Modos de sintesis:
  - `sequential`: concatena respuestas (rapido).
  - `llm`: reescribe con LLM (mas coherente, mas costo).
  - `weighted`: mezcla por relevancia (equilibrado).


INTEGRACION EN CHAT SERVICE
-------------------------------------------------------------------------------

Archivo: `src/application/chat_service.py`

Decision de ruteo:
- Si hay mas de una intencion sobre threshold, usar `MultiIntentProcessor`.
- Si no, mantener flujo actual de una estrategia (compatibilidad).


CONFIGURACION RECOMENDADA
-------------------------------------------------------------------------------

Archivo: `src/core/config.py`

Nuevos parametros:
- `MULTI_INTENT_ENABLED = True`
- `MULTI_INTENT_THRESHOLD = 0.60`
- `MULTI_INTENT_SYNTHESIS_MODE = "llm" | "sequential" | "weighted"`


FASES DE IMPLEMENTACION
-------------------------------------------------------------------------------

Fase 1 (3-4h): Base
- Dataclass de score por intent.
- Clasificador multiintencion.
- Procesador multiestrategia.
- Sintesis secuencial.
- Pruebas unitarias.

Fase 2 (2-3h): Sintesis avanzada
- Modo LLM.
- Comparativa de modos.
- Toggle por configuracion.

Fase 3 (1-2h): Optimizacion
- Cache de clasificacion.
- Paralelismo controlado.
- Endurecimiento de manejo de errores.

Fase 4 (1h): Validacion
- Reejecucion de suite.
- Comparativa antes/despues.
- Metricas finales.


ESTRATEGIA DE PRUEBAS
-------------------------------------------------------------------------------

Casos nuevos:
1. Deteccion de multiples intents en una sola entrada.
2. Ejecucion de varias estrategias y presencia en metadata.
3. Sintesis coherente sin omisiones de intent.
4. Compatibilidad retroactiva para mensajes de una sola intencion.


RIESGOS Y MITIGACIONES
-------------------------------------------------------------------------------

Riesgo: aumento de latencia
- Mitigacion: modo secuencial por defecto en entornos sensibles.

Riesgo: mayor complejidad
- Mitigacion: cobertura de tests y rollout gradual.

Riesgo: falsos positivos en clasificacion
- Mitigacion: tuning de threshold y telemetria de calidad.


METRICAS DE EXITO
-------------------------------------------------------------------------------

Objetivos:
- Cobertura de intenciones multiples >90%.
- Respuestas de caso multiintencion >200 chars.
- Falsos positivos <5%.
- Sin regresiones en flujo de intencion unica.


ESTADO
-------------------------------------------------------------------------------

- Diseno tecnico: COMPLETO
- Implementacion: PENDIENTE
- Dependencias bloqueantes: NINGUNA

================================================================================
