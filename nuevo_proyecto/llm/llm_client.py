from google import genai
import os
import PIL.Image
import io
import json


class LLMClient:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "models/gemini-2.5-flash"

    async def extract_entities(self, prompt: str):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"""
Devuelve SOLO un JSON válido.
Formato:
{{"products": ["producto1", "producto2"]}}

Texto:
{prompt}
""",
            )
            return json.loads(response.text)
        except Exception as e:
            print("⚠️ Gemini error:", e)
            return {"products": []}

    async def analyze_image_and_recommend(self, image_bytes):
        img = PIL.Image.open(io.BytesIO(image_bytes))
        response = self.client.models.generate_content(
            model=self.model,
            contents=["Describe el producto de supermercado en la imagen", img],
        )
        return response.text
    
# --------------------------------------------
 
    async def generate_inventory_response(
        self, product_name: str, stock: int, question: str
    ):
        """
        Genera una respuesta en lenguaje natural basada en datos reales
        del inventario. La IA SOLO redacta, no inventa datos.
        """

        prompt = f"""
            Eres un asistente inteligente de inventario.

            Pregunta del usuario:
        "{question}"

        Datos reales del inventario:
        Producto: {product_name}
        Stock actual: {stock}

        Instrucciones:
        - Responde en español
        - Usa un tono natural y amigable
        - NO inventes datos
        - Si el stock es bajo (<=5), recomienda comprar más
        - Si el stock es suficiente, indícalo claramente
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip()

        except Exception as e:
            print("⚠️ Error generando respuesta IA:", e)
            return (
                f"El producto {product_name} tiene actualmente "
                f"{stock} unidades disponibles en el inventario."
            )
