from functools import lru_cache

from dotenv import load_dotenv
from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings

from ..enums.environment import EnvironmentEnum

load_dotenv()


class _Settings(BaseSettings):
    algorithm: str = "HS256"
    app_source: str = "local"
    app_uri: str = ""
    app_version: str = "0.0.1"
    aws_dynamodb_table: str = "functional-monitoring-dynamodb--table"
    bucket_prefix: str = ""
    database_engine: str = "sqlite"
    database_url: str = "sqlite:///./db/sql_app.db"
    fastapi_env: EnvironmentEnum = EnvironmentEnum.dev
    fastapi_title: str = "FastAPI Test - Backend"
    openapi_path: str = ""
    pytest_xdist_worker: str | None = None
    root_path: str = ""
    secret_key_jwt: str = ""

    model_config = ConfigDict(env_file=".env", extra="allow")

    @model_validator(mode="after")
    @classmethod
    def rename_test_database(cls, env):
        if env.pytest_xdist_worker and env.fastapi_env == EnvironmentEnum.test:
            env.database_url = env.database_url.replace(
                "test", f"test_{env.pytest_xdist_worker}"
            )
        return env


@lru_cache()
def get_settings() -> _Settings:
    """This function get the setting of the app.

    :returns: _Settings

    """
    return _Settings()


settings = get_settings()
