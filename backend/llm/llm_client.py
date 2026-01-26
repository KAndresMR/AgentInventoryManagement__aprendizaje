from llm.tools import ExtractProductLabelsTool

class LLMClient:
    def __init__(self):
        self.tool = ExtractProductLabelsTool()

    async def extract_products(self, query: str) -> dict:
        return await self.tool.arun(query=query)
