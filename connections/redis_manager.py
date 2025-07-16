import json
from os import environ
from typing import List, Optional

from google.cloud import redis_v1beta1
from pydantic import BaseModel, Field, field_validator
from redis import ConnectionPool, Redis
from redis.exceptions import RedisError
from rediscluster import RedisCluster, RedisClusterException

from config import settings
from utils.logger import Logger
from utils.singleton import Singleton


class RedisInstanceData(BaseModel):
    nodes: List[
        dict
    ]  # [{"host": "node1", "port": 6379}, {"host": "node2", "port": 6379}]
    ssl: bool = True
    ca_data: str = Field(..., min_length=1)

    @field_validator("nodes")
    def validate_nodes(cls, nodes):
        if not nodes:
            raise ValueError("At least one node must be provided for Redis Cluster")
        return nodes


class RedisConnectionGoogleInstance:
    def __init__(self, instance_path: str, ssl: bool = True):
        self.instance_path = instance_path
        self.ssl = ssl

    def get_instance(self):
        request = redis_v1beta1.GetInstanceRequest(
            name=self.instance_path,
        )
        return redis_v1beta1.CloudRedisClient().get_instance(request)

    def get_connection_data(self) -> RedisInstanceData:
        instance = self.get_instance()
        nodes = [
            {"host": endpoint.ip, "port": endpoint.port}
            for endpoint in instance.connectivity.endpoints
        ]
        return RedisInstanceData(
            nodes=nodes,
            ssl=self.ssl,
            ca_data=instance.server_ca_certs[0].cert,
        )


class RedisConnectionFactory:
    _pool: ConnectionPool = None
    _ssl_environ: str = "SSL_CERT_FILE"
    _ca_path: str = "/tmp/redis_ca.pem"

    @classmethod
    def save_certificate(cls, data: str):
        with open(cls._ca_path, "w") as ca_file:
            ca_file.write(data)

    @classmethod
    def activate_certificate(cls, ca_path: str | None = None):
        ca_path = ca_path or cls._ca_path
        environ[cls._ssl_environ] = ca_path

    @classmethod
    async def pool(cls, nodes: List[dict], ssl: bool) -> ConnectionPool:
        if cls._pool:
            return cls._pool

        cls._pool = ConnectionPool(
            startup_nodes=nodes,
            decode_responses=True,
            ssl=ssl,
        )
        return cls._pool

    @classmethod
    def new(cls, data: RedisInstanceData) -> Redis:
        if data.ssl:
            cls.save_certificate(data.ca_data)
            cls.activate_certificate()

        return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class RedisManager(metaclass=Singleton):
    def __init__(self):
        self.redis_client = None
        self.logger = Logger()

    def initialize(self):
        """Initializes the RedisCluster connection."""
        if self.redis_client is None:
            try:
                # Initialize RedisCluster connection with URL
                if settings.REDIS_URL:
                    self.redis_client = RedisCluster.from_url(
                        url=settings.REDIS_URL,
                        decode_responses=True,
                        skip_full_coverage_check=True,
                    )
                # Initialize Redis connection with Google instance path
                elif settings.REDIS_INSTANCE_PATH:
                    instance_path = settings.REDIS_INSTANCE_PATH
                    google_instance = RedisConnectionGoogleInstance(
                        instance_path, ssl=False
                    )
                    instance_data = google_instance.get_connection_data()
                    self.redis_client = RedisConnectionFactory.new(instance_data)
                self.redis_client.ping()
                self.logger.info("RedisCluster connection initialized successfully.")
            except RedisClusterException as e:
                self.logger.warning(f"Error initializing RedisCluster connection: {e}")
                if settings.REDIS_URL:
                    self.redis_client = Redis.from_url(
                        url=settings.REDIS_URL,
                        decode_responses=True,
                    )
                elif settings.REDIS_INSTANCE_PATH:
                    instance_path = settings.REDIS_INSTANCE_PATH
                    google_instance = RedisConnectionGoogleInstance(instance_path)
                    instance_data = google_instance.get_connection_data()
                    self.redis_client = RedisConnectionFactory.new(instance_data)
                self.redis_client.ping()
                self.logger.info("Redis connection initialized successfully.")
            except RedisError as e:
                self.logger.error(f"Error initializing Redis connection: {e}")
                raise

    def close(self):
        """Closes the RedisCluster connection."""
        if self.redis_client is not None:
            self.redis_client.close()
            self.logger.info("Redis connection closed.")
            self.redis_client = None

    def set(self, key: str, value: str, ex: Optional[int] = None):
        """Sets a key-value pair in Redis."""
        try:
            serialized = json.dumps(value) if value else ""
            self.redis_client.set(key, serialized, ex=ex)
            self.logger.debug(f"Key '{key}' set with expiration {ex}.")
        except RedisError as e:
            self.logger.error(f"Error setting value for key '{key}': {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """Gets a value by key from Redis."""
        try:
            raw_value = self.redis_client.get(key)
            value = json.loads(raw_value) if raw_value else None
            self.logger.debug(f"Value retrieved for key '{key}'.")
            return value
        except RedisError as e:
            self.logger.error(f"Error getting value for key '{key}': {e}")
            return None

    def delete(self, key: str):
        """Deletes a key from Redis."""
        try:
            self.redis_client.delete(key)
            self.logger.debug(f"Key '{key}' deleted.")
        except RedisError as e:
            self.logger.error(f"Error deleting key '{key}': {e}")
            raise
