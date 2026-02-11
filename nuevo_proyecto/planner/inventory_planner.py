from ocr.ocr_reader import extract_text
from agents.parser_agent import parse_product_data
from agents.verifier_agent import verify_product_data
from services.llm_service import extract_product_entities
from difflib import get_close_matches
from services.product_service import ProductService
from database.db import AsyncSessionLocal
import re


# IMPORTANTE:
# función async porque usa IA
async def run_inventory_pipeline(image_bytes, product_service=None):

    # =========================
    # 1. OCR
    # =========================
    raw_text = extract_text(image_bytes)

    size_match = re.search(r"(\d+(\.\d+)?)\s?(ml|l|g|kg)", raw_text.lower())
    regex_size = size_match.group(0) if size_match else None

    # =========================
    # 2. IA: marca + producto
    # =========================
    entities = await extract_product_entities(raw_text)

    brand = entities.get("marca", "desconocido")
    product_name = entities.get("nombre_producto", "producto_desconocido")

    # =========================
    # Limpieza simple del nombre
    # =========================
    if product_name and product_name != "producto_desconocido":
        words = product_name.split()
        product_name = " ".join(words[:2])  # máximo 2 palabras

    # =========================
    # 2.1 Corrección con base de datos
    # =========================
    async with AsyncSessionLocal() as session:
        product_service = ProductService(session)
        product_name = await product_service.correct_product_name(product_name)

    # =========================
    # Corrección por palabras clave
    # =========================
    async with AsyncSessionLocal() as session:
        product_service = ProductService(session)
        products = await product_service.list_products()

        detected_words = product_name.lower().split()

        best_match = None
        best_score = 0

        for p in products:
            db_words = p.product_name.lower().split()

            score = len(set(detected_words) & set(db_words))

            if score > best_score:
                best_score = score
                best_match = p.product_name

        if best_match and best_score > 0:
            product_name = best_match

    # =========================
    # NOMBRE FINAL (CLAVE)
    # =========================
    final_product_name = product_name

    print("RAW OCR:", raw_text)
    print("ENTITIES:", entities)
    print("---------------------------")

    # =========================
    # 3. Parser (para precio, fechas, etc.)
    # =========================
    parsed = parse_product_data(raw_text)

    size = parsed.get("size") or regex_size
    precio = parsed.get("precio")
    fecha_vencimiento = parsed.get("fecha_vencimiento")
    descripcion = parsed.get("descripcion")

    # =========================
    # 4. Verificación
    # =========================
    product_data = {
        "nombre": final_product_name,
        "size": size,
        "precio": precio,
        "fecha_vencimiento": fecha_vencimiento,
    }

    verification = verify_product_data(product_data)

    # =========================
    # 5. Respuesta: error
    # =========================
    if verification["status"] == "error":
        return {
            "status": "error",
            "message": "No se pudo detectar información suficiente del producto.",
            "raw_text": raw_text,
        }

    # =========================
    # 6. Respuesta: faltan datos
    # =========================
    if verification["status"] == "need_info":

        missing_fields = verification["missing"]
        missing_text = "\n".join([f"- {f}" for f in missing_fields])

        message = f"""
Detecté el producto: {product_name}.

Faltan los siguientes datos:
{missing_text}

Puedes:
1) Subir una foto donde se vea esa información
2) Escribir los datos aquí en el chat
3) Indicar si el producto no tiene ese campo
"""

        print("FINAL PRODUCT NAME:", final_product_name)
        print("FINAL SIZE:", size)

        return {
            "status": "need_info",
            "brand": brand,
            "product_name": final_product_name,
            "size": size,
            "missing": missing_fields,
            "message": message,
            "raw_text": raw_text,
        }

    # =========================
    # 7. Confirmación final
    # =========================
    print("NAME IN MESSAGE:", final_product_name)

    return {
        "status": "confirm",
        "brand": brand,
        "product_name": final_product_name,
        "size": size,
        "precio": precio,
        "fecha_vencimiento": fecha_vencimiento,
        "raw_text": raw_text,
    }
