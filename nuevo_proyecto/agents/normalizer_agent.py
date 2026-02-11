def normalize_product_data(data):
    nombre = data.get("nombre", "producto_desconocido")
    size = data.get("size")

    # Normalización básica
    if size:
        size = size.replace(" ", "")

    return {"product_name": nombre, "size": size}
