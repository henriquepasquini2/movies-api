import os

from decouple import UndefinedValueError, config

from utils.singleton import Singleton


class Configuration(metaclass=Singleton):
    """
    Singleton class to load the configuration from environment
    variables and secrets for the Movies API.
    """

    def __init__(self):
        self.PROJECT_NAME = "Movie API"
        self.PROJECT_VERSION = "0.1.0"
        self.API_V1_STR = "/api/v1"
        self.PROJECT_ID = self._load_variable("PROJECT_ID", default="moviedb")
        self.NAMESPACE = self._load_variable("NAMESPACE", default="public")
        self.STACKDRIVER_LOGGER = self._load_variable(
            "STACKDRIVER_LOGGER", cast=bool, default=True
        )
        self.LOGS_ENABLED = self._load_variable("LOGS_ENABLED", cast=bool, default=True)
        self.LOG_LEVEL = self._load_variable("LOG_LEVEL", default="INFO")
        self.IS_LOCAL = self._load_variable("IS_LOCAL", cast=bool, default=False)
        self.ES_WITCHER_URL = self._load_variable(
            variable_name="ES_MOVIES_URL",
            default="http://localhost:8200",
        )
        self.REDIS_URL = self._load_variable(
            variable_name="REDIS_URL",
            default="redis://localhost:6279",
        )
        self.REDIS_HOST = self._load_variable(
            variable_name="REDIS_HOST", default="localhost"
        )
        self.REDIS_PORT = self._load_variable(
            variable_name="REDIS_PORT", cast=int, default=6279
        )
        self.REDIS_INSTANCE_PATH = self._load_variable(
            variable_name="REDIS_INSTANCE_PATH",
            default="projects/moviedb/locations/us-east1/clusters/movies-redis-cluster",
        )
        self.DEFAULT_CACHE_EXPIRATION = self._load_variable(
            "DEFAULT_CACHE_EXPIRATION", cast=int, default=3600 * 24
        )
        self.SLACK_HOOK = self._load_variable(
            "SLACK_HOOK",
            cast=str,
            default="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ",
        )

    @staticmethod
    def _load_variable(variable_name: str, cast: type = str, default=None):
        try:
            if default is None:
                return config(variable_name, cast=cast)
            else:
                return config(variable_name, cast=cast, default=default)
        except UndefinedValueError:
            return default

    @staticmethod
    def _all_secrets_directories(secrets_base_dir="/var/secrets"):

        if not os.path.isdir(secrets_base_dir):
            return []

        secrets_dir_files = os.listdir(secrets_base_dir)

        for filename in secrets_dir_files:
            filepath = os.path.join(secrets_base_dir, filename)
            if os.path.isdir(filepath):
                yield filepath

    def _secret_value(
        self, secret_name: str, secrets_base_dir="/var/secrets/", cast=None
    ):
        """Procura o valor de `secret_name` em cada um dos diretórios em
        `secrets_base_dir` em ordem alfabética.
        Se não encontrar em nenhum, vê se `secret_name` existe como
        variável de ambiente e retorna.
        """
        secret_directories = sorted(
            self._all_secrets_directories(secrets_base_dir=secrets_base_dir)
        )

        for secret_dir in secret_directories:
            secret_filepath = os.path.join(secret_dir, secret_name)

            if not os.path.exists(secret_filepath):
                continue

            with open(secret_filepath, "r") as secret_file:
                result = secret_file.read()
                if cast:
                    result = cast(result)
                return result

        if cast:
            return self._load_variable(secret_name, cast=cast)
        else:
            return self._load_variable(secret_name)


settings = Configuration()
