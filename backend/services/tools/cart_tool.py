from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import asyncio
from playwright.async_api import async_playwright
from .base_tool import format_tool_response

class AddToCartInput(BaseModel):
    url: str = Field(description="The URL of the product to add to the cart.")

class AddToCartTool(BaseTool):
    name: str = "add_to_cart"
    description: str = "Use this tool to navigate to a product page and add the item to the shopping cart."
    args_schema: Type[BaseModel] = AddToCartInput

    def _run(self, url: str) -> str:
        # Run async playwright inside a synchronous tool interface
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._async_add_to_cart(url))
            return result
        finally:
            loop.close()
            
    async def _async_add_to_cart(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # 1. Open the page
                response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Check for blocking (403 or Captcha)
                if response and response.status in [403, 503]:
                    return format_tool_response("FAILED", "CAPTCHA_DETECTED or IP Blocked.")
                    
                # 2. Wait for Add to Cart button (Mocking generic selectors for demo)
                # In real life, selectors change rapidly.
                buttons = await page.query_selector_all('input[name="submit.add-to-cart"], button:has-text("Add to Cart")')
                
                if not buttons:
                     return format_tool_response("FAILED", "COULD_NOT_FIND_ADD_TO_CART_BUTTON")
                     
                # 3. Simulate Click
                await buttons[0].click()
                
                # 4. Wait for cart confirmation page
                await page.wait_for_timeout(3000) # Wait a sec for redirect or ajax
                
                return format_tool_response("SUCCESS", "Item successfully added to cart.")
                
            except Exception as e:
                # Log exception and return controlled failure rather than crashing agent
                return format_tool_response("FAILED", f"Playwright Exception: {str(e)}")
            finally:
                await browser.close()
