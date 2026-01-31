import strawberry
import base64
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from database.db import AsyncSessionLocal, engine, Base
from services.product_service import ProductService
from services.search_service import SearchService
from llm.llm_client import LLMClient


# =========================
# GraphQL Types
# =========================
@strawberry.type
class ProductType:
    id: int
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
            return [ProductType(id=p.id, name=p.name, stock=p.stock) for p in products]

    @strawberry.field
    async def searchIntelligent(self, query: str) -> list[str]:
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)
            search_service = SearchService(llm, product_service)

            result = await search_service.semanticSearch(query)
            return result.get("products", [])

    @strawberry.field
    async def askInventory(self, question: str) -> str:
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)
            search_service = SearchService(llm, product_service)

            return await search_service.ask_inventory(question)


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

            return ProductType(id=product.id, name=product.name, stock=product.stock)

    @strawberry.mutation
    async def analyzeImage(self, image: str) -> str:
        llm = LLMClient()
        image_bytes = base64.b64decode(image)
        return await llm.analyze_image_and_recommend(image_bytes)

    @strawberry.mutation
    async def detectProductFromImage(self, image: str) -> str:
        async with AsyncSessionLocal() as session:
            llm = LLMClient()
            product_service = ProductService(session)

            try:
                image_bytes = base64.b64decode(image)
                description = await llm.analyze_image_and_recommend(image_bytes)
            except Exception:
                return "⚠️ Error al analizar la imagen (límite de la IA)."

            if not description:
                return "❌ No se pudo analizar la imagen."

            # Extraer producto desde texto
            result = await llm.extract_entities(description)
            products = result.get("products", [])

            inventory = await product_service.list_products()

            # 1️⃣ Comparación directa por IA
            if products:
                detected = products[0].lower()
                for p in inventory:
                    if detected in p.name.lower():
                        return (
                            f"📸 Producto detectado: {p.name}\n"
                            f"✅ Existe en inventario (stock: {p.stock})"
                        )

            # 2️⃣ Fallback sin IA (texto libre)
            desc_lower = description.lower()
            for p in inventory:
                if p.name.lower() in desc_lower:
                    return (
                        f"📸 Producto detectado: {p.name}\n"
                        f"✅ Existe en inventario (stock: {p.stock})"
                    )

            return "📸 Imagen analizada.\n" "❌ El producto no existe en el inventario."


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
