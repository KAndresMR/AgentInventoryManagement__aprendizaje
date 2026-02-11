import strawberry
import base64
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from planner.inventory_planner import run_inventory_pipeline
from database.db import AsyncSessionLocal, engine, Base
from services.product_service import ProductService
from services.search_service import SearchService
from llm.llm_client import LLMClient
import re

LAST_DETECTED_PRODUCT = {}


# =========================
# GraphQL Types
# =========================
@strawberry.type
class ProductType:
    id: str
    name: str
    stock: int


# =========================
# Queries
# =========================
@strawberry.type
class Query:

    @strawberry.field
    async def products(self) -> list[ProductType]:
        async with AsyncSessionLocal() as session:
            service = ProductService(session)
            products = await service.list_products()
            return [
                ProductType(
                    id=str(p.id),
                    name=p.product_name,
                    stock=p.quantity_on_hand,
                )
                for p in products
            ]

    @strawberry.field
    async def searchIntelligent(self, query: str) -> str:
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)
            search_service = SearchService(llm, product_service)

            result = await search_service.semanticSearch(query)
            products = result.get("products", [])

            if not products:
                return "❌ No encontré productos relacionados en el inventario."

            inventory = await product_service.list_products()
            for p in inventory:
                if p.product_name.lower() == products[0].lower():
                    return await llm.generate_inventory_response(
                        product_name=p.product_name,
                        stock=p.quantity_on_hand,
                        question=query,
                    )

            return "❌ El producto fue detectado, pero no existe en el inventario."

    @strawberry.field
    async def askInventory(self, question: str) -> str:
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)
            search_service = SearchService(llm, product_service)

            return await search_service.ask_inventory(question)

    @strawberry.field
    async def productById(self, id: str) -> ProductType | None:
        async with AsyncSessionLocal() as session:
            service = ProductService(session)
            product = await service.get_product_by_id(id)

            if not product:
                return None

            return ProductType(
                id=str(product.id),
                name=product.product_name,
                stock=product.quantity_on_hand,
            )


