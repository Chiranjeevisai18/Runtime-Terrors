
from services.product_scraper import search_amazon_products
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    print("Testing Tavily Amazon Scraper directly...")
    
    results = search_amazon_products("modern side table")
    
    print(f"Got {len(results)} results:")
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title:   {res.get('title')}")
        print(f"Price:   {res.get('price')}")
        print(f"URL:     {res.get('url')}")
        print(f"Image:   {res.get('image_url')[:50]}...")
        print(f"Price: {res.get('price')}")
        print(f"URL:   {res.get('url')}")


import sys
import logging
logging.basicConfig(level=logging.DEBUG)


from services.product_scraper import search_amazon_products
import json

if __name__ == "__main__":
    print("Testing Tavily Amazon Scraper directly...")
    
    results = search_amazon_products("modern side table")
    
    print(f"Got {len(results)} results:")
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title:   {res.get('title')}")
        print(f"Price:   {res.get('price')}")
        print(f"URL:     {res.get('url')}")
        print(f"Image:   {res.get('image_url')[:50]}...")

