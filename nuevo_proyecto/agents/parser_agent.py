import re


def parse_product_data(text: str) -> dict:
    text = text.lower()

    # Tamaño
    size_match = re.search(r"(\d+(\.\d+)?)\s?(ml|l|g|kg)", text)
    size = size_match.group(0) if size_match else None

    # Precio
    price_match = re.search(r"(pvp[:\s]*)?\$?\s?(\d+(\.\d{1,2})?)", text)
    precio = price_match.group(2) if price_match else None

    # Fecha fabricación
    fab_match = re.search(r"f[:\s]*(\d{4}/\d{2}/\d{2})", text)
    fecha_fabricacion = fab_match.group(1) if fab_match else None

    # Fecha vencimiento
    ven_match = re.search(r"v[:\s]*(\d{4}/\d{2}/\d{2})", text)
    fecha_vencimiento = ven_match.group(1) if ven_match else None

    return {
        "size": size,
        "precio": precio,
        "fecha_fabricacion": fecha_fabricacion,
        "fecha_vencimiento": fecha_vencimiento,
    }
