from connections.elastic import Elasticsearch
from connections.redis_manager import RedisManager


async def get_cache():
    cache = RedisManager()
    try:
        yield cache
    finally:
        await cache.close()


async def get_elastic():
    elastic = Elasticsearch()
    try:
        yield elastic
    finally:
        await elastic.close()
