================================================================================
INFORME DE INVESTIGACION P1 - EXTRACCION DE PRODUCTOS
================================================================================

PROBLEMA INVESTIGADO
-------------------------------------------------------------------------------

En la prueba #3 (intent de recomendacion) el campo `products_mentioned` quedaba
vacio, aun cuando el flujo completo no arrojaba excepciones.

Sintoma observado:
- products_mentioned: []


INVESTIGACION REALIZADA
-------------------------------------------------------------------------------

Pasos ejecutados:
1. Captura de respuesta real del LLM en el flujo de recomendacion.
2. Comparacion de tokens de salida contra nombres del catalogo.
3. Validacion de la logica de fuzzy matching con distintos thresholds.
4. Revision del system prompt para la estrategia de recomendacion.
5. Confirmacion de la etapa de extraccion posterior al LLM.


CAUSA RAIZ
-------------------------------------------------------------------------------

El LLM no estaba obligado a mencionar nombres exactos del catalogo.

Salida generica actual:
- "Te recomendaria una laptop potente..."

Salida deseada:
- "Te recomendaria Laptop Pro X..."

Conclusiones:
- El problema principal no era el threshold.
- El problema principal era la ausencia de nombres extraibles en la respuesta.


OPCIONES EVALUADAS
-------------------------------------------------------------------------------

1. Substring simple: descartada por falsos positivos.
2. TF-IDF + cosine similarity: descartada por sobreingenieria.
3. NER: descartada por complejidad innecesaria.
4. Fuzzy matching con threshold mas bajo: ya aplicado, insuficiente.
5. Extraccion con segunda llamada LLM: viable pero con mayor costo y latencia.
6. Mejorar system prompt: opcion elegida.


CAMBIO IMPLEMENTADO
-------------------------------------------------------------------------------

Archivo: `src/core/config.py`

Se reforzo el prompt de recommendation con instrucciones explicitas:
- Usar nombres especificos del catalogo.
- Mencionar el nombre exacto del producto.
- Incluir ejemplo concreto de salida esperada.


IMPACTO ESPERADO
-------------------------------------------------------------------------------

Antes:
- products_mentioned = []

Despues (esperado):
- products_mentioned = ["Laptop Pro X", ...]

Metricas estimadas:
- Exactitud de extraccion: 0% -> 85-95%
- Latencia: sin cambios relevantes
- Costo de API: sin cambios


VALIDACION PENDIENTE
-------------------------------------------------------------------------------

Cuando haya cuota disponible:
1. Ejecutar prueba #3 con prompt actualizado.
2. Verificar mencion de nombres del catalogo.
3. Validar que la extraccion detecta los productos.
4. Ejecutar revalidacion completa.


LECCIONES APRENDIDAS
-------------------------------------------------------------------------------

1. Si se espera un comportamiento del LLM, debe indicarse explicitamente.
2. El postprocesamiento no puede extraer informacion que no existe.
3. Antes de ajustar thresholds, validar la calidad del contenido de salida.


ESTADO
-------------------------------------------------------------------------------

- Causa raiz identificada: SI
- Fix aplicado: SI
- Validacion E2E: PENDIENTE

================================================================================
