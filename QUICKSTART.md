# Guía Rápida de Uso

## 🚀 Inicio Rápido (5 minutos)

### 1. Clonar e Instalar

```bash
# Clonar repositorio
git clone <url-del-repo>
cd Proyecto-Sistema-de-atencion-al-cliente-personalizado

# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# (Opcional para desarrollo y testing)
pip install -r requirements-dev.txt
```

### 2. Configurar API Key (Opcional)

**Opción A: Usar Google AI Studio (RECOMENDADO - Tokens Gratuitos)**

Si quieres probar la app **sin costo inicial**, usa Google AI Studio:

1. Ve a https://aistudio.google.com
2. Inicia sesión con tu cuenta Google
3. Haz clic en "Get API key"
4. Copia tu API key

Luego crea un archivo `.env` en la raíz del proyecto:

```env
LLM_PROVIDER=google_ai_studio
GOOGLE_API_KEY=tu-api-key-aqui
```

O configura variables de entorno:

```bash
# Linux/Mac:
export LLM_PROVIDER="google_ai_studio"
export GOOGLE_API_KEY="tu-api-key-aqui"

# Windows PowerShell:
$env:LLM_PROVIDER = "google_ai_studio"
$env:GOOGLE_API_KEY = "tu-api-key-aqui"
```

**Opción B: Usar OpenAI (requiere pago)**

