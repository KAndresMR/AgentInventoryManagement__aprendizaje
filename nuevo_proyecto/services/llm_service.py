from llm.llm_client import LLMClient

llm = LLMClient()


# =========================
# Generar respuesta del agente
# =========================
async def generate_response(prompt: str) -> str:
    return await llm.generate_text(prompt)


# =========================
# Extraer marca y producto
# =========================
async def extract_product_entities(raw_text: str) -> dict:
    return await llm.extract_product_entities(raw_text)
