import os
import sys
import json
from dotenv import load_dotenv

# Add backend to path so we can import services
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv()

from app import create_app
from extensions import db
from services.product_scraper import get_or_scrape_products
from services.agent_service import run_booking_agent

def test_scraper():
    print("\n--- Testing Product Scraper (Amazon) ---")
    query = "modern beige sofa"
    results = get_or_scrape_products(query)
    
    if results:
        print(f"SUCCESS: Scraped {len(results)} products.")
        for i, product in enumerate(results[:2]):
            print(f"  {i+1}. {product['title']} - {product['price']}")
    else:
        print("FAILURE: Scraper returned no results.")

def test_booking_agent():
    print("\n--- Testing Booking Agent (Gemini + Playwright Tools) ---")
    # Using a known product URL (or a placeholder for demo)
    # In a real test, we'd use one of the URLs from the scraper result
    test_url = "https://www.amazon.com/dp/B08P2H8S1C" # Example placeholder
    
    print(f"Initiating booking for: {test_url}")
    # User ID 1 is likely the admin/first user for testing
    result = run_booking_agent(test_url, user_id=1)
    
    print("Agent Result:")
    print(json.dumps(result, indent=2))
    
    if result.get("status") in ["SUCCESS", "FALLBACK", "INFO_REQUIRED"]:
        print(f"SUCCESS: Agent returned valid status: {result['status']}")
    else:
        print(f"FAILURE: Agent failed with status: {result.get('status')}")

if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # 1. Test Scraper
        test_scraper()
        
        # 2. Test Agent (Note: This will involve live Playwright calls)
        test_booking_agent()
