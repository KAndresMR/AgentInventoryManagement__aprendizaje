from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product, ProductVariant, Stock

class ProductService:

    async def upsert_product(
        self,
        session: AsyncSession,
        name: str,
        sku: str,
        price: float,
        quantity: int
    ) -> Product:

        # Buscar producto
        result = await session.execute(
            select(Product).where(Product.name == name)
        )
        product = result.scalar_one_or_none()

        if not product:
            product = Product(name=name)
            session.add(product)
            await session.flush()

        # Buscar variante
        result = await session.execute(
            select(ProductVariant).where(ProductVariant.sku == sku)
        )
        variant = result.scalar_one_or_none()

        if not variant:
            variant = ProductVariant(
                sku=sku,
                price=price,
                product=product
            )
            session.add(variant)
            await session.flush()

            stock = Stock(
                quantity=quantity,
                variant=variant
            )
            session.add(stock)
        else:
            variant.price = price
            variant.stock.quantity = quantity

        await session.commit()
        return product

    async def list_products(self, session: AsyncSession):
        result = await session.execute(select(Product))
        return result.scalars().all()
