from llm.llm_client import LLMClient
from services.product_service import ProductService


class SearchService:

    def __init__(self, llm_client: LLMClient, product_service: ProductService):
        self.llm_client = llm_client
        self.product_service = product_service

    # ======================================================
    # IA: identificar productos desde texto (con protección)
    # ======================================================
    async def identify_product(self, text: str):
        """
        Extrae productos desde texto usando IA.
        Si la IA falla (cuota, error), devuelve lista vacía.
        """
        try:
            result = await self.llm_client.extract_entities(text)
            return result.get("products", [])
        except Exception as e:
            print("⚠️ IA no disponible:", e)
            return []

    # ======================================================
    # SEARCH INTELIGENTE (para el buscador)
    # Devuelve SOLO nombres de productos detectados
    # ======================================================
    async def semanticSearch(self, text: str):
        """
        1️⃣ Busca primero en la base de datos (sin IA)
        2️⃣ Si no hay match, usa IA para detectar producto
        """

        text = text.strip().lower()
        inventory = await self.product_service.list_products()

        direct_matches = [
            p.name for p in inventory if text in p.name.lower()
        ]

        if direct_matches:
            return {"products": direct_matches}

        enriched_text = f"Producto de supermercado: {text}"
        products = await self.identify_product(enriched_text)

        if not products:
            return {"products": []}

        valid_products = []
        for prod in products:
            for p in inventory:
                if prod.lower() in p.name.lower():
                    valid_products.append(p.name)

        return {"products": list(set(valid_products))}

    # ======================================================
    # ASISTENTE CONVERSACIONAL DE INVENTARIO
    # Devuelve una RESPUESTA TIPO IA (string)
    # ======================================================
    async def ask_inventory(self, question: str) -> str:
        """
        Responde preguntas como:
        - ¿Hay arroz?
        - Stock de arroz
        - Todavía hay leche
        """

        inventory = await self.product_service.list_products()
        question_lower = question.lower()

        # 1️⃣ Intentar detectar producto SIN IA
        for p in inventory:
            if p.name.lower() in question_lower:
                # 👉 IA SOLO PARA REDACTAR
                return await self.llm_client.generate_inventory_response(
                    product_name=p.name,
                    stock=p.stock,
                    question=question
                )

        products = await self.identify_product(question)

        if not products:
            return "❌ No encontré ese producto en el inventario. ¿Deseas buscar otro?"

        detected = products[0].lower()

        for p in inventory:
            if detected in p.name.lower():
                return await self.llm_client.generate_inventory_response(
                    product_name=p.name,
                    stock=p.stock,
                    question=question
                )

        return f"❌ El producto {products[0]} no existe en el inventario."