# =========================
# Mutations
# =========================
@strawberry.type
class Mutation:

    @strawberry.mutation
    async def addProduct(self, name: str, stock: int) -> ProductType:
        async with AsyncSessionLocal() as session:
            service = ProductService(session)
            product = await service.create_product(name, stock)

            return ProductType(
                id=str(product.id),
                name=product.product_name,
                stock=product.quantity_on_hand,
            )

    @strawberry.mutation
    async def analyzeImage(self, image: str) -> str:
        llm = LLMClient()
        image_bytes = base64.b64decode(image)
        return await llm.analyze_image_and_recommend(image_bytes)

    @strawberry.mutation
    async def detectProductFromImage(self, image: str) -> str:
        global LAST_DETECTED_PRODUCT
        async with AsyncSessionLocal() as session:
            product_service = ProductService(session)

            image_bytes = base64.b64decode(image)

            # ejecutar pipeline
            result = await run_inventory_pipeline(image_bytes, product_service)
            

            status = result["status"]
            raw_text = result.get("raw_text", "")

            if status == "error":
                return (
                    f"⚠️ {result['message']}\n\n"
                    f"🧾 Texto detectado por OCR:\n{raw_text}"
                )

            if status in ["need_info", "confirm"]:

                

                LAST_DETECTED_PRODUCT = {
                    "name": result["product_name"],
                    "brand": result.get("brand"),
                    "size": result.get("size"),
                    "price": result.get("precio"),
                    "expiration_date": result.get("fecha_vencimiento"),
                    "image": image,
                }

                summary = f"""
            📦 Producto detectado:

            Marca: {LAST_DETECTED_PRODUCT.get("brand", "No detectada")}
            Nombre: {LAST_DETECTED_PRODUCT.get("name")}
            Tamaño: {LAST_DETECTED_PRODUCT.get("size", "No detectado")}
            Precio: {LAST_DETECTED_PRODUCT.get("price", "No detectado")}
            Fecha de vencimiento: {LAST_DETECTED_PRODUCT.get("expiration_date", "No detectada")}
            """

                return (
                    summary
                    + """
                Revisa la información detectada.

                Si deseas actualizar algún campo, puedes escribir por ejemplo:
                - precio 1.25
                - vence 2026-08-01
                - tamaño 600g

                Cuando todo esté correcto, escribe:
                👉 guardar producto
                """
                )

    @strawberry.mutation
    async def replyToAgent(self, message: str) -> str:
        global LAST_DETECTED_PRODUCT
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)
            search_service = SearchService(llm, product_service)

            msg = message.lower()

            # =========================
            # SALUDO
            # =========================
            if msg in [
                "hola",
                "buenas",
                "buenos dias",
                "buenas tardes",
                "como estas",
                "qué tal",
            ]:
                prompt = """
    Eres un asistente profesional de inventario.

    Saluda de forma breve, natural y profesional.
    Indica que puedes ayudar a registrar productos
    o consultar el inventario.
    """
                return await llm.generate_text(prompt)

            # =========================
            # INTENCIÓN: REGISTRAR PRODUCTO
            # =========================
            if any(word in msg for word in ["registrar", "agregar", "nuevo producto"]):
                prompt = """
    Eres un asistente inteligente de inventario.

    El usuario quiere registrar un producto nuevo.

    Explícale de forma clara y profesional cómo hacerlo.
    Debes pedirle exactamente estas 3 fotos:

    1) Foto frontal → nombre y marca del producto
    2) Lateral izquierdo → ingredientes
    3) Lateral derecho → tabla nutricional
    """
                return await llm.generate_text(prompt)

            # =========================
            # ACTUALIZAR DATOS DEL PRODUCTO DETECTADO
            # =========================

            if LAST_DETECTED_PRODUCT:

                # actualizar precio
                price_match = re.search(r"precio\s+(\d+(\.\d+)?)", msg)
                if price_match:
                    LAST_DETECTED_PRODUCT["price"] = price_match.group(1)
                    return f"✅ Precio actualizado a {price_match.group(1)}"

                # actualizar fecha de vencimiento
                date_match = re.search(r"venc[e]?\s+(\d{4}-\d{2}-\d{2})", msg)
                if date_match:
                    LAST_DETECTED_PRODUCT["expiration_date"] = date_match.group(1)
                    return (
                        f"✅ Fecha de vencimiento actualizada a {date_match.group(1)}"
                    )

                # actualizar tamaño
                size_match = re.search(r"tamañ?o\s+(\d+\s?(g|kg|ml|l))", msg)
                if size_match:
                    LAST_DETECTED_PRODUCT["size"] = size_match.group(1)
                    return f"✅ Tamaño actualizado a {size_match.group(1)}"

            # =========================
            # CONFIRMAR GUARDADO DEL PRODUCTO
            # =========================
            if "guardar producto" in msg or "listo" in msg:

               

                if not LAST_DETECTED_PRODUCT:
                    return "No hay ningún producto pendiente para guardar."

                product = await product_service.create_product_with_image(
                    name=LAST_DETECTED_PRODUCT["name"],
                    stock=1,
                    image_b64=LAST_DETECTED_PRODUCT["image"],
                    brand=LAST_DETECTED_PRODUCT.get("brand"),
                    size=LAST_DETECTED_PRODUCT.get("size"),
                    price=LAST_DETECTED_PRODUCT.get("price"),
                    expiration_date=LAST_DETECTED_PRODUCT.get("expiration_date"),
                )

                LAST_DETECTED_PRODUCT = {}

                return (
                    f"✅ Producto registrado correctamente:\n" f"{product.product_name}"
                )

            # =========================
            # CONSULTAS DE INVENTARIO (INTELIGENTES)
            # =========================
            if any(
                word in msg
                for word in [
                    "tenemos",
                    "hay",
                    "stock",
                    "disponible",
                    "inventario",
                    "productos",
                    "lista",
                ]
            ):
                # AQUÍ se usa el search_service
                return await search_service.ask_inventory(message)

            # =========================
            # RESPUESTA GENERAL DEL AGENTE
            # =========================
            prompt = f"""
    Eres un asistente profesional de inventario.

    Tu función es:
    - Ayudar a registrar productos
    - Consultar stock
    - Responder preguntas sobre inventario

    Siempre orienta la conversación hacia el inventario.

    Pregunta del usuario:
    {message}

    Responde de forma breve, clara y profesional.
    """
            return await llm.generate_text(prompt)


# =========================
# App
# =========================
schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")


# =========================
# Startup
# =========================
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
