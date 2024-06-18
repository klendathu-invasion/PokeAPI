from fastapi import APIRouter

from ..utils.tools import Tools

# add each routers in a list
routers = []
Tools.append_all_routers_in_package(routers, __path__[0], __package__)
