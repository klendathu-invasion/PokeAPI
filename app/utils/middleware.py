from fastapi import Request
from fastapi.logger import logger

from ..config.translation import active_translation


def add_middlewares(app):
    @app.middleware("http")
    async def get_accept_language(request: Request, call_next):
        active_translation(request.headers.get("accept-language", None))
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def app_entry(request: Request, call_next):
        body = await request.body()
        if body:
            body_decoded = body.decode(errors="ignore")
            logger.info(body_decoded)

        response = await call_next(request)
        return response
