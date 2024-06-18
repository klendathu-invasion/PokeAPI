from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.staticfiles import StaticFiles

from ..routers import routers
from .config_app import ConfigApp
from .database import engine
from .logging import Logging
from .seeds import Seed


def startup(app: FastAPI, engine):
    """This function do some actions in startup of the app.

    :param app: the app of the project
    :param engine: the engine of the database
    :type app: FastAPI

    """
    Logging.initialite_logging()
    Seed.initialize_database(engine)
    ConfigApp.initialize_app(app)
    logger.debug("startup done.")


def shutdown():
    """This function do some actions in shutdown of the app."""
    logger.debug("shutdown done.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """This function do some actions in startup and in shutdown of the app.

    :param app: the app of the project
    :type app: FastAPI

    """

    scheduler = BackgroundScheduler()

    startup(app, engine)
    scheduler.start()
    yield

    scheduler.shutdown()
    shutdown()
