from llm.llm_client import LLMClient
from services.product_service import ProductService


class SearchService:

    def __init__(self, llm_client: LLMClient, product_service: ProductService):
        self.llm_client = llm_client
        self.product_service = product_service

    # =========================
    # IA (con manejo de errores)
    # =========================
    async def identify_product(self, text: str):
        """
        Extrae productos usando IA.
        Si la IA falla (cuota, error), devuelve lista vacía.
        """
        try:
            result = await self.llm_client.extract_entities(text)
            return result.get("products", [])
        except Exception as e:
            print("⚠️ IA no disponible:", e)
            return []

    # =========================
    # SEARCH INTELIGENTE
    # =========================
    async def semanticSearch(self, text: str):
        """
        1️⃣ Busca primero en BD (SIN IA)
        2️⃣ Solo si no hay match, usa IA
        """

        text = text.strip().lower()
        inventory = await self.product_service.list_products()

        # 1️⃣ BÚSQUEDA DIRECTA (GRATIS)
        direct_matches = [p.name for p in inventory if text in p.name.lower()]

        if direct_matches:
            return {"products": direct_matches}

        # 2️⃣ SOLO SI NO HAY MATCH → IA
        enriched_text = f"Producto de supermercado: {text}"
        products = await self.identify_product(enriched_text)

        if not products:
            return {"products": []}

        # 3️⃣ VALIDAR RESULTADOS IA
        valid = []
        for prod in products:
            for p in inventory:
                if prod.lower() in p.name.lower():
                    valid.append(p.name)

        return {"products": list(set(valid))}

    # =========================
    # PREGUNTAS DE INVENTARIO
    # =========================
    async def ask_inventory(self, question: str) -> str:
        inventory = await self.product_service.list_products()
        question_lower = question.lower()

        # 1️⃣ Intento directo sin IA
        for p in inventory:
            if p.name.lower() in question_lower:
                if p.stock > 0:
                    return f"✅ Sí, hay {p.name}. Stock: {p.stock}"
                else:
                    return f"⚠️ {p.name} está agotado."

        # 2️⃣ IA SOLO SI ES NECESARIO
        products = await self.identify_product(question)

        if not products:
            return "❌ No hay ese producto en el inventario."

        product_name = products[0].lower()

        for p in inventory:
            if product_name in p.name.lower():
                if p.stock > 0:
                    return f"✅ Sí, hay {p.name}. Stock: {p.stock}"
                else:
                    return f"⚠️ {p.name} está agotado."

        return f"❌ No hay {products[0]} en el inventario."
