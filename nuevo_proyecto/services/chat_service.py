from services.llm_service import generate_response
from database.db import AsyncSessionLocal
from sqlalchemy import text


async def get_stock_from_db(product_name: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                """
                SELECT name, stock
                FROM products
                WHERE LOWER(name) LIKE :name
                LIMIT 1
            """
            ),
            {"name": f"%{product_name.lower()}%"},
        )

        row = result.fetchone()
        if row:
            return {"name": row[0], "stock": row[1]}
        return None


async def chat_with_agent(message: str):
    msg = message.lower()

    # palabras clave de stock
    keywords = ["stock", "hay", "cantidad", "disponible"]

    if any(k in msg for k in keywords):
        words = msg.split()

        for word in words:
            product = await get_stock_from_db(word)
            if product:
                return f"Sí, hay {product['stock']} unidades de {product['name']} en el inventario."

        return "No encontré ese producto en el inventario."

    # respuesta general con IA
    prompt = f"""
    Eres un asistente de inventario.
    Responde de forma clara y breve.

    Usuario: {message}
    """
    return generate_response(prompt)
