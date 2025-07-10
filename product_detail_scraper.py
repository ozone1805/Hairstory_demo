import sys
import requests
from bs4 import BeautifulSoup
import json

# Accept URL as a command-line argument, or use default
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://hairstory.com/products/pre-wash-4-oz"

# Fetch the HTML from the URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)
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
results = {}
for key, selector in selectors.items():
    element = soup.select_one(selector)
    if element:
        results[key] = element.get_text(strip=True)
    else:
        results[key] = None

# Write to JSON file
output_path = "pre_wash_product_info.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
