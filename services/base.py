from abc import ABC

from connections.elastic import Elasticsearch
from connections.redis_manager import RedisManager
from utils.logger import Logger


class BaseService(ABC):
    """
    BaseService class provides common methods and properties
    for all service classes to inherit from.
    """

    def __init__(self):
        self.logger = Logger()
        self.cache = RedisManager()
        self.es = Elasticsearch()
