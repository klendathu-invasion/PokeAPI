import logging

from fastapi.logger import logger as logger_fastapi
from pydantic import BaseModel
from uvicorn.logging import AccessFormatter, DefaultFormatter

from .env import settings


class AppFormatter(DefaultFormatter):
    def __init__(
        self,
        fmt: str,
        datefmt: str = "%Y-%m-%dT%H:%M:%S",
        style: str | None = None,
        **args,
    ):
        date_prefix = ""
        if settings.app_source == "local":
            color_start = "\x1b[32;20m"
            color_end = "\x1b[0m"
            date_prefix = f"[{color_start}%(asctime)s.%(msecs)03d{color_end}]"
        data = {
            "fmt": fmt.replace(
                "%(levelprefix)s",
                f"{date_prefix}[%(thread)d] %(name)-25s - %(levelprefix)s",
            )
        }
        if datefmt:
            data["datefmt"] = datefmt
        if style:
            data["style"] = style
        data.update(args)
        super().__init__(**data)


class AppAccessFormatter(AppFormatter, AccessFormatter):
    pass


class Logging(BaseModel):
    @staticmethod
    def _set_formatter_or_add_handler(
        formatter: AppFormatter,
        handler: logging.StreamHandler,
        logger: logging.Logger,
    ) -> None:
        """This function set the first formatter (or the handler) for the logger.

        :param formatter: the formatter to add into the logger
        :param handler: the handler to add if no one exist
        :param logger: the logger to update
        :type formatter: AppFormatter
        :type handler: logging.StreamHandler
        :type logger: logging.Logger

        """
        if len(logger.handlers) > 0:
            if formatter.__class__ == type:
                old_formatter = logger.handlers[0].formatter
                logger.handlers[0].setFormatter(formatter(fmt=old_formatter._fmt))
            else:
                logger.handlers[0].setFormatter(formatter)
        else:
            logger.addHandler(handler)

    @staticmethod
    def _get_level_logging():
        """This function define the level of the logging for the logger fastapi."""
        if settings.app_source == "local":
            return logging.DEBUG
        elif settings.fastapi_env.value in ["dev", "test"]:
            return logging.INFO
        return logging.WARNING

    @classmethod
    def initialite_logging(cls):
        """This function define the formatter for the different loggers used by the app."""
        handler_stream = logging.StreamHandler()
        formatter = AppFormatter(fmt="%(levelprefix)s %(message)s")
        handler_stream.setFormatter(formatter)

        logger_fastapi.setLevel(cls._get_level_logging())
        cls._set_formatter_or_add_handler(
            logger=logger_fastapi, handler=handler_stream, formatter=formatter
        )
        cls._set_formatter_or_add_handler(
            logger=logging.getLogger("sqlalchemy.engine.Engine"),
            handler=handler_stream,
            formatter=formatter,
        )
        cls._set_formatter_or_add_handler(
            logger=logging.getLogger("uvicorn"),
            handler=handler_stream,
            formatter=AppFormatter,
        )
        cls._set_formatter_or_add_handler(
            logger=logging.getLogger("uvicorn.access"),
            handler=handler_stream,
            formatter=AppAccessFormatter,
        )
