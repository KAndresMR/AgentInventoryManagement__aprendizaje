import tensorflow as tf
import numpy as np
import json
import cv2

# Cargar modelo
model = tf.keras.models.load_model("product_classifier.h5")

# Cargar etiquetas
with open("labels.json", "r") as f:
    class_indices = json.load(f)

labels = {v: k for k, v in class_indices.items()}


def predict_product(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return "producto_desconocido", 0.0

    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img, verbose=0)
    class_id = np.argmax(preds)
    confidence = float(preds[0][class_id])

    product_name = labels[class_id]

    return product_name, confidence
