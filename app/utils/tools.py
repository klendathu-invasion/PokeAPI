import importlib
import os
import re
from functools import lru_cache

from fastapi import APIRouter
from pydantic import BaseModel

from ..config.env import settings
from ..config.metadata_tag import MetadataTag

INIT_FILE = "__init__.py"


class Tools(BaseModel):
    @staticmethod
    def append_all_routers_in_package(
        router_list: list[APIRouter], package_path: str, package_name: str
    ) -> None:
        """This function append in a list the router in each module in the package requested.

        :param router_list: the list to append the routers
        :param package_path: the path of package requested
        :param package_name: the name of the package requested
        :type router_list: list[APIRouter]
        :type package_path: str
        :type package_name: str
        :returns: None

        """
        directory = os.listdir(package_path)
        for file_path in directory:
            module_path = None
            if os.path.isdir(f"{package_path}/{file_path}") and file_path not in [
                "__pycache__"
            ]:
                module_path = file_path
            elif (
                os.path.isfile(f"{package_path}/{file_path}")
                and file_path.endswith(".py")
                and file_path
                not in [
                    INIT_FILE,
                    "debug.py",
                    "visual.py",
                ]
            ):
                module_path = file_path[:-3]
            elif file_path in [
                "debug.py",
                "visual.py",
            ] and settings.fastapi_env.value in [
                "dev",
                "test",
            ]:
                module_path = file_path[:-3]
            if module_path is not None:
                module = importlib.import_module(
                    f".{module_path}", package=f"{package_name}"
                )
                router_list.append(getattr(module, "api_router"))

    @staticmethod
    def get_class_from_string(my_module, my_class: str):
        """This get a class of a module from a str.

        :param my_module: the parent module
        :param my_class: the str with the class
        :type my_module: module
        :type my_class: str
        :returns: class

        """

        if my_module is None:
            return None
        tmp = my_module
        for class_str in my_class.split("."):
            if class_str in dir(tmp):
                tmp = getattr(tmp, class_str)
            else:
                return None
        return tmp

    # @staticmethod
    # def get_examples(router: str, endpoint: str) -> dict:
    #     """This function return the examples for an endpoint in a router.

    #     :param router: the name of the router
    #     :param endpoint: the name of the endpoint
    #     :type router: str
    #     :type endpoint: str
    #     :returns: dict

    #     """
    #     filename = f"openapi/examples/routers/{router}/{endpoint}.json"
    #     examples_json = {}
    #     if os.path.isfile(filename):
    #         with open(filename) as f:
    #             examples_json = json.load(f)
    #     return examples_json

    @staticmethod
    def get_name_of_folder(file_path: str) -> str:
        """This function get the name of the folder of the file path requested.

        :param file_path: the file path requested
        :type file_path: str
        :returns: str

        """
        str_path_of_file = os.path.realpath(file_path)
        name_elements_in_path_of_file = str_path_of_file.split(os.path.sep)
        return name_elements_in_path_of_file[-2]

    @staticmethod
    def include_all_routers_in_package(
        router: APIRouter, package_path: str, package_name: str
    ) -> None:
        """This function include in a router the router in each module in the package requested.

        :param router: the router to include the routers
        :param package_path: the path of package requested
        :param package_name: the name of the package requested
        :type router: APIRouter
        :type package_path: str
        :type package_name: str
        :returns: None

        """
        directory = os.listdir(package_path)
        for file_path in directory:
            if (
                os.path.isfile(f"{package_path}/{file_path}")
                and file_path.endswith(".py")
                and file_path not in [INIT_FILE]
            ):
                router_name = file_path[:-3]
                module = importlib.import_module(
                    f".{router_name}", package=f"{package_name}"
                )
                metadata = getattr(MetadataTag, f"__tag_{router_name}__")
                router.include_router(
                    getattr(module, "router"),
                    prefix=metadata.prefix,
                    tags=[metadata.name],
                )

    @staticmethod
    def import_all_module_in_package(package_path: str, package_name: str) -> None:
        """This function import each module in the package requested.

        :param package_path: the path of package requested
        :param package_name: the name of the package requested
        :type package_path: str
        :type package_name: str
        :returns: None

        """
        directory = os.listdir(package_path)
        for file_path in directory:
            if (
                os.path.isfile(f"{package_path}/{file_path}")
                and file_path.endswith(".py")
                and file_path not in [INIT_FILE]
            ):
                importlib.import_module(f".{file_path[:-3]}", package=f"{package_name}")
            elif os.path.isdir(f"{package_path}/{file_path}") and file_path not in [
                "__pycache__"
            ]:
                importlib.import_module(f".{file_path}", package=f"{package_name}")

    @staticmethod
    def query_like_escape(attribute: str | None) -> dict:
        """This function escape the parameter to a like query.

        :param attribute: the parameter to escape
        :type attribute: str
        :returns: dict

        """
        if attribute is None:
            return {"other": ""}
        return {"other": re.sub(r"([_%])", r"\\\1", attribute), "escape": "\\"}

    @staticmethod
    @lru_cache()
    def sizeof_fmt(num):
        for unit in ("", "Ko", "Mo", "Go", "To"):
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}"
            num /= 1024.0
        return f"{num:.1f} {unit}"
