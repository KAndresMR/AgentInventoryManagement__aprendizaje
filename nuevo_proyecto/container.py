from aioinject import Container, Singleton, Scoped
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from services.product_service import ProductService
from services.search_service import SearchService
from llm.llm_client import LLMClient


#  FUNCIÓN SÍNCRONA (NO async, NO yield)
def get_session() -> AsyncSession:
    return AsyncSessionLocal()


def create_container() -> Container:
    container = Container()

    #  ESTA LÍNEA ES LA CLAVE DE TODO
    container.register(Scoped(get_session, provides=AsyncSession))

    # Servicios
    container.register(Singleton(LLMClient))
    container.register(Scoped(ProductService))
    container.register(Scoped(SearchService))

    return container
