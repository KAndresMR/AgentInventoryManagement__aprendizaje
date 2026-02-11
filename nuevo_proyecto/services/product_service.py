from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.product_stock import ProductStock
from models.product_image import ProductImage
import uuid
import os
import base64
from difflib import get_close_matches


class ProductService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_products(self):
        result = await self.session.execute(select(ProductStock))
        return result.scalars().all()

    async def create_product(self, name: str, stock: int):
        product = ProductStock(
            product_id=name.lower().replace(" ", "_"),
            product_name=name,
            quantity_on_hand=stock,
            quantity_reserved=0,
            quantity_available=stock,
            minimum_stock_level=10,
            reorder_point=20,
            optimal_stock_level=100,
            supplier_id="SUP-001",
            supplier_name="Proveedor Demo",
        )

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def create_product_with_image(
        self,
        name: str,
        stock: int,
        image_b64: str,
        brand: str | None = None,
        size: str | None = None,
        price=None,
        expiration_date=None,
    ):
        # Crear producto
        product = ProductStock(
            product_id=name.lower().replace(" ", "_"),
            product_name=name,
            brand=brand,
            size=size,
            price=price,
            expiration_date=expiration_date,
            quantity_on_hand=stock,
            quantity_reserved=0,
            quantity_available=stock,
            minimum_stock_level=10,
            reorder_point=20,
            optimal_stock_level=100,
            supplier_id="SUP-001",
            supplier_name="Proveedor Demo",
        )

        self.session.add(product)
        await self.session.flush()  # obtener ID sin commit

        # Guardar imagen
        os.makedirs("product_images", exist_ok=True)
        filename = f"product_images/{product.id}.jpg"

        with open(filename, "wb") as f:
            f.write(base64.b64decode(image_b64))

        # Registrar imagen
        image = ProductImage(
            product_stock_id=product.id,
            image_path=filename,
        )

        self.session.add(image)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def find_closest_product_name(self, detected_name: str) -> str:
        """
        Busca el nombre más parecido en la base de datos.
        Si no encuentra coincidencias, devuelve el nombre original.
        """
        result = await self.session.execute(select(ProductStock))
        products = result.scalars().all()

        product_names = [p.product_name.lower() for p in products]

        match = get_close_matches(
            detected_name.lower(),
            product_names,
            n=1,
            cutoff=0.6,
        )

        if match:
            return match[0].capitalize()

        return detected_name

    async def correct_product_name(self, detected_name: str) -> str:
        """
        Corrige el nombre del producto usando coincidencias con la base de datos.
        No rompe el flujo actual.
        """

        if not detected_name or detected_name == "producto_desconocido":
            return detected_name

        products = await self.list_products()

        if not products:
            return detected_name

        db_names = [p.product_name for p in products]

        # buscar coincidencia por similitud
        match = get_close_matches(
            detected_name,
            db_names,
            n=1,
            cutoff=0.6,  # nivel de similitud
        )

        if match:
            return match[0]  # nombre oficial de la BD

        return detected_name
