from bots.base_bot import BaseBot, BotConfig 
from typing import List, Dict, Optional 
import re 
from datetime import datetime 
import csv


class ProductScraperBot(BaseBot):
    def __init__(self, config: BotConfig):
        super().__init__(config)
        self.products = []

    def scrape_product_page(self, url: str, selectors: Dict) -> Dict: 
        if not self.navigate(url):
            return None

        self.wait_random(2, 4)

        product_data = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "scrapped_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        }   
        # Extract product details using provided selectors
        for key, selector in selectors.items():
            try:
                if key.startswith("price"):
                    value = self._extract_price(selector)
                elif key == "availability":
                    value = self._extract_availability(selector)
                elif key == "rating":
                    value = self._extract_rating(selector)
                else:
                    element = self.page.query_selector(selector)
                    value = element.text_content().strip() if element else None

                product_data[key] = value

            except Exception as e:
                print(f"Error extracting {key} from {url}: {e}")
                product_data[key] = None

        product_name = product_data.get('name', 'product').replace(' ', '_')[:50]
        self.take_screenshot(f"product_{product_name}")
        return product_data
    

    def _extract_price(self, selector: str) -> Optional[float]:
        element = self.page.query_selector(selector)
        if not element:
            return None
        
        text = element.text_content().strip()
        #Find numbers with decimal points
        matches = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                return None
        return None
    
    def _extract_availability(self, selector: str) -> bool:
        element = self.page.query_selector(selector)
        if element:
            text = element.text_content().strip().lower()
            return "In stock" in text or "available" in text
        return False

    def _extract_rating(self, selector: str) -> Optional[float]:
        element = self.page.query_selector(selector)
        if not element:
            return None
        
        text = element.text_content().strip()
        matches = re.findall(r'\d\.?\d*', text)
        if matches:
            try:
                rating = float(matches[0])
                return min(max(rating, 0), 5)
            except:
                return None
        return None
    
    def scrape_multiple_pages(self, urls: List[str], selectors: Dict) -> List[Dict]:
        self.products = []

        for i, url in enumerate(urls):
            print(f"Scraping {i + 1}/{len(urls)}: {url}")
            
            product = self.scrape_product_page(url, selectors)
            if product:
                self.products.append(product)
                print(f"Scraped: {product.get('name', 'Unknown')}")

            if i < len(urls) - 1:
                self.wait_random(3, 6)

        return self.products 
    
    def save_to_csv(self, filename: str = "products.csv"):
        if not self.products: 
            print("No products to save.")
            return
        
        filepath = self.data_dir / filename 
        fieldnames = self.products[0].keys() if self.products else [] 

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)

        print(f"CSV saved:{filepath} ({len(self.products)} products)")
