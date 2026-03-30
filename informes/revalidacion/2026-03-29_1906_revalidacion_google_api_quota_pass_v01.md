# Revalidacion de cuota Google API

## 1. Contexto
Se retoma la sesion pendiente que habia quedado bloqueada por limite de cuota en Google AI Studio.
La guia aplicada para nomenclatura y ubicacion es: informes/GUIA_CREACION_INFORMES.md.

## 2. Problema
No era posible cerrar la revalidacion de P1 (extraccion de productos) porque la API devolvia 429 RESOURCE_EXHAUSTED.

## 3. Causa raiz
Se habia alcanzado el limite diario del modelo en free tier.

## 4. Cambios aplicados
1. Se preparo un probe minimo sin reintentos: scripts/check_google_quota_minimal.py.
2. El probe hace exactamente una solicitud corta para minimizar consumo.
3. Se evito usar scripts de suite completa antes de confirmar cuota disponible.

## 5. Validacion
Ejecucion:
- Comando: .\\.venv\\Scripts\\python.exe scripts/check_google_quota_minimal.py
- Resultado: {"ok": true, "status": "quota_available", "model": "gemini-2.5-flash", "elapsed_sec": 5.368}

Interpretacion:
- La cuota esta restablecida y disponible para continuar revalidacion pendiente.
- Consumo usado para verificacion: 1 request minimo.

## 6. Impacto
1. Se desbloquea la revalidacion real de P1 y la suite de 8 pruebas.
2. Se reduce riesgo de desperdiciar requests al confirmar disponibilidad antes de correr pruebas largas.

## 7. Riesgos
1. El limite puede agotarse de nuevo si se ejecutan muchas pruebas consecutivas.
2. La latencia de API puede variar durante revalidacion completa.

## 8. Proximos pasos
1. Ejecutar scripts/revalidation_after_fixes.py para confirmar P1 con quota disponible.
2. Ejecutar scripts/run_8_tests.py para cierre integral antes/despues.
3. Guardar resultados nuevos en informes/revalidacion con version incremental.
