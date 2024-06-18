from fastapi import APIRouter

from ...utils.tools import Tools

# get the name of this folder
name_current_folder = Tools.get_name_of_folder(__file__)

# create router with prefix version
api_router = APIRouter(prefix=f"/{name_current_folder}")

Tools.include_all_routers_in_package(api_router, __path__[0], __package__)
