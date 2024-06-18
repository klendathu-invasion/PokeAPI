import i18n
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, schemas
from ..utils.tools import Tools
from .check import Check
from .check_uniq import CheckUniqHelper


class RouterModelHelper(BaseModel):
    name: str
    parents: list[str] = []
    uniq_list: list[CheckUniqHelper] = []

    def _add_to_query(
        self,
        query: dict,
        name: str,
        model_dict: dict,
        new_model_dict: dict | None = None,
        attributes: list[str] = [],
        operator: str = "__eq__",
    ) -> None:
        """This function add attribute to the query by method specified.

        :param query: the dict to add some key
        :param name: a name to check
        :param model_dict: the dict of the model
        :param new_model_dict: the dict of the new model
        :param attributes: the list of attributes to add
        :param operator: the operator to use
        :type query: dict
        :type name: str
        :type model_dict: dict
        :type new_model_dict: dict | None
        :type attributes: list[str]
        :type operator: str
        :returns: None

        """
        for attribute in attributes:
            model = (
                model_dict
                if attribute != name
                or new_model_dict is None
                or name not in new_model_dict
                or new_model_dict[name] is None
                else new_model_dict
            )
            model_attribute = model[attribute]
            if operator in ["ilike", "like"]:
                model_attribute = Tools.query_like_escape(model_attribute)
            query[attribute] = {operator: model_attribute}

    def _check_uniq(
        self, db: Session, model_dict: dict, new_model_dict: dict | None = None
    ):
        """This function check for each attribute in uniq_list if the model exist.

        :param db: the session
        :param model_dict: the dict of the model
        :param new_model_dict: the dict of new model
        :type db: Session
        :type model_dict: dict
        :type new_model_dict: dict | None
        :returns: the class of the model self.name

        """
        model_class = Tools.get_class_from_string(
            models, f"{self.name}.{self.name.title().replace('_', '')}"
        )
        for uniq in self.uniq_list:
            if (
                new_model_dict is None
                or uniq.name in new_model_dict
                and new_model_dict[uniq.name]
            ):
                query = {}
                self._add_to_query(
                    query,
                    name=uniq.name,
                    model_dict=model_dict,
                    new_model_dict=new_model_dict,
                    attributes=uniq.equal_list,
                )
                self._add_to_query(
                    query,
                    name=uniq.name,
                    model_dict=model_dict,
                    new_model_dict=new_model_dict,
                    attributes=uniq.ilike_list,
                    operator="ilike",
                )
                if new_model_dict:
                    query["id"] = {"not_in": [model_dict["id"]]}
                Check.model_exist(
                    db=db,
                    model_class=model_class,
                    query=query,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    attribute=uniq.name,
                    check=True,
                )
        return model_class

    def list(self, db: Session, query: dict):
        """This function is a generic list route.

        :param db: the session
        :param query: the query to search the list of the model
        :type db: Session
        :type query: dict
        :returns: the list of the model

        """
        model_class = Tools.get_class_from_string(
            models, f"{self.name}.{self.name.title().replace('_', '')}"
        )
        return model_class.where(db, **query)

    def create(self, db: Session, model_dict: dict):
        """This function is a generic create route.

        :param db: the session
        :param model_dict: the dict of the attributes to create the model
        :type db: Session
        :type model_dict: dict
        :returns: the model created

        """
        for parent in self.parents:
            model_parent = Tools.get_class_from_string(
                models, f"{parent}.{parent.title().replace('_', '')}"
            )
            Check.model_exist(
                db=db,
                model_class=model_parent,
                query={"id": model_dict[f"{parent}_id"]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        model_class = self._check_uniq(db, model_dict)
        return model_class.create(db, **model_dict)

    def read(self, db: Session, id: int):
        """This function is a generic read route.

        :param db: the session
        :param id: the id of the searched model
        :type db: Session
        :type id: int
        :returns: the model

        """
        model_class = Tools.get_class_from_string(
            models, f"{self.name}.{self.name.title().replace('_', '')}"
        )
        db_model = Check.model_exist(
            db=db,
            model_class=model_class,
            query={"id": id},
            status_code=status.HTTP_404_NOT_FOUND,
        )
        return db_model

    def update(self, db: Session, id: int, new_model_dict: dict):
        """This function is a generic update route.

        :param db: the session
        :param id: the id of the searched model
        :param new_model_dict: a dict with the changes for the model
        :type db: Session
        :type id: int
        :type new_model_dict: dict
        :returns: the model updated

        """
        db_model = self.read(db, id)
        self._check_uniq(db, db_model.as_dict(), new_model_dict)
        db_model.update(db, **new_model_dict)
        return db_model

    def delete(self, db: Session, id: int) -> dict:
        """This function is a generic delete route.

        :param db: the session
        :param id: the id to find the model
        :type db: Session
        :type relation_ids: int
        :returns: dict

        """
        return {"message": self.read(db, id).delete(db)}


class RouterLinkHelper(BaseModel):
    name: str
    relations: list[str]

    def create(self, db: Session, model_dict: dict):
        """This function is a generic create route for linked model.

        :param db: the session
        :param model_dict: the dict of the attributes to create the model
        :type db: Session
        :type model_dict: dict
        :returns: the model created

        """
        query = {}
        for relation in self.relations:
            relation_id = f"{relation}_id"
            query[relation_id] = model_dict[relation_id]
            model_relation = Tools.get_class_from_string(
                models, f"{relation}.{relation.title().replace('_', '')}"
            )
            Check.model_exist(
                db=db,
                model_class=model_relation,
                query={"id": model_dict[relation_id]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        model_class = Tools.get_class_from_string(
            models, f"{self.name}.{self.name.title().replace('_', '')}"
        )
        Check.model_exist(
            db=db,
            model_class=model_class,
            query=query,
            status_code=status.HTTP_400_BAD_REQUEST,
            check=True,
        )
        return model_class.create(db, **model_dict)

    def delete(self, db: Session, relation_ids: dict) -> dict:
        """This function is a generic delete route for linked model.

        :param db: the session
        :param relation_ids: the dict of the attributes to find the model
        :type db: Session
        :type relation_ids: dict
        :returns: dict

        """
        model_class = Tools.get_class_from_string(
            models, f"{self.name}.{self.name.title().replace('_', '')}"
        )
        query = {}
        for relation in self.relations:
            relation_id = f"{relation}_id"
            query[relation_id] = relation_ids[relation_id]
        db_model = Check.model_exist(
            db=db,
            model_class=model_class,
            query=query,
            status_code=status.HTTP_404_NOT_FOUND,
        )
        return {"message": db_model.delete(db)}
