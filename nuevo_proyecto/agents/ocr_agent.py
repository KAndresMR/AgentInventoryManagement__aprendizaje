from ocr.ocr_reader import extract_text
from agents.parser_agent import parse_product_data


def extract_product_data(image_bytes):
    text = extract_text(image_bytes)

    print("OCR detectó:")
    print(text)

    data = parse_product_data(text)

    return {
        "product_name": data["nombre"],
        "size": data["size"],
        "raw_text": text,
    }
