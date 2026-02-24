import os
from tavily import TavilyClient

class ProductScraperError(Exception):
    pass

def search_amazon_products(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches amazon.com using Tavily for a given query and returns a list of dictionaries.
    """
    results = []
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    
    if not tavily_api_key:
        print("TAVILY_API_KEY not found in environment. Returning empty list.")
        return []

    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=tavily_api_key)
        
        # Explicit search for Amazon
        tavily_query = f"site:amazon.com {query} buy online furniture"
        print(f"Querying Tavily for: {tavily_query}")
        
        # Execute search with include_images=True
        # We also request raw content if available, but usually the snippet describes it well
        response = client.search(
            query=tavily_query,
            search_depth="advanced",
            include_images=True,
            include_answer=False,
            max_results=max_results
        )
        
        search_results = response.get("results", [])
        images = response.get("images", [])
        
        for i, item in enumerate(search_results):
            # Fallback to amazon logo or a placeholder if images aren't found for that specific index
            image_url = images[i] if i < len(images) else "https://via.placeholder.com/300?text=Amazon+Product"
            
            title = item.get("title", f"Amazon Product: {query}")
            url = item.get("url", f"https://www.amazon.com/s?k={query}")
            
            # Tavily might not always return direct Amazon prices in snippets,
            # so we'll do our best to extract it from the content snippet using $ regex,
            # or provide a default layout
            import re
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', item.get("content", ""))
            price = f"${price_match.group(1)}" if price_match else "Check Amazon"
            
            results.append({
                "title": title[:70] + "..." if len(title) > 70 else title,
                "vendor": "amazon.com",
                "url": url,
                "price": price,
                "rating": "4.5 out of 5 stars", # Mock rating as snippets rarely show exact stars cleanly
                "image_url": image_url
            })
            
    except Exception as e:
        print(f"Tavily Scraper Exception: {str(e)}")
        raise ProductScraperError(f"Failed to scrape using Tavily: {str(e)}")
        
    return results

def get_or_scrape_products(query: str) -> list[dict]:
    """
    Calls Tavily to search Amazon and returns raw results.
    No DB dependency to avoid Flask app context issues.
    """
    try:
        scraped_data = search_amazon_products(query)
        print(f"Tavily returned {len(scraped_data)} results for '{query}'.", flush=True)
        return scraped_data
    except ProductScraperError as e:
        print(f"Scraper error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_or_scrape_products: {e}")
        return []

