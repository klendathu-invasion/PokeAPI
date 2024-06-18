from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from ..routers import routers


class ConfigApp:
    @staticmethod
    def initialize_app(app: FastAPI):
        """This function do some actions to configure the app of the project.

        :param app: the app of the project
        :type app: FastAPI

        """
        app.mount("/static", StaticFiles(directory="openapi/static"), name="static")
        app.mount("/css", StaticFiles(directory="app/css"), name="css")
        app.mount("/public", StaticFiles(directory="app/public"), name="public")

        # INCLUDE ALL ROUTERS
        for router in routers:
            app.include_router(router)

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.root_path + app.openapi_url,
                title=app.title,
                swagger_favicon_url=f"{app.root_path}/public/img/logo.png",
                swagger_js_url=f"{app.root_path}/static/swagger-ui-bundle.js",
                swagger_css_url=f"{app.root_path}/static/swagger-ui.css",
                swagger_ui_parameters={"docExpansion": "none"},
            )
