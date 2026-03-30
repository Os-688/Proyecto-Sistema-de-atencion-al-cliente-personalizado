# Scripts de Pruebas Operativas

Esta carpeta contiene scripts de validacion manual complementaria a `pytest`.

## Precondiciones Minimas

1. Entorno virtual activo.
2. Dependencias instaladas (`requirements.txt` y/o `requirements-dev.txt`).
3. Proveedor LLM configurado (`LLM_PROVIDER`).
4. Si usas `openai` o `google_ai_studio`, configurar API key correspondiente.
5. Si no hay API key, usar `LLM_PROVIDER=mock` para pruebas locales sin llamadas externas.

Activacion recomendada del entorno local estandar (`.venv`):

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/Mac
source .venv/bin/activate
```

## Objetivo

- Ejecutar escenarios de pruebas funcionales guiadas.
- Validar quick wins y regresiones puntuales.
- Generar evidencia operativa para `informes/`.

## Decision Rapida (30 segundos)

| Si necesitas... | Ejecuta... | Resultado |
|---|---|---|
| Verificar flujo completo en 8 escenarios | `python scripts/run_8_tests.py` | JSON en `informes/revalidacion/` |
| Confirmar solo quick wins criticos | `python scripts/revalidation_after_fixes.py` | JSON en `informes/revalidacion/` |
| Probar conectividad E2E basica | `python scripts/test_smoke.py` | Salida en consola |
| Investigar por que no se detectan productos | `python scripts/p1_debug_products.py` | Diagnostico en consola |
| Validar mapeo de cliente C001 | `python scripts/p2_validate_customer_mapping.py` | Validacion en consola |

## Scripts Disponibles

### 1) `run_8_tests.py`

Ejecuta la suite funcional de 8 pruebas sobre el flujo de chat.

Comando:

```bash
python scripts/run_8_tests.py
```

Salida:
- JSON en `informes/revalidacion/` con timestamp.

### 2) `revalidation_after_fixes.py`

Re-ejecuta pruebas criticas despues de aplicar fixes:
- Test #2 (support metadata)
- Test #3 (recommendation / products)
- Test #7 (resiliencia)
- Test #8 (input largo / multi-intencion)

Comando:

```bash
python scripts/revalidation_after_fixes.py
```

Salida:
- JSON en `informes/revalidacion/` con timestamp.

### 3) `test_smoke.py`

Smoke test rapido de conectividad y flujo basico.

Comando:

```bash
python scripts/test_smoke.py
```

Salida:
- No guarda archivo por defecto.
- Imprime resultado en consola (stdout).

### 4) `p1_debug_products.py`

Script de diagnostico para investigar extraccion de productos.

Comando:

```bash
python scripts/p1_debug_products.py
```

Salida:
- Diagnostico en consola (stdout).

### 5) `p2_validate_customer_mapping.py`

Valida mapeo de customer ID para enriquecimiento de metadata.

Comando:

```bash
python scripts/p2_validate_customer_mapping.py
```

Salida:
- Validacion en consola (stdout).

## Riesgo de Mutacion de Datos

Atencion: estos scripts operativos pueden mutar datos reales del proyecto
(por ejemplo, crear tickets en `data/tickets.json`) cuando ejecutan flujos de
soporte.

- `pytest` en `tests/` usa aislamiento de datos.
- `scripts/` no aplica ese aislamiento automaticamente.

Recomendacion a largo plazo:
- Ejecutar scripts con copia de `data/` o en entorno de prueba dedicado.
- Evitar usarlos en ramas de release sin control de evidencia.
- Registrar en `informes/` toda corrida que muta estado.

## Convencion de Artefactos

Los archivos de salida se guardan en `informes/` siguiendo:

`AAAA-MM-DD_HHMM_tipo_modulo_estado_vNN.ext`

Referencia de convencion completa:
- [informes/GUIA_CREACION_INFORMES.md](../informes/GUIA_CREACION_INFORMES.md)

## Nota de Uso

- Estos scripts no reemplazan `pytest`; lo complementan.
- Para CI/CD, priorizar `pytest tests/ -v`.
- Para analisis funcional y evidencia ejecutiva, usar esta carpeta.
