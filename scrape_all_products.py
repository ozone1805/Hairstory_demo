import csv
import requests
from bs4 import BeautifulSoup
import json
import time
import sys

def scrape_product_details(url, product_name):
    """
    Scrape product details from a Hairstory product page using the original logic.
    
    Args:
        url (str): The product URL to scrape
        product_name (str): The product name from CSV
        
    Returns:
        dict: Dictionary containing product information
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching: {product_name} - {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Use the original selectors
        selectors = {
            "title": "#MainContent h1 span",
            "subtitle": "#MainContent h2",
            "details": "div#ProductDescription",
            "benefits": "div[content-type='benefit']",
            "how_to_use": "div[content-type='how_to_use']",
            "ingredients": "div[content-type='ingredients']"
        }
        
        # Extract text content
        results = {"name": product_name, "url": url}
        for key, selector in selectors.items():
            element = soup.select_one(selector)
            if element:
                results[key] = element.get_text(strip=True)
            else:
                results[key] = None
        
        return results
        
    except Exception as e:
        print(f"Error scraping {product_name}: {e}")
        return {"name": product_name, "url": url, "error": str(e)}

def main():
    """Main function to scrape all products from CSV."""
    all_products = []
    
    # Read products from CSV
    with open('products.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        products = list(reader)
    
    print(f"Found {len(products)} products to scrape")
    print("-" * 50)
    
    # Scrape each product
    for i, product in enumerate(products, 1):
        print(f"Processing {i}/{len(products)}: {product['name']}")
        
        product_data = scrape_product_details(product['url'], product['name'])
        all_products.append(product_data)
        
        # Add a small delay to be respectful to the server
        if i < len(products):  # Don't delay after the last product
            time.sleep(1)
    
    # Save all products to JSONL format (product_catalogue.txt)
    jsonl_output_path = "product_catalogue.txt"
    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        for product in all_products:
            f.write(json.dumps(product, ensure_ascii=False) + '\n')
    
    # Save all products to JSON format (all_products.json)
    json_output_path = "all_products.json"
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    print(f"\nScraped {len(all_products)} products")
    print(f"Results saved to: {jsonl_output_path} (JSONL format)")
    print(f"Results saved to: {json_output_path} (JSON format)")
    
    # Print summary
    successful = sum(1 for p in all_products if "error" not in p)
    failed = len(all_products) - successful
    print(f"Successful: {successful}, Failed: {failed}")

if __name__ == "__main__":
    main() 