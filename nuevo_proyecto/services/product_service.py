from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.product import Product

class ProductService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_products(self):
        result = await self.session.execute(select(Product))
        return result.scalars().all()

    async def create_product(self, name: str, stock: int):
        product = Product(name=name, stock=stock)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
