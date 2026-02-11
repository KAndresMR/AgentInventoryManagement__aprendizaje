import cv2
import os
import numpy as np
from PIL import Image
import io


DATASET_PATH = "imagenes_productos"


def load_dataset_features():
    features = {}

    orb = cv2.ORB_create()

    for product_name in os.listdir(DATASET_PATH):
        product_path = os.path.join(DATASET_PATH, product_name)

        if not os.path.isdir(product_path):
            continue

        descriptors_list = []

        for img_name in os.listdir(product_path):
            img_path = os.path.join(product_path, img_name)

            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            keypoints, descriptors = orb.detectAndCompute(img, None)
            if descriptors is not None:
                descriptors_list.append(descriptors)

        if descriptors_list:
            features[product_name] = np.vstack(descriptors_list)

    return features


DATASET_FEATURES = load_dataset_features()


def detect_product_by_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if descriptors is None:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    best_match = None
    best_score = 0

    for product, dataset_desc in DATASET_FEATURES.items():
        matches = bf.match(descriptors, dataset_desc)
        score = len(matches)

        if score > best_score:
            best_score = score
            best_match = product

    if best_score > 20:
        return best_match

    return None
