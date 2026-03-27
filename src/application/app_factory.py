"""
Factory de aplicacion.
Orquesta el wiring de dependencias para CLI y Streamlit desde un punto unico.
"""

from dataclasses import dataclass
from typing import Optional

from src.application.chat_service import ChatService
from src.core.interfaces import IDatabase, ILLMClient
from src.clients.openai_client import MockLLMClient, OpenAIClient
from src.factories.llm_provider_factory import LLMProviderFactory
from src.factories.strategy_factory import StrategyFactory
from src.infrastructure.database_sim import DatabaseSimulator


@dataclass
class AppComponents:
    """Contenedor con componentes ya construidos para ejecutar la aplicacion."""

    chat_service: ChatService
    database: IDatabase
    llm_client: ILLMClient
    provider_name: str


class AppFactory:
    """Construye la aplicacion completa respetando inyeccion de dependencias."""

    @staticmethod
    def create_components(provider: Optional[str] = None) -> AppComponents:
        """Crea y conecta cliente LLM, base de datos, strategy factory y chat service."""
        llm_client = LLMProviderFactory.create(provider)
        database = DatabaseSimulator()
        strategy_factory = StrategyFactory(llm_client, database)
        chat_service = ChatService(strategy_factory)

        provider_name = AppFactory._resolve_provider_name(llm_client)

        return AppComponents(
            chat_service=chat_service,
            database=database,
            llm_client=llm_client,
            provider_name=provider_name,
        )

    @staticmethod
    def _resolve_provider_name(llm_client: ILLMClient) -> str:
        """Normaliza el nombre del proveedor para UI y logging operacional."""
        if isinstance(llm_client, OpenAIClient):
            return "openai"
        if isinstance(llm_client, MockLLMClient):
            return "mock"

        # Fallback generico para proveedores nuevos registrados dinamicamente.
        return llm_client.__class__.__name__.replace("Client", "").lower()
