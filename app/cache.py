from cachetools import TTLCache
from config import settings

cache = TTLCache(maxsize=5000, ttl=settings.CACHE_TTL)