También puedes crear un archivo `.env`:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
LLM_PROVIDER=openai
```

**Opción C: Sin API Key (modo demo)**

- El sistema funciona en modo simulación
- Respuestas basadas en keywords
- Ideal para desarrollo y testing
- Sin costo, sin API key necesaria

### 3. Ejecutar

**Interfaz CLI (Terminal):**
```bash
python main.py
```

**Interfaz Web (Streamlit):**
```bash
streamlit run app.py
```

---

## 💬 Ejemplos de Uso

### Soporte Técnico
```
💬 Tú: No puedo iniciar sesión en mi cuenta
🤖 Asistente: [Detecta "support"] 
              [Proporciona solución paso a paso]
              [Crea ticket #107]
```

### Recomendaciones
```
💬 Tú: Busco una laptop para diseño gráfico con buen presupuesto
🤖 Asistente: [Detecta "recommendation"]
              [Consulta catálogo]
              [Recomienda: Laptop Pro X ($1,299.99)]
```

### Quejas
```
💬 Tú: El producto llegó dañado, estoy muy molesto
🤖 Asistente: [Detecta "complaint", severidad: high]
              [Respuesta empática]
              [Ofrece compensación]
              [Crea ticket para supervisor]
```

### FAQ
```
💬 Tú: ¿Cuánto tarda el envío?
🤖 Asistente: [Detecta "faq"]
              [Busca en base de conocimiento]
              [Respuesta: "3-5 días hábil estándar, 1-2 express"]
```

---

## 🧪 Testing

Antes de correr tests, instala dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
```

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html

# Test específico
pytest tests/test_chat_service.py -v
```

Resultado esperado: suite ejecutada sin modificar los archivos reales de `data/`.

**Aislamiento en pruebas**:
- Los tests usan una copia temporal de `data/` (definida en `tests/conftest.py`).
- Ejecutar tests no debe modificar `data/tickets.json` ni otros JSON reales.

### Testing Operativo con Scripts

Además de `pytest`, el proyecto incluye scripts operativos para validaciones guiadas:

```bash
python scripts/run_8_tests.py
python scripts/revalidation_after_fixes.py
python scripts/test_smoke.py
```

Documentación completa de propósito, entradas y salidas:

- [scripts/README.md](scripts/README.md)

Los resultados y artefactos se guardan en:

- `run_8_tests.py` -> `informes/revalidacion/` (JSON con timestamp)
- `revalidation_after_fixes.py` -> `informes/revalidacion/` (JSON con timestamp)
- `test_smoke.py` -> salida en consola (no guarda archivo por defecto)

Importante:

- `pytest` usa aislamiento de datos de prueba.
- `scripts/` puede mutar datos reales en `data/` durante pruebas funcionales.

Guia recomendada por tipo de uso:

- Si necesitas pruebas automatizadas de desarrollo: usa `pytest`.
- Si necesitas validacion funcional manual y evidencia: usa `scripts/`.
- Si necesitas trazabilidad historica: revisa `informes/`.

---

## 🎮 Comandos CLI

Dentro de la interfaz CLI (`python main.py`):

| Comando | Descripción |
|---------|-------------|
| `/ayuda` | Muestra ayuda completa |
| `/limpiar` | Limpia historial de conversación |
| `/stats` | Muestra estadísticas de la sesión |
| `/usuario 1` | Simula ser usuario con ID 1 (1-4) |
| `/salir` | Termina la conversación |

Métricas mostradas por `/stats`:

- `avg_response_time_ms`: promedio de latencia por respuesta.
- `p95_response_time_ms`: latencia en percentil 95.
- `fallback_to_general_count` y `fallback_rate_pct`: frecuencia de fallback a intención general.
- `intent_accuracy_pct`: accuracy de clasificación si hay etiquetas esperadas.
- `intent_evaluated_samples`: cantidad de muestras usadas para accuracy.

Lectura rápida recomendada:

- Si sube `fallback_rate_pct`, revisar reglas de detección de intención.
- Si sube `p95_response_time_ms`, revisar prompts o dependencia LLM.
- Si `intent_accuracy_pct` aparece como N/A, no se están enviando etiquetas esperadas.

---

## 🛠️ Estructura del Proyecto

```
Proyecto-Sistema-de-atencion-al-cliente-personalizado/
├── src/
│   ├── core/               # Interfaces y configuración
│   ├── policies/           # Reglas de negocio aisladas
│   ├── clients/            # Cliente OpenAI
│   ├── infrastructure/     # Base de datos simulada
│   ├── strategies/         # 5 estrategias de chat
│   ├── factories/          # Factory Pattern
│   ├── application/        # Servicio de chat
│   └── ui/                 # CLI y Streamlit
├── data/                   # Datos JSON simulados
├── scripts/                # Scripts de testing operativo y diagnóstico
├── tests/                  # Tests unitarios (pytest)
├── informes/               # Evidencia, análisis, revalidaciones y resúmenes
├── main.py                 # Entry point CLI
├── app.py                  # Entry point Streamlit
└── requirements.txt        # Dependencias
```

---

## 🔧 Configuración Avanzada

### Cambiar Modelo de OpenAI

Editar [src/core/config.py](src/core/config.py):

```python
OPENAI_MODEL: str = "gpt-4"  # Cambiar de gpt-3.5-turbo a gpt-4
```

### Agregar Nueva Estrategia

1. Crear archivo en `src/strategies/`:

```python
# src/strategies/refund_strategy.py
from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse

class RefundStrategy(IChatStrategy):
    def __init__(self, llm_client, database):
        self.llm_client = llm_client
        self.database = database
    
    def process(self, context: ChatContext) -> ChatResponse:
        # Tu lógica de reembolsos
        return ChatResponse(
            message="Procesando reembolso...",
            intent="refund",
            confidence=0.9
        )
    
    def get_strategy_name(self) -> str:
        return "RefundStrategy"
```

2. Registrar en `StrategyFactory`:

```python
# src/factories/strategy_factory.py
from src.strategies.refund_strategy import RefundStrategy

self._strategies["refund"] = RefundStrategy(llm_client, database)
```

3. Agregar prompt en `Config.SYSTEM_PROMPTS`

---

## 🎯 Casos de Uso Pre-cargados

El sistema incluye datos de ejemplo:

- **5 Clientes**: Con diferentes membresías (Premium, Standard, Basic)
- **6 Productos**: Electrónica, accesorios, audio
- **5 Tickets**: Histórico de soporte
- **8 FAQ**: Preguntas frecuentes comunes

Simula ser un usuario con `/usuario <id>` (1-4).

---

## 🐛 Troubleshooting

### Error: "OpenAI API key no configurada"
**Solución**: 
- Configura la variable de entorno `OPENAI_API_KEY`
- O usa el modo simulación (funciona sin API key)

### Error: "ModuleNotFoundError"
**Solución**:
```bash
pip install -r requirements.txt
```

### Tests fallan
**Solución**:
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements-dev.txt

# Verificar entorno virtual activo
```

### Streamlit no abre
**Solución**:
```bash
# Verificar instalación
pip show streamlit

# Abrir manualmente
# Navega a: http://localhost:8501
```

---

## 📊 Métricas de Calidad

- ✅ Tests unitarios ejecutables con `pytest tests/ -v`
- ✅ **5 estrategias** implementadas
- ✅ **2 interfaces** (CLI + Web)
- ✅ **Principios SOLID** aplicados
- ✅ **Inyección de dependencias** completa
- ✅ **Cobertura de casos**: soporte, recomendaciones, quejas, FAQ

### Métricas Operativas Disponibles

- ✅ Latencia promedio por interacción (`avg_response_time_ms`)
- ✅ Latencia p95 (`p95_response_time_ms`)
- ✅ Tasa de fallback a intención general (`fallback_rate_pct`)
- ✅ Accuracy de intención con muestras etiquetadas (`intent_accuracy_pct`)

---

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature: `git checkout -b feature/nueva-estrategia`
3. Commit: `git commit -m 'Agregar RefundStrategy'`
4. Push: `git push origin feature/nueva-estrategia`
5. Pull Request

---

## 📝 Recursos Adicionales

- [README.md](README.md) - Documentación completa
- [scripts/README.md](scripts/README.md) - Guía de scripts operativos
- [informes/GUIA_CREACION_INFORMES.md](informes/GUIA_CREACION_INFORMES.md) - Convención de informes
- [SOLID_ANALYSIS.md](SOLID_ANALYSIS.md) - Análisis de principios SOLID
- [tests/](tests/) - Ejemplos de testing con mocks

Lectura sugerida para onboarding:

1. [README.md](README.md)
2. [QUICKSTART.md](QUICKSTART.md)
3. [scripts/README.md](scripts/README.md)
4. [informes/GUIA_CREACION_INFORMES.md](informes/GUIA_CREACION_INFORMES.md)

---

## ⏱️ Tiempos Estimados

- **Setup inicial**: 5 minutos
- **Primer test**: 2 minutos
- **Entender arquitectura**: 15 minutos
- **Agregar nueva estrategia**: 30 minutos
- **Personalizar para tu caso**: 1-2 horas

---

**¿Preguntas?** Revisa el [README.md](README.md) completo o ejecuta `/ayuda` en la CLI.
