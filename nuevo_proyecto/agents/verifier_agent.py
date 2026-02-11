def verify_product_data(data: dict):

    required_fields = {
        "nombre": "Nombre del producto",
        "size": "Tamaño",
        "precio": "Precio",
        "fecha_vencimiento": "Fecha de vencimiento",
    }

    missing = []

    for key, label in required_fields.items():
        value = data.get(key)
        if not value or value in ["producto_desconocido", "no_detectado"]:
            missing.append(label)

    if len(missing) == len(required_fields):
        return {
            "status": "error",
            "missing": missing,
        }

    if missing:
        return {
            "status": "need_info",
            "missing": missing,
        }

    return {
        "status": "complete",
        "missing": [],
    }
