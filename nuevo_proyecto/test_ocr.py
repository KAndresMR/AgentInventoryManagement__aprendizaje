from agents.ocr_agent import extract_product_data

with open("durazno.jpeg", "rb") as f:
    img = f.read()

result = extract_product_data(img)
print(result)
