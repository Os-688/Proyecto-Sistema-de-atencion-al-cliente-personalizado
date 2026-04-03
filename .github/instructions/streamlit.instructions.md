---
applyTo: "src/ui/**/*.py,app.py"
description: "Use when: debugging or fixing Streamlit UI code, handling session state, widgets, or rendering errors in the customer chatbot interface"
---

# Streamlit Configuration & Best Practices for Chatbot UI

## Project Context

This file guides development for the chatbot's Streamlit interface. The app uses:
- **Session state** to manage chat history, user context, and service instances
- **Tabs, sidebars, and containers** for layout organization
- **Real-time metric updates** for chat statistics
- **Error handling** for LLM client fallbacks and dependency injection

## Session State Management

### Initialization Pattern

```python
def initialize_session_state():
    """Inicializa el estado de la sesión una sola vez"""
    if 'chat_service' not in st.session_state:
        # Inyección de dependencias centralizada
        components = AppFactory.create_components()
        
        st.session_state.chat_service = components.chat_service
        st.session_state.database = components.database
        st.session_state.llm_provider = components.provider_name
        st.session_state.messages = []
        st.session_state.current_user_id = None
        st.session_state.total_conversations = 0
```

**Key Rules:**
- ✅ Always check `if 'key' not in st.session_state` before initializing
- ✅ Initialize service instances (AppFactory) in session state once
- ✅ Use session state for Chat history (`messages`), user selections, and counters
- ❌ Don't recreate AppFactory on every rerun—use dependency injection via session state
- ❌ Don't store large objects in session state unless they're cached

### Updating Session State

```python
# ✅ CORRECT: Direct modification
st.session_state.messages.append({"role": "user", "content": prompt})
st.session_state.total_conversations += 1

# ❌ WRONG: Trying to mutate before initialization
if prompt := st.chat_input(...):
    # Initialize first, then use
    initialize_session_state()
    st.session_state.messages.append(...)
```

## Widget Layout

### Sidebar Pattern

The sidebar should contain:
1. **User selector** (dropdown from database)
2. **Statistics** (metrics from chat service)
3. **Database info** (open tickets, FAQ count, categories)
4. **Controls** (buttons for clear history)
5. **API status** (provider name, mock vs real)

```python
def render_sidebar():
    """Renderiza controles y estadísticas en la barra lateral"""
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # 1. User selector with fallback
        customers = st.session_state.database.get_customers()
        customer_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in customers}
        customer_options["Sin usuario"] = None
        
        selected = st.selectbox("Selecciona un usuario:", list(customer_options.keys()))
        st.session_state.current_user_id = customer_options[selected]
        
        # 2. Stats from chat service
        stats = st.session_state.chat_service.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mensajes", stats['total_messages'])
        with col2:
            st.metric("Conversaciones", st.session_state.total_conversations)
        
        # 3. Clear history with rerun
        if st.button("🗑️ Limpiar Conversación"):
            st.session_state.chat_service.clear_history()
            st.session_state.messages = []
            st.rerun()
        
        # 4. Provider status
        provider = st.session_state.llm_provider
        if provider == "mock":
            st.warning("⚠️ Modo simulación activo")
        else:
            st.success(f"✅ {provider.upper()}")
```

**Key Points:**
- Always provide fallback/default options (e.g., "Sin usuario" = None)
- Use `.get_stats()` from service—don't duplicate logic
- Call `st.rerun()` after state changes that need UI refresh
- Show provider status for transparency

### Chat Tabs

Use `st.tabs()` for multi-view organization:

```python
def render_chat_interface():
    """Renderiza interfaz principal con tabs"""
    st.title("🤖 Chatbot de Atención al Cliente")
    
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Historial", "ℹ️ Info"])
    
    with tab1:
        render_chat_tab()
    with tab2:
        render_history_tab()
    with tab3:
        render_info_tab()
```

### Chat Tab Interaction Pattern

```python
def render_chat_tab():
    """Procesamiento de input y respuesta con gestión de errores"""
    # Display conversation history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Mostrar metadata si existe
                if "metadata" in message and message["metadata"]:
                    with st.expander("📊 Detalles"):
                        st.json(message["metadata"])
    
    # Input handler
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # 1. Add user message to state
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # 2. Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 3. Process response with error handling
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    response = st.session_state.chat_service.process_message(
                        user_input=prompt,
                        user_id=st.session_state.current_user_id
                    )
                    
                    # Display response
                    st.markdown(response.message)
                    
                    # Attach metadata
                    metadata = {
                        "intent": response.intent,
                        "confidence": f"{response.confidence:.2f}",
                        **response.metadata
                    }
                    
                    with st.expander("📊 Detalles"):
                        st.json(metadata)
                    
                    # Update session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.message,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    st.error(f"Error procesando mensaje: {str(e)}")
                    print(f"❌ Error: {e}")
        
        # 4. Update conversation counter and rerun
        st.session_state.total_conversations += 1
        st.rerun()
```

