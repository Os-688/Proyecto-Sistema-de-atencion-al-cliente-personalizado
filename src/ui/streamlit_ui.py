"""Interfaz Streamlit para el chatbot de atención al cliente."""

from datetime import datetime

import streamlit as st

from src.application.app_factory import AppFactory


def _apply_custom_theme() -> None:
    """Aplica ajustes visuales complementarios al tema configurado en .streamlit/config.toml."""
    # Este CSS solo ajusta detalles visuales; la paleta base vive en .streamlit/config.toml.
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top left, #f7fcff 0%, #eef7fc 40%, #e7f2f9 100%);
        }
        [data-testid="stSidebar"] {
            border-right: 2px solid #0057A8;
        }
        [data-testid="metric-container"] {
            border-left: 4px solid #0057A8;
            border-radius: 10px;
            box-shadow: 0 1px 8px rgba(0, 87, 168, 0.12);
        }
        .stChatMessage {
            border-radius: 12px;
            border: 1px solid rgba(0, 87, 168, 0.12);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Inicializa dependencias y estado UI una sola vez por sesión."""
    # Streamlit re-ejecuta el script en cada interacción, por eso protegemos el wiring aquí.
    if "chat_service" in st.session_state:
        return

    try:
        # Punto único de inyección de dependencias para mantener la UI desacoplada.
        components = AppFactory.create_components()
        st.session_state.chat_service = components.chat_service
        st.session_state.database = components.database
        st.session_state.llm_provider = components.provider_name
        st.session_state.messages = []
        st.session_state.current_user_id = None
        st.session_state.total_conversations = 0
    except Exception as exc:
        st.error(f"No se pudo inicializar la aplicación: {exc}")
        st.stop()


def render_sidebar() -> None:
    """Renderiza configuración, estado operacional y métricas de sesión."""
    with st.sidebar:
        st.title("Configuración")
        st.subheader("Usuario Simulado")

        try:
            customers = st.session_state.database.get_customers()
            customer_options = {"Sin usuario": None}
            customer_options.update({f"{c['name']} (ID: {c['id']})": c["id"] for c in customers})

            selected_customer = st.selectbox(
                "Selecciona un usuario:",
                options=list(customer_options.keys()),
                index=0,
                key="selected_customer",
            )
            st.session_state.current_user_id = customer_options[selected_customer]
        except Exception as exc:
            st.error(f"Error al cargar usuarios: {exc}")

        st.subheader("Estadísticas")
        try:
            # Métricas provienen del servicio de aplicación para evitar duplicar reglas en la UI.
            stats = st.session_state.chat_service.get_stats()
            db_stats = st.session_state.database.get_stats()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mensajes", stats.get("total_messages", 0))
                st.metric("Clientes", db_stats.get("total_customers", 0))
            with col2:
                st.metric("Conversaciones", st.session_state.total_conversations)
                st.metric("Productos", db_stats.get("total_products", 0))

            st.subheader("Base de Datos")
            st.info(
                "\n".join(
                    [
                        f"Tickets abiertos: {db_stats.get('open_tickets', 0)}",
                        f"FAQ disponibles: {db_stats.get('total_faq', 0)}",
                        f"Categorias: {', '.join(db_stats.get('product_categories', []))}",
                    ]
                )
            )
        except Exception as exc:
            st.warning(f"No se pudieron cargar métricas: {exc}")

        st.subheader("Controles")
        if st.button("Limpiar Conversación", use_container_width=True):
            st.session_state.chat_service.clear_history()
            st.session_state.messages = []
            st.session_state.total_conversations = 0
            st.rerun()

        st.subheader("Estado API")
        provider = st.session_state.get("llm_provider", "desconocido")
        if provider == "mock":
            st.warning("Modo simulación activo")
        else:
            st.success(f"Proveedor activo: {provider}")


def render_chat_tab() -> None:
    """Renderiza mensajes del chat y maneja nuevos envíos."""
    # Rehidratamos toda la conversación en cada rerun para mantener la UI determinística.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("metadata"):
                with st.expander("Detalles"):
                    st.json(message["metadata"])

    prompt = st.chat_input("Escribe tu mensaje aquí...")
    if not prompt:
        return

    # Guardamos primero el mensaje del usuario para persistencia si falla el procesamiento.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat(),
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # El único punto de orquestación de negocio está en ChatService.
                response = st.session_state.chat_service.process_message(
                    user_input=prompt,
                    user_id=st.session_state.current_user_id,
                )

                metadata = {
                    "intent": response.intent,
                    "confidence": f"{response.confidence:.2f}",
                    **(response.metadata or {}),
                }

                st.markdown(response.message)
                with st.expander("Detalles"):
                    # Exponer metadata ayuda a depurar intent-classification sin logs adicionales.
                    st.json(metadata)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response.message,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                st.session_state.total_conversations += 1
            except Exception as exc:
                # Degradación elegante: el usuario recibe feedback y el flujo no se rompe.
                st.error(f"Ocurrió un error procesando tu mensaje: {exc}")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "Lo siento, hubo un error temporal. Intenta nuevamente.",
                        "metadata": {"error": str(exc)},
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    # Forzamos rerun para que el historial y métricas se refresquen en la misma interacción.
    st.rerun()


def render_history_tab() -> None:
    """Renderiza historial resumido de mensajes."""
    st.subheader("Historial de Conversación")

    if not st.session_state.messages:
        st.info("No hay mensajes en el historial aún. Comienza una conversación.")
        return

    for msg in st.session_state.messages:
        col1, col2, col3 = st.columns([1, 5, 2])

        with col1:
            st.markdown("### 👤" if msg["role"] == "user" else "### 🤖")

        with col2:
            preview = msg["content"]
            st.markdown(f"**{preview[:120]}...**" if len(preview) > 120 else f"**{preview}**")
            if msg.get("metadata"):
                st.caption(f"Intención: {msg['metadata'].get('intent', 'N/A')}")

        with col3:
            timestamp = msg.get("timestamp")
            if timestamp:
                try:
                    st.caption(datetime.fromisoformat(timestamp).strftime("%H:%M:%S"))
                except ValueError:
                    st.caption("N/A")

        st.divider()


def render_info_tab() -> None:
    """Renderiza información del sistema y ejemplos de uso."""
    st.subheader("Información del Sistema")
    st.markdown(
        """
### Capacidades del Chatbot

- Soporte técnico y resolución de incidencias
- Recomendaciones de productos con catálogo
- Gestión de quejas y feedback
- Respuestas a preguntas frecuentes

### Arquitectura

La app respeta principios SOLID con inyección de dependencias vía AppFactory.
"""
    )

    with st.expander("Ejemplos de Consultas"):
        st.markdown(
            """
- "No puedo iniciar sesión en mi cuenta"
- "Busco una laptop para diseño gráfico"
- "El producto llegó dañado"
- "¿Cómo cambio mi contraseña?"
"""
        )


def render_chat_interface() -> None:
    """Renderiza la vista principal con tabs."""
    st.title("Chatbot de Atención al Cliente")
    # Tabs separan vistas sin partir estado ni crear rutas adicionales.
    tab1, tab2, tab3 = st.tabs(["Chat", "Historial", "Info"])

    with tab1:
        render_chat_tab()
    with tab2:
        render_history_tab()
    with tab3:
        render_info_tab()


def main() -> None:
    """Función principal de la aplicación Streamlit."""
    # Debe ser la primera llamada a Streamlit para evitar errores de configuración de página.
    st.set_page_config(
        page_title="Chatbot Atención al Cliente",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _apply_custom_theme()
    # Orden intencional: tema -> estado -> sidebar -> vista principal.
    # Esto evita estados parcialmente inicializados en reruns tempranos.
    initialize_session_state()
    render_sidebar()
    render_chat_interface()

    st.markdown("---")
    st.caption("Sistema de Atención al Cliente Automatizado | Proyecto LLM 2026")


if __name__ == "__main__":
    main()
