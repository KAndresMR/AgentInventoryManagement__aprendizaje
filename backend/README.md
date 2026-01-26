# Backend – FastAPI + GraphQL (Prototipo)

Este backend es un prototipo funcional desarrollado con FastAPI y Strawberry GraphQL.
Expone una API GraphQL con datos simulados (mock), sin conexión a base de datos.

Su objetivo es demostrar la estructura base del backend y el funcionamiento de GraphQL.

---

## 🧰 Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.12
- pip (incluido con Python)

Para verificar:

python --version
pip --version

## Ubicación del backend

AgentInventoryManagement\_\_aprendizaje/backend

## Instalar las dependencias

pip install fastapi uvicorn strawberry-graphql aioinject pydantic-settings

## Levantar el servidor

uvicorn main:app --reload

## Endpoints disponibles

http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/graphql

## Query GraphQL de ejemplo

query {
products {
id
name
price
stock {
quantity
available
}
}
}
