def build_product_payload(normalized_data):
    return {
        "product_id": normalized_data["product_name"],
        "product_name": normalized_data["product_name"],
        "quantity_on_hand": 1,
    }
