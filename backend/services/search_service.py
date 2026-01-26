from llm.llm_client import LLMClient

# Feature flag: activar/desactivar LLM
LLM_ENABLED = False


class SearchService:
    """
    Servicio inteligente de búsqueda semántica.
    Implementa multilabel (máx. 3 productos) con fallback sin LLM.
    """

    def __init__(self):
        self.llm = LLMClient()

    async def semanticSearch(self, query: str) -> dict:
        """
        Punto de entrada principal del servicio.
        """
        if LLM_ENABLED:
            return await self.llm.extract_products(query)

        # Fallback sin LLM
        return self._fallback_search(query)

    def _fallback_search(self, query: str) -> dict:
        """
        Búsqueda simple basada en reglas.
        No es semántica, pero garantiza funcionamiento sin LLM.
        """

        stopwords = {
            "y", "o", "de", "la", "el", "los", "las",
            "un", "una", "¿tienen", "tienen", "hay",
            "me", "pueden", "por", "favor"
        }

        words = (
            query.lower()
            .replace("¿", "")
            .replace("?", "")
            .split()
        )

        products = []

        for w in words:
            if w not in stopwords and w not in products:
                products.append(w)

            if len(products) == 3:
                break

        return {
            "products": products
        }
