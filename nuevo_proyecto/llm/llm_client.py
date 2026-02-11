import httpx
import base64
from difflib import get_close_matches

KNOWN_PRODUCTS = [
    "ricacao",
    "coca cola",
    "avena",
    "nescafe",
    "tatos",
]

INVENTORY_SYSTEM_PROMPT = """
Eres un asistente inteligente de gestión de inventario para una empresa.

Tu función es:
- Registrar productos
- Consultar existencias
- Informar niveles de stock
- Dar recomendaciones de reposición
- Guiar al usuario en procesos del inventario

Reglas de comportamiento:

1. Responde siempre de forma:
   - Profesional
   - Clara
   - Breve
   - Conversacional

2. Si el usuario hace preguntas generales:
   - Responde amablemente
   - Redirige la conversación al inventario

3. Si un producto tiene:
   - 0 unidades → indicar que no hay stock y recomendar reposición
   - menos de 10 unidades → indicar stock bajo y recomendar abastecimiento
   - más de 10 unidades → indicar stock adecuado

4. Nunca respondas de forma robótica o técnica.
5. Habla como un asistente empresarial real.
6. Siempre responde en español.
"""


class LLMClient:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "mistral"

    # =========================
    # Método interno para llamar a Ollama
    # =========================
    async def _call_ollama(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60,
                )
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            print("Error Ollama:", e)
            return "⚠️ Error en la IA."

    # =========================
    # Extraer productos desde texto
    # =========================
    async def extract_entities(self, prompt: str):
        ia_prompt = f"""
Devuelve SOLO un JSON válido con formato:
{{"products": ["producto1"]}}

Texto:
{prompt}
"""
        response = await self._call_ollama(ia_prompt)

        try:
            import json

            return json.loads(response)
        except Exception:
            return {"products": []}

    # =========================
    # Analizar imagen (solo nombre)
    # =========================
    async def analyze_image_and_recommend(self, image_bytes):
        img_b64 = base64.b64encode(image_bytes).decode()

        prompt = f"""
La siguiente imagen es un producto.

Indica solo el nombre del producto.
Ejemplos:
Coca Cola
Arroz
Galletas

Imagen en base64:
{img_b64}
"""

        return await self._call_ollama(prompt)

    # =========================
    # Respuesta de inventario
    # =========================
    async def generate_inventory_response(
        self, product_name: str, stock: int, question: str
    ):
        prompt = f"""
    Consulta del usuario:
    {question}

    Producto: {product_name}
    Stock actual: {stock} unidades

    Genera una respuesta profesional:
    - Indica el estado del stock
    - Da una recomendación si es necesario
    """
        return await self.generate_text(prompt)

    # =========================
    # Texto general del agente
    # =========================
    async def generate_text(self, prompt: str) -> str:
        final_prompt = f"""
    {INVENTORY_SYSTEM_PROMPT}

    Instrucción del sistema:
    Responde al usuario siguiendo las reglas del asistente.

    Mensaje o contexto:
    {prompt}
    """
        return await self._call_ollama(final_prompt)

    # =========================
    # LIMPIAR NOMBRE DE PRODUCTO
    # =========================
    async def extract_product_entities(self, raw_text: str) -> dict:
        """
        Extrae marca y nombre del producto usando IA.
        Devuelve un JSON con:
        {
            "marca": "...",
            "nombre_producto": "..."
        }
        """

        prompt = f"""
    Eres un agente inteligente de inventario.

    Debes analizar el siguiente texto detectado por OCR
    y extraer dos campos:

    - marca: empresa fabricante
    - nombre_producto: nombre comercial del producto

    Reglas:
    - No inventes productos.
    - Si no puedes detectar un campo, usa "desconocido".
    - Devuelve SOLO un JSON válido.
    - Sin explicaciones.

    Ejemplo:

    Texto:
    "Nestle Ricacao mezcla en polvo con vitaminas"

    Respuesta:
    {{
    "marca": "Nestle",
    "nombre_producto": "Ricacao"
    }}

    Texto OCR:
    {raw_text}
    """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "mistral:latest",
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60,
                )

                data = response.json()
                text = data.get("response", "").strip()

                # Intentar convertir a JSON
                import json

                return json.loads(text)

        except Exception as e:
            print("Error extrayendo entidades:", e)
            return {
                "marca": "desconocido",
                "nombre_producto": "producto_desconocido",
            }
