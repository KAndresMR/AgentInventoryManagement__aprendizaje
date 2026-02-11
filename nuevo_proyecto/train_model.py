import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

# Configuración
DATASET_PATH = "imagenes_productos"
IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 10

# Generador de imágenes con aumentos
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,
    zoom_range=0.1,
    horizontal_flip=True,
)

train_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
)


# Modelo basado en MobileNet
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights="imagenet"
)

base_model.trainable = False

model = models.Sequential(
    [
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="relu"),
        layers.Dense(train_data.num_classes, activation="softmax"),
    ]
)

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

model.summary()

# Entrenamiento
model.fit(train_data, epochs=EPOCHS)


# Guardar modelo
model.save("product_classifier.h5")

# Guardar etiquetas
import json

with open("labels.json", "w") as f:
    json.dump(train_data.class_indices, f)

print("Modelo entrenado y guardado.")
