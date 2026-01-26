from domain.product_schemas import ProductSchema, StockSchema

MOCK_PRODUCTS = [
    ProductSchema(
        id=1,
        name="Laptop",
        price=1200.0,
        stock=StockSchema(quantity=10, available=True)
    ),
    ProductSchema(
        id=2,
        name="Mouse",
        price=25.5,
        stock=StockSchema(quantity=0, available=False)
    )
]
