import json
import os
import sqlite3
import subprocess

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
        logger.info(
            f"====== Start connection with database : {settings.database_engine} ======"
        )

        logger.info("====== Database initialized ======")
        alembic_cmd = ["alembic", "--raiseerr", "upgrade", "head"]

        if settings.app_source == "local":
            logger.info("Begin migration with alembic")
            subprocess.run(alembic_cmd)
        else:
            subprocess.Popen(alembic_cmd)
        logger.info("====== Migrations done ======")

    @classmethod
    def initialize_database(cls, engine):
        """This function prepare the database at the start of the server (create tables and seed them on dev mode).

        :param engine: the database
        :returns: None

        """
        event.listen(engine, "connect", cls._set_sqlite_pragma)
        cls._create_database()
        if settings.fastapi_env.value in ["dev", "test"]:
            cls.initialize_table(engine)

    @staticmethod
    def initialize_table(engine) -> None:
        """This function insert some data in the database.

        :param engine: the database
        :returns: None

        """
        with engine.connect() as conn:
            for table in models.Base.metadata.sorted_tables:
                tablename = str(table)
                filename = f"app/config/seeds/{tablename}.json"
                if (
                    os.path.isfile(filename)
                    and len(conn.execute(table.select()).fetchall()) == 0
                ):
                    if (
                        "id" in table.columns.keys()
                        and settings.database_engine != "sqlite"
                    ):
                        conn.execute(
                            text(f"ALTER SEQUENCE {tablename}_id_seq RESTART WITH 1;")
                        )
                        conn.commit()
                    logger.debug(f"EXECUTE INSERT IN {tablename}")
                    with open(filename) as f:
                        table_json = json.load(f, object_hook=DictHandler.parser)
                        conn.execute(table.insert(), table_json)
            conn.commit()

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
