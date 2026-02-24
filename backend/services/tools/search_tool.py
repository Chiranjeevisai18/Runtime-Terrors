from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from .base_tool import format_tool_response
from services.product_scraper import get_or_scrape_products

class SearchProductInput(BaseModel):
    query: str = Field(description="The search query for the product, e.g., 'modern beige sofa'.")

class SearchProductTool(BaseTool):
    name: str = "search_product"
    description: str = "Use this tool to search for a product on the vendor site. Returns a list of matching products with their URLs and prices."
    args_schema: Type[BaseModel] = SearchProductInput

    def _run(self, query: str) -> str:
        try:
             # Re-use our existing scraper logic
             results = get_or_scrape_products(query)
             if not results:
                 return format_tool_response("FAILED", "No products found for that query.")
                 
             return format_tool_response("SUCCESS", "Found products.", products=results)
        except Exception as e:
             return format_tool_response("FAILED", f"Search error: {str(e)}")
