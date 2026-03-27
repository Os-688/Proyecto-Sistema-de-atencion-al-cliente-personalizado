"""
Factory de proveedores LLM.
Centraliza la creacion de clientes para evitar acoplar la UI a implementaciones concretas.
"""

from typing import Callable, Dict, List, Optional

from src.clients.openai_client import MockLLMClient, OpenAIClient
from src.core.config import Config
from src.core.interfaces import ILLMClient


class LLMProviderFactory:
    """Crea clientes LLM segun configuracion o proveedor explicitamente indicado."""

    _providers: Dict[str, Callable[[], ILLMClient]] = {
        "openai": OpenAIClient,
        "mock": MockLLMClient,
    }

    @classmethod
    def register_provider(cls, name: str, provider_builder: Callable[[], ILLMClient]) -> None:
        """Registra un proveedor nuevo sin modificar la logica de creacion (OCP)."""
        normalized_name = (name or "").strip().lower()
        if not normalized_name:
            raise ValueError("El nombre del proveedor no puede ser vacio")

        cls._providers[normalized_name] = provider_builder

    @classmethod
    def create(cls, provider: Optional[str] = None) -> ILLMClient:
        """
        Crea un cliente LLM.

        Precedencia:
        1. `provider` recibido como parametro.
        2. `Config.LLM_PROVIDER`.
        3. fallback a "mock" cuando no hay proveedor soportado o no hay API key para OpenAI.
        """
        selected_provider = (provider or Config.LLM_PROVIDER).strip().lower() or "openai"

        if selected_provider not in cls._providers:
            print(
                f"⚠️  Proveedor LLM '{selected_provider}' no soportado. "
                "Usando proveedor mock."
            )
            return cls._providers["mock"]()

        # Si el proveedor seleccionado requiere API key y no existe, degradar a mock.
        if selected_provider == "openai" and not Config.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY no configurada. Usando proveedor mock.")
            return cls._providers["mock"]()

        try:
            return cls._providers[selected_provider]()
        except Exception as exc:
            print(
                f"⚠️  No se pudo inicializar el proveedor '{selected_provider}': {exc}. "
                "Usando proveedor mock."
            )
            return cls._providers["mock"]()

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Retorna los proveedores registrados actualmente."""
        return list(cls._providers.keys())
