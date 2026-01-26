import asyncio
from services.search_service import SearchService

async def test():
    service = SearchService()

    result = await service.semanticSearch(
        "¿Tienen leche y pan y arroz?"
    )
    print(result)

asyncio.run(test())
