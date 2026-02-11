from llm.llm_client import LLMClient
from services.product_service import ProductService
from rapidfuzz import process, fuzz


class SearchService:

    def __init__(self, llm_client: LLMClient, product_service: ProductService):
        self.llm_client = llm_client
        self.product_service = product_service

    # ======================================================
    # IA: identificar productos desde texto (con protección)
    # ======================================================
    async def identify_product(self, text: str):
        try:
            result = await self.llm_client.extract_entities(text)
            return result.get("products", [])
        except Exception as e:
            print("⚠️ IA no disponible:", e)
            return []

    # ======================================================
    # SEARCH INTELIGENTE
    # ======================================================
    async def semanticSearch(self, text: str):
        text = text.strip().lower()
        inventory = await self.product_service.list_products()

        # búsqueda directa sin IA
        direct_matches = [
            p.product_name for p in inventory if text in p.product_name.lower()
        ]

        if direct_matches:
            return {"products": direct_matches}

        # fallback con IA
        enriched_text = f"Producto de supermercado: {text}"
        products = await self.identify_product(enriched_text)

        if not products:
            return {"products": []}

        valid_products = []
        for prod in products:
            for p in inventory:
                if prod.lower() in p.product_name.lower():
                    valid_products.append(p.product_name)

        return {"products": list(set(valid_products))}

    # ======================================================
    # ASISTENTE CONVERSACIONAL
    # ======================================================
    async def ask_inventory(self, question: str):
        inventory = await self.product_service.list_products()
        question_lower = question.lower()

        # =========================
        # DETECTAR INTENCIÓN DE REGISTRO
        # =========================
        register_keywords = [
            "registrar producto",
            "agregar producto",
            "nuevo producto",
            "añadir producto",
            "crear producto",
        ]

        for kw in register_keywords:
            if kw in question_lower:
                return (
                    "📦 Perfecto. Vamos a registrar un producto.\n\n"
                    "Necesito tres imágenes:\n"
                    "1️⃣ Frontal → nombre y marca\n"
                    "2️⃣ Lateral izquierdo → ingredientes\n"
                    "3️⃣ Lateral derecho → información nutricional\n\n"
                    "Puedes subir las imágenes por el chat."
                )

        # =========================
        # CONSULTA GENERAL DE INVENTARIO
        # =========================
        inventory_keywords = [
            "inventario",
            "productos",
            "lista",
            "que tenemos",
            "qué tenemos",
            "mostrar inventario",
        ]

        if any(word in question_lower for word in inventory_keywords):
            if not inventory:
                return "El inventario se encuentra vacío."

            product_list = "\n".join(
                [
                    f"• {p.product_name}: {p.quantity_on_hand} unidades"
                    for p in inventory
                ]
            )

            prompt = f"""
    Eres un asistente profesional de inventario.

    El usuario pidió ver el inventario completo.

    Productos disponibles:
    {product_list}

    Responde de forma natural, clara y profesional.
    Incluye una recomendación general si detectas
    algún producto con bajo stock.
    """
            return await self.llm_client.generate_text(prompt)

        # =========================
        # BÚSQUEDA DE PRODUCTO ESPECÍFICO
        # =========================
        best_match = None

        # =========================
        # Detectar producto con IA
        # =========================
        detected_products = await self.identify_product(question_lower)

        if detected_products:
            detected_name = detected_products[0].lower()

            for p in inventory:
                if detected_name in p.product_name.lower():
                    best_match = p
                    break

        # =========================
        # Fuzzy match si no hay IA
        # =========================
        if not best_match:
            product_names = [p.product_name for p in inventory]
            match = process.extractOne(
                question_lower, product_names, scorer=fuzz.partial_ratio
            )

            if match and match[1] > 70:
                for p in inventory:
                    if p.product_name == match[0]:
                        best_match = p
                        break

        # ================================
        # SI ENCUENTRA PRODUCTO
        # ================================
        if best_match:
            stock = best_match.quantity_on_hand

            if stock == 0:
                status = "sin stock"
                recommendation = "Se recomienda realizar reposición inmediata."
            elif stock < 10:
                status = "stock bajo"
                recommendation = "Conviene abastecer este producto pronto."
            else:
                status = "stock adecuado"
                recommendation = "El nivel actual es suficiente."

            prompt = f"""
        Eres un asistente profesional de inventario.

        Producto consultado: {best_match.product_name}
        Stock actual: {stock} unidades
        Estado: {status}
        Recomendación: {recommendation}

        Responde de forma natural, clara y profesional al usuario.
        """
            return await self.llm_client.generate_text(prompt)

        # ================================
        # SUGERENCIAS
        # ================================
        suggestions = []

        for p in inventory:
            score = fuzz.partial_ratio(question_lower, p.product_name.lower())
            if score > 50:
                suggestions.append((p.product_name, p.quantity_on_hand, score))

        suggestions = sorted(suggestions, key=lambda x: x[2], reverse=True)

        if suggestions:
            suggestion_text = "\n".join(
                [f"• {name} ({stock} unidades)" for name, stock, _ in suggestions[:3]]
            )

            prompt = f"""
        Eres un asistente profesional de inventario.

        El usuario consultó un producto que no existe en el sistema.

        Producto solicitado:
        {question}

        Productos similares en inventario:
        {suggestion_text}

        Responde de forma natural, profesional y útil.
        Indica que el producto no existe y sugiere registrar uno nuevo.
        """

            return await self.llm_client.generate_text(prompt)

        # ================================
        # RESPUESTA CONVERSACIONAL
        # ================================
        prompt = f"""
    Eres un asistente inteligente de inventario.

    Responde de forma natural, amable y profesional.
    Siempre intenta redirigir la conversación
    hacia temas de inventario o productos.

    Mensaje del usuario:
    {question}
    """
        return await self.llm_client.generate_text(prompt)


# ======================================================
# FUNCIÓN AUXILIAR (fuera de la clase)
# ======================================================
async def find_similar_product(session, text: str):
    from services.product_service import ProductService

    service = ProductService(session)
    products = await service.list_products()

    if not products:
        return None

    product_names = [p.product_name for p in products]

    match = process.extractOne(text, product_names, scorer=fuzz.partial_ratio)

    if match and match[1] > 80:
        return match[0]

    return None
