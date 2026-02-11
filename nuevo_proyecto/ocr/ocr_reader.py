from paddleocr import PaddleOCR
import numpy as np
import cv2
import re

# Inicializar OCR
ocr = PaddleOCR(lang="es", use_angle_cls=True)


def preprocess_image(image_bytes: bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return None

    # Aumentar resolución
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aumentar contraste
    alpha = 1.8
    beta = 20
    contrast = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # Umbral adaptativo
    thresh = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


def extract_text(image_bytes: bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return ""

    versiones = []

    # versión 1: imagen original
    versiones.append(img)

    # versión 2: escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    versiones.append(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))

    # versión 3: aumento de tamaño
    resized = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    versiones.append(resized)

    mejor_texto = ""
    mayor_longitud = 0

    for version in versiones:
        result = ocr.ocr(version)
        textos = []

        if result and result[0]:
            for linea in result[0]:
                texto = linea[1][0]
                confianza = linea[1][1]
                if confianza > 0.5:
                    textos.append(texto)

        texto_total = " ".join(textos).lower()
        texto_total = re.sub(r"[^a-z0-9\s\.\,\/\$]", " ", texto_total)

        if len(texto_total) > mayor_longitud:
            mayor_longitud = len(texto_total)
            mejor_texto = texto_total

    return mejor_texto
