from pydantic import BaseModel

class StockSchema(BaseModel):
    quantity: int
    available: bool

class ProductSchema(BaseModel):
    id: int
    name: str
    price: float
    stock: StockSchema
