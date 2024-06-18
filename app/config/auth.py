from functools import lru_cache

import i18n
from fastapi import Depends, HTTPException, Request, status
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, schemas
from ..helpers.check import Check
from ..utils.dependency import Dependency
from ..utils.tools import Tools
from . import role as config_role
from .env import settings

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")
# _oauth2_scheme = HTTPBearer(auto_error=False)
ERROR_INVALID_CREDENTIALS = "errors.invalid_credential"


class Auth(BaseModel):
    __abilities__ = {
        # v1/admin
        "admin_create_hierarchy": [],
        # v1/cart
        "list_carts_by_user": ["myself"],
        "create_cart": ["possessor", "client"],
        "read_cart": ["possessor"],
        "update_cart": ["possessor"],
        "delete_cart": ["possessor"],
        # v1/product
        "list_products_by_shop": ["owner", "member", "possessor", "client"],
        "create_product": ["owner", "member"],
        "read_product": ["owner", "member", "possessor", "client"],
        "update_product": ["owner", "member"],
        "delete_product": ["owner", "member"],
        # v1/shop
        "list_shops_by_user": ["myself"],
        "create_shop": ["owner", "member", "pro"],
        "read_shop": ["owner", "member", "possessor", "client"],
        "update_shop": ["owner", "member"],
        "delete_shop": ["owner", "member"],
        # v1/wish
        "list_wishes_by_user": ["myself"],
        "create_wish": ["myself"],
        "read_wish": ["possessor"],
        "update_wish": ["possessor"],
        "delete_wish": ["possessor"],
        # v1/shop_member
        "create_shop_member": ["owner", "member"],
        "delete_shop_member": ["owner", "member"],
        # v1/user
        "read_user_me": ["myself"],
        "create_user": [],
        "get_all_admin": [],
        "read_user": ["myself"],
        "update_user_is_admin": [],
        "delete_user": [],
    }

    @staticmethod
    def _decode_token(
        token: str | None = Depends(_oauth2_scheme),
        db: Session = Depends(Dependency.get_db),
    ) -> tuple[models.user.User, Session]:
        """This function get the user with the token given (match by matricule ).

        :param token: the token where is stored the jwt authentification token
        :param db: the session
        :type token: str
        :type db: Session
        :returns: tuple[models.user.User, Session]

        """
        if token is None:
            logger.error("Token : Decode token - None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t(ERROR_INVALID_CREDENTIALS),
            )
        db_user = None
        try:
            payload = jwt.decode(
                token,
                settings.secret_key_jwt,
                algorithms=[settings.algorithm],
            )
            matricule = payload.get("matricule")
            email = payload.get("email")
            if matricule is None or email is None:
                logger.error(
                    f"Token : Decode token - matricule : {matricule}, email : {email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t(ERROR_INVALID_CREDENTIALS),
                )
            db_user = models.user.User.find_by(db, matricule=matricule, email=email)
            if db_user is None:
                logger.error(
                    f"Token : Decode token - User not found : {matricule}, email : {email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t(ERROR_INVALID_CREDENTIALS),
                )
        except JWTError as jwt_error:
            logger.error(f"Token : Decode token - JWTError : {jwt_error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t(ERROR_INVALID_CREDENTIALS),
            )
        return (db_user, db)

    @classmethod
    @lru_cache()
    def _check_role_endpoint(cls, role: tuple, endpoint: str) -> None:
        """This function check if the user with the role is allow to go to the endpoint of the request.

        :param role: the role of the user
        :param endpoint: the endpoint of the request
        :type role: str
        :type endpoint: str
        :returns: None
        :raises HTTPException: raises HTTP exception if the role isn't allow for this endpoint

        """
        if endpoint in cls.__abilities__:
            if len(set(role) & set(cls.__abilities__[endpoint])) == 0:
                logger.error(
                    f"Check role : role ({role}) not allowed for endpoint ({endpoint})"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t("errors.invalid_role"),
                )

    @classmethod
    def _get_role(cls, db: Session, user: schemas.user.UserComplete, args: dict) -> set:
        """This function get the role of an user for the arguments.

        :param db: the session
        :param user: the user
        :param args: the arguments to find the role
        :type db: Session
        :type user: schemas.user.UserComplete
        :type args: dict
        :returns: str | None

        """
        # ["owner", "member", "pro", "client"]
        print(f"{user = }")
        if user.is_admin:
            return {"admin"}
        role = {"pro"} if user.is_pro else {"client"}  # change with scope
        keys_set = set(args) & set(config_role.Role.__tables_by_id__.keys())
        for key in keys_set:
            model_id = int(args[key] or "0")
            if key == "user_id" and user.id == model_id:
                if len(keys_set) == 1:
                    role.add("myself")
            else:
                information_table = config_role.Role.__tables_by_id__[key]
                print(f"{information_table = } | {key = }")
                cl = information_table["class"]
                model = Tools.get_class_from_string(
                    models, f"{cl}.{cl.title().replace('_', '')}"
                ).find_by(db, id=model_id)
                print(f"{user = } | {model = }")
                print(f"1_{role = }")
                if "user_id" in dir(model):
                    print(f"{model.user_id = }")
                if "user_ids" in dir(model):
                    print(f"{model.user_ids = }")
                if "user_id" in dir(model) and model.user_id == user.id:
                    if "role" in information_table:
                        tmp_role = information_table["role"]
                        if tmp_role == "owner" and user.is_pro:
                            role.add("owner")
                        elif tmp_role == "possessor" and not user.is_pro:
                            role.add("possessor")
                elif "user_ids" in dir(model) and user.id in model.user_ids:
                    role.add("member")
                print(f"2_{role = }")
        return role

        # role = None
        # keys_set = set(args) & set(config_role.Role.__tables_by_id__.keys())
        # if len(keys_set) > 1 and "team_id" in keys_set and "user_id" not in keys_set:
        #     keys_set.remove("team_id")
        # for key in keys_set:
        #     model_id = int(args[key] or "0")
        #     if key == "user_id":
        #         if user.is_admin:
        #             role = "admin"
        #         elif user.id == model_id:
        #             role = "user"
        #     else:
        #         information_table = config_role.Role.__tables_by_id__[key]
        #         cl = information_table["class"]
        #         model = Tools.get_class_from_string(
        #             models, f"{cl}.{cl.title().replace('_', '')}"
        #         ).find_by(db, id=model_id)
        #         role = config_role.Role.get_best_role(
        #             db, user, model, information_table
        #         )
        #     if role is not None:
        #         return role
        # if not keys_set:
        #     role = config_role.Role.get_best_role(db, user)
        # return role

    @staticmethod
    def get_current_user(
        response_decode_token: tuple[models.user.User, Session] = Depends(
            staticmethod(_decode_token)
        )
    ) -> tuple[schemas.user.UserComplete, Session]:
        """This function check existence of the current user and get it.

        :param response_decode_token: the tuple containing the user and the session
        :type response_decode_token: tuple[models.user.User, Session]
        :returns: tuple[schemas.user.UserComplete, Session]
        :raises HTTPException: raises HTTP exception if the user is None

        """
        user, db = response_decode_token
        if not user:
            logger.error(f"Get current user : no user authenticated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t(ERROR_INVALID_CREDENTIALS),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return (schemas.user.UserComplete.model_validate(user), db)

    @classmethod
    def get_level_informations(
        cls,
        user: schemas.user.UserComplete,
        db: Session,
        level: str,
        model_name: str,
        query_json: dict,
        metadata: dict,
    ) -> tuple[str, int]:
        """This function get the id of the model and his key for others tables and add informations in metadata if the user is allowed to see the model.

        :param user: the user who needs authorization
        :param db: the session
        :param level: the name of the level of the users organization
        :param model_name: the name of the model of the level
        :param query_json: the query to find the model requested
        :param metadata: the metadata where add some informations about the model
        :type user: schemas.user.UserComplete
        :type db: Session
        :type level: str
        :type model_name: str
        :type query_json: dict
        :type metadata: dict
        :returns: tuple[str, int]
        :raises HTTPException: raises HTTP exception if the model isn't found or if the user isn't allowed for this model

        """
        model_class = Tools.get_class_from_string(models, model_name)
        model = Check.model_exist(
            db=db,
            model_class=model_class,
            query=query_json,
            status_code=status.HTTP_404_NOT_FOUND,
        )
        model_key_id = f"{level}_id"
        information_table = config_role.Role.__tables_by_id__[model_key_id]
        role = config_role.Role.get_best_role(db, user, model, information_table)
        if role is None:
            logger.error(f"Get level information : role is None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t("errors.invalid_role"),
            )
        attribut = list(query_json.keys())[0]
        metadata[f"{level}_{attribut}"] = getattr(model, attribut)
        metadata[f"{level}_id"] = str(model.id)
        return (model_key_id, model.id)

    @classmethod
    def check_role_user(
        cls,
        request: Request,
        response_user: tuple[schemas.user.UserComplete, Session] = Depends(
            staticmethod(get_current_user)
        ),
    ) -> schemas.user.User:
        """This function check existence of the current user and the permission of its role and get it.

        :param request: the resquest
        :param response_user: the tuple containing the user and the session
        :type request: Request
        :type request: tuple[schemas.user.UserComplete, Session]
        :returns: schemas.user.User

        """
        current_user, db = response_user
        user = schemas.user.UserComplete(**current_user.model_dump())
        if "_json" in request.__dict__ and type(request._json) is dict:
            args = request._json
            args.update(request.scope["path_params"])
        else:
            args = dict(request.scope["path_params"])
        role = cls._get_role(db, user, args)
        if "admin" not in role:
            endpoint = request.scope["route"].endpoint.__name__
            cls._check_role_endpoint(tuple(role), endpoint)
        return schemas.user.User(**user.model_dump())
