import requests
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed, stop_after_attempt
from typing import List
from models import Product
from notifier import Notifier
from utils import Utils
from log import Log

notifier = Notifier()

class Scraper:
    def __init__(self, base_url: str, proxy: str = None):
        self.base_url = base_url
        self.proxy = proxy

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    def fetch_page(self, page_number: int) -> str:
        try:
            url = f"{self.base_url}page/{page_number}/"
            if (page_number == 1):
                url = self.base_url
            response = requests.get(url, proxies={"http": self.proxy, "https": self.proxy})
            response.raise_for_status()
            return response.text
        except Exception as e:
            Log.L(Log.E, "Error fetching page content from {} {}", self.base_url, e)

    def parse_page(self, html_content: str) -> List[Product]:
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        for item in soup.select('.product.type-product'):
            try:
                title_element = item.select_one('.addtocart-buynow-btn a')
                if title_element and title_element.has_attr('data-title'):
                    title = title_element['data-title']
                else:
                    title = ""
                
                price_element = item.select_one('.mf-product-price-box .price .woocommerce-Price-amount')
                if price_element:
                    price = float(price_element.text.replace('₹', '').replace(',', '').strip())
                else:
                    price = 0.0
                    
                image_element = item.select_one('.mf-product-thumbnail img')
                if image_element and image_element.has_attr('data-lazy-src'):
                    image_url = image_element['data-lazy-src']
                    image_url = Utils.download_image(image_url)
                else:
                    image_url = "No image found"
                    
                if title == "" or image_url == "No image found":
                    Log.L(Log.D, "Empty values found for title/image")
                else:
                    products.append(Product(product_title=title, product_price=price, path_to_image=image_url))
            except Exception as e:
                Log.L(Log.E, "Error getting product details {}", e)
            return products

    def scrape(self, max_pages: int) -> List[Product]:
        all_products = []
        for page_number in range(1, max_pages + 1):
            page_content = self.fetch_page(page_number)
            products = self.parse_page(page_content)
            all_products.extend(products)
        return all_products