**Error Handling Rules:**
- ✅ Wrap `chat_service.process_message()` in try-except
- ✅ Show user-friendly error message with `st.error()`
- ✅ Log full error to console for debugging
- ❌ Don't let exceptions propagate uncaught
- ❌ Don't show raw stack traces to users

## Metadata Display

Always expose response metadata (intent, confidence, custom fields) in expanders:

```python
with st.expander("📊 Detalles"):
    st.json({
        "intent": response.intent,
        "confidence": f"{response.confidence:.2f}",
        "multi_intent": response.metadata.get("multi_intent", False),
        "intents_detected": response.metadata.get("intents_detected", []),
        **response.metadata
    })
```

This helps debug intent classification issues and builds transparency.

## Common Pitfalls

### ❌ Pitfall 1: Creating new AppFactory on every rerun

```python
# WRONG: This creates new instances every time user types
def main():
    components = AppFactory.create_components()  # ← RERUN EVERY TIME
    response = components.chat_service.process_message(user_input)
```

**Fix**: Store in session state once

```python
# CORRECT: Factory runs once, service is reused
def main():
    initialize_session_state()  # ← CHECKS IF ALREADY INITIALIZED
    response = st.session_state.chat_service.process_message(user_input)
```

### ❌ Pitfall 2: Not handling dropdown/widget changes

```python
# WRONG: User selection doesn't update state
selected = st.selectbox("Choose user", customer_list)
# selected value is local, never stored in session_state
```

**Fix**: Always update session state from widgets

```python
# CORRECT: Update session state after widget
customers = st.session_state.database.get_customers()
customer_options = {...}
selected = st.selectbox("Choose user", customer_options.keys())
st.session_state.current_user_id = customer_options[selected]  # ← UPDATE
```

### ❌ Pitfall 3: Not calling st.rerun() after state changes

```python
# WRONG: State updated but UI doesn't refresh
if st.button("Clear"):
    st.session_state.messages = []
    # Missing st.rerun()—messages still show old content
```

**Fix**: Call `st.rerun()` to trigger full re-execution from top

```python
# CORRECT: State updated and UI refreshes
if st.button("Clear"):
    st.session_state.messages = []
    st.rerun()  # ← Forces re-render
```

## Performance Optimization

### Use `@st.cache_data` for Static Data

```python
@st.cache_data
def load_customers():
    """Cache database lookups that rarely change"""
    return st.session_state.database.get_customers()

customers = load_customers()
```

### Use `st.chat_message()` Context Manager

```python
# ✅ CORRECT: Efficient chat bubbles
with st.chat_message("user"):
    st.markdown(message["content"])

# ❌ INEFFICIENT: Redrawing entire container
st.write(f"**User**: {message['content']}")
```

## Testing UI Changes

1. **Check session state initialization**: Verify `initialize_session_state()` runs once
2. **Verify user selection updates**: Select a user, check if `st.session_state.current_user_id` changes
3. **Test error handling**: Send invalid input, verify error message displays
4. **Check metadata display**: Inspect JSON metadata for intent/confidence
5. **Test rerun behavior**: Modify state, call `st.rerun()`, verify UI updates
6. **Profile performance**: Use `st.write(st.session_state)` to inspect state size

## File Structure

```
src/ui/
├── __init__.py
├── streamlit_ui.py          # Main entry point
├── cli_interface.py         # CLI alternative
└── components/
    ├── sidebar.py           # (Optional) Extract sidebar logic
    ├── chat_tab.py          # (Optional) Extract chat rendering
    └── history_tab.py       # (Optional) Extract history rendering

app.py                        # Streamlit entry point
```

For now, keep everything in `streamlit_ui.py`. Extract components only if file exceeds 500 lines.

## Debugging

Enable debug output:

```python
# In streamlit_ui.py
import streamlit as st

DEBUG = True

if DEBUG:
    st.write("**Debug: Session State**")
    st.write(st.session_state)
```

Check logs:
```bash
streamlit run app.py --logger.level=debug
```
