import strawberry
from typing import List, Optional
from domain.models import MOCK_PRODUCTS

@strawberry.type
class Stock:
    quantity: int
    available: bool

@strawberry.type
class Product:
    id: int
    name: str
    price: float
    stock: Stock

@strawberry.type
class Query:

    @strawberry.field
    def products(self, limit: int = 10, offset: int = 0) -> List[Product]:
        return MOCK_PRODUCTS[offset: offset + limit]

    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        for product in MOCK_PRODUCTS:
            if product.id == id:
                return product
        return None
