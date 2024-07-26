import uvicorn
from fastapi import FastAPI, Depends
from typing import List, Optional
from scraper import Scraper
from storage import Storage
from notifier import Notifier
from models import Product
from dependencies import verify_token
from cache import cache
from config import settings
from log import Log
from utils import Utils

app: FastAPI = FastAPI()
storage: Storage = Storage()
notifier: Notifier = Notifier()
scraper: Scraper = Scraper(base_url=settings.SCRAPPING_URL)

def update_cache() -> None:
    products: List[Product] = storage.load()
    for product in products:
        cache[product.product_title] = product.product_price

async def scrape_data(max_pages: int, proxy: str) -> dict:
    Log.L(Log.I, "Received data scrapping request with max_pages {} and proxy {}", max_pages, proxy)
    scraper.proxy = proxy
    try:
        products = scraper.scrape(max_pages=max_pages)
        should_save: bool = False
        should_update_map: dict[str, Product] = {}
        for product in products:
            price = cache.get(product.product_title)
            if price == None:
                should_save = True
                should_update_map[product.product_title] = product
            elif price != product.product_price:
                should_update_map[product.product_title] = product
            else:
                Utils.delete_file(product.path_to_image)
            cache[product.product_title] = product.product_price
            
        if should_save:
            db_products: List[Product] = storage.load()
            to_save_products: List[Product] = []
            for product in db_products:
                if should_update_map.get(product.product_title):
                    to_save_products.append(should_update_map.get(product.product_title))
                    should_update_map.pop(product.product_title)
                    Utils.delete_file(product.path_to_image)
                else:
                    to_save_products.append(product)
            
            for productName in should_update_map:
                to_save_products.append(should_update_map[productName])
            storage.save(to_save_products)

        notifier.notify("Scraped {} products and updated {} products".format(len(products), len(should_update_map)))
        return {"message": "Scraped {} products and updated {} products".format(len(products), len(should_update_map))}
    except Exception as e:
        Log.L(Log.E, "Error scrapping/updating data {}", e)
        return {"message": "failed with error {}".format(e)}

# @app.get("/scrape", dependencies=[Depends(verify_token)])
@app.get("/scrape")
async def scrape(max_pages: Optional[int] = 5, proxy: Optional[str] = None) -> dict:
    return await scrape_data(max_pages=max_pages, proxy=proxy)

if __name__ == "__main__":
    try:
        update_cache()
        Log.L(Log.I, "Cache updated")
        Log.L(Log.I, "Starting API server")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        Log.L(Log.E, "Error starting server", e.with_traceback())
