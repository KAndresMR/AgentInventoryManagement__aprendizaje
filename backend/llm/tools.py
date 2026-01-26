from typing import List, Type
from pydantic import BaseModel
from langchain.tools import BaseTool


class ProductLabelInput(BaseModel):
    query: str


class ExtractProductLabelsTool(BaseTool):
    name: str = "extract_product_labels"
    description: str = "Extract up to 3 product names from a user query"
    args_schema: Type[BaseModel] = ProductLabelInput

    async def _arun(self, query: str) -> dict:
        """
        Prototipo simple de extracción de productos (multilabel).
        """
        keywords = ["leche", "pan", "arroz", "huevos", "azúcar"]

        labels: List[str] = []
        query_lower = query.lower()

        for k in keywords:
            if k in query_lower:
                labels.append(k)

        return {
            "products": labels[:3]  # máximo 3 productos
        }

    def _run(self, query: str):
        raise NotImplementedError("Only async supported")
