import sqlite3

from alembic.config import Config
from fastapi.logger import logger
from pydantic import BaseModel
from sqlalchemy import event, text

from .. import models
from ..utils.dict_handler import DictHandler
from .env import settings


class Seed(BaseModel):
    @staticmethod
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        """This function set PRAGMA foreign_keys to ON if the database is sqlite3 (refuse a foreign_key that doesn't exist in the linked table).

        :param dbapi_connection: the database
        :returns: None

        """
        if type(dbapi_connection) is sqlite3.Connection:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @staticmethod
    def _create_database() -> None:
        """This function run the script to init the database and the migrations to have a database up to date.

        :returns: None

        """

    @classmethod
    def initialize_database(cls, engine):
        """This function prepare the database at the start of the server (create tables and seed them on dev mode).

        :param engine: the database
        :returns: None

        """
        event.listen(engine, "connect", cls._set_sqlite_pragma)

    @staticmethod
    def initialize_table(engine) -> None:
        """This function insert some data in the database.

        :param engine: the database
        :returns: None

        """

    @classmethod
    async def reset_database(cls, engine):
        """This function reset the database.

        :param engine: the database
        :returns: None

        """
        if settings.fastapi_env.value in ["dev", "test"]:
            models.Base.metadata.drop_all(bind=engine)
            cls._create_database()
            cls.initialize_table(engine)
