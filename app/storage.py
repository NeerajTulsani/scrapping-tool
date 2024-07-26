import json
from pathlib import Path
from typing import List
from models import Product
from config import settings

class Storage:
    def __init__(self):
        self.db_file = Path(settings.DATABASE_FILE)

    def save(self, products: List[Product]) -> None:
        data = [product.dict() for product in products]
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self) -> List[Product]:
        if not self.db_file.exists():
            return []
        with open(self.db_file, 'r') as f:
            data = json.load(f)
        return [Product(**item) for item in data]
