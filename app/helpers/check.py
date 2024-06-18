import i18n
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ..errors.no_account_user import NoAccountUserError


class Check(BaseModel):
    @staticmethod
    def model_exist(
        db: Session,
        model_class: DeclarativeMeta,
        query: dict,
        status_code: int,
        attribute: str | None = None,
        check: bool = False,
        bypass: bool = False,
    ):
        """This function check existance of a model by query and return this model.

        :param db: the session
        :param model_class: the class of the model
        :param query: the query to find the model
        :param status_code: the status code if failed
        :param attribute: the name of the attribute if check for unicity of the model
        :param check: a bool to check existance or not of the model
        :type db: Session
        :type model_class: DeclarativeMeta
        :type query: dict
        :type status_code: int
        :type attribute: str | None
        :type check: bool
        :returns: the model
        :raises HTTPException: raises HTTP exception if the model is found with check = True or isn't found with check = False

        """
        db_model = model_class.find_by(db, **query)
        db_model_exist = db_model is not None if check else db_model is None
        error = "errors.already_with_name" if check else "errors.not_found_with_name"
        if db_model_exist:
            if bypass:
                raise NoAccountUserError(attr=", ".join(map(str, query.values())))
            key = "name" if attribute is None else f"attributes.{attribute}"
            raise HTTPException(
                status_code=status_code,
                detail=i18n.t(
                    error,
                    name=i18n.t(f"models.{model_class.__tablename__}.{key}"),
                ),
            )
        return db_model
