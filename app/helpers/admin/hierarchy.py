from fastapi import HTTPException, status
from fastapi.logger import logger
from pydantic import BaseModel, StringConstraints
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from typing_extensions import Annotated

from ... import models, schemas
from ...utils.tools import Tools


class HierarchyResponse(BaseModel):
    company_state: str
    company_id: int
    factory_state: str
    factory_id: int
    division_state: str
    division_id: int
    cei_state: str
    cei_id: int
    workshop_state: str
    workshop_id: int
    line_state: str
    line_id: int
    work_cell_state: str
    work_cell_id: int


class Hierarchy(BaseModel):
    @staticmethod
    def message_new_model(new_model: bool) -> str:
        """This function define the message for a model depends if the model already exist or just be created.

        :param new_model: the boolean define if the model already exist or just be created
        :type new_model: bool
        :returns: str

        """
        if new_model:
            return "Done"
        return "Already exist"

    @staticmethod
    def ilike_query(key: str, value: str) -> dict:
        """This function define a dict to have an ilike query.

        :param key: the name of the column for the query
        :param value: the value for the query
        :type key: str
        :type value: str
        :returns: dict

        """
        return {key: {"ilike": Tools.query_like_escape(value)}}

    @staticmethod
    def get_model(
        db: Session,
        model_class: DeclarativeMeta,
        model_parent: models.base_model.BaseModel,
        children: str,
        model_base,
        query: dict,
    ) -> tuple[models.base_model.BaseModel, bool]:
        """This function get the model from the database or set one to create it.

        :param db: the session
        :param model_class: the class of the model requested
        :param model_parent: the parent of the model requested
        :param children: the name of the attribute for the children of the parent of the model requested
        :param model_base: the schema of the model to build if not found
        :param query: the query to find the model
        :type db: Session
        :type model_class: DeclarativeMeta
        :type model_parent: models.base_model.BaseModel
        :type children: str
        :type query: dict
        :returns: tuple[models.base_model.BaseModel, bool]

        """
        is_new = False
        model = model_class.find_by(db, **query) if model_parent.id else None
        if model is None:
            model = model_class(**model_base.model_dump())
            getattr(model_parent, children).append(model)
            is_new = True
        return (model, is_new)

    @classmethod
    def get_response(
        cls,
        company_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        company_trigram: Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, min_length=3, pattern=r"^[a-zA-Z]+$"
            ),
        ],
        factory_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        division_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        cei_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        workshop_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        line_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        work_cell_name: Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1)
        ],
        db: Session,
    ) -> HierarchyResponse:
        """This function find or create the 7 levels.

        :param company_name: the name of the company
        :param company_trigram: the trigram of the company
        :param factory_name: the name of the factory
        :param division_name: the name of the division
        :param cei_name: the name of the cei
        :param workshop_name: the name of the workshop
        :param line_name: the name of the line
        :param work_cell_name: the name of the work_cell
        :param db: the session
        :type company_name: str
        :type company_trigram: str
        :type factory_name: str
        :type division_name: str
        :type cei_name: str
        :type workshop_name: str
        :type line_name: str
        :type work_cell_name: str
        :type db: Session
        :returns: tuple[HierarchyResponse]
        :raises HTTPException: raises HTTP exception if the company_name and company_trigram match with a company but not together

        """
        company = schemas.company.CompanyBase(
            name=company_name, trigram=company_trigram
        )
        factory = schemas.factory.FactoryBase(name=factory_name, company_id=0)
        division = schemas.division.DivisionBase(name=division_name, factory_id=0)
        cei = schemas.cei.CeiBase(name=cei_name, division_id=0)
        workshop = schemas.workshop.WorkshopBase(name=workshop_name, cei_id=0)
        line = schemas.line.LineBase(name=line_name, workshop_id=0)
        work_cell = schemas.work_cell.WorkCellBase(name=work_cell_name, line_id=0)

        db_company_name = models.company.Company.find_by(
            db, **cls.ilike_query("name", company.name)
        )
        db_company = models.company.Company.find_by(
            db, **cls.ilike_query("trigram", company.trigram)
        )
        if db_company != db_company_name:
            error = []
            if db_company_name:
                message = f"A company with the name '{db_company_name.name}' already exist (id = {db_company_name.id})"
                logger.error(message)
                error.append(message)
            if db_company:
                message = f"A company with the trigram '{db_company.trigram}' already exist (id = {db_company.id})"
                logger.error(message)
                error.append(message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        new_company = False
        if db_company is None:
            db_company = models.company.Company(**company.model_dump())
            new_company = True
        factory.company_id = db_company.id
        db_factory, new_factory = cls.get_model(
            db=db,
            model_class=models.factory.Factory,
            model_parent=db_company,
            children="factories",
            model_base=factory,
            query={
                "company_id": db_company.id,
                **cls.ilike_query("name", factory.name),
            },
        )

        division.factory_id = db_factory.id
        db_division, new_division = cls.get_model(
            db=db,
            model_class=models.division.Division,
            model_parent=db_factory,
            children="divisions",
            model_base=division,
            query={
                "factory_id": db_factory.id,
                **cls.ilike_query("name", division.name),
            },
        )

        cei.division_id = db_division.id
        db_cei, new_cei = cls.get_model(
            db=db,
            model_class=models.cei.Cei,
            model_parent=db_division,
            children="ceis",
            model_base=cei,
            query={"division_id": db_division.id, **cls.ilike_query("name", cei.name)},
        )

        workshop.cei_id = db_cei.id
        db_workshop, new_workshop = cls.get_model(
            db=db,
            model_class=models.workshop.Workshop,
            model_parent=db_cei,
            children="workshops",
            model_base=workshop,
            query={"cei_id": db_cei.id, **cls.ilike_query("name", workshop.name)},
        )

        line.workshop_id = db_workshop.id
        db_line, new_line = cls.get_model(
            db=db,
            model_class=models.line.Line,
            model_parent=db_workshop,
            children="lines",
            model_base=line,
            query={"workshop_id": db_workshop.id, **cls.ilike_query("name", line.name)},
        )

        work_cell.line_id = db_line.id
        db_work_cell, new_work_cell = cls.get_model(
            db=db,
            model_class=models.work_cell.WorkCell,
            model_parent=db_line,
            children="work_cells",
            model_base=work_cell,
            query={"line_id": db_line.id, **cls.ilike_query("name", work_cell.name)},
        )

        db_company.save(db)
        return HierarchyResponse(
            company_state=cls.message_new_model(new_company),
            company_id=db_company.id,
            factory_state=cls.message_new_model(new_factory),
            factory_id=db_factory.id,
            division_state=cls.message_new_model(new_division),
            division_id=db_division.id,
            cei_state=cls.message_new_model(new_cei),
            cei_id=db_cei.id,
            workshop_state=cls.message_new_model(new_workshop),
            workshop_id=db_workshop.id,
            line_state=cls.message_new_model(new_line),
            line_id=db_line.id,
            work_cell_state=cls.message_new_model(new_work_cell),
            work_cell_id=db_work_cell.id,
        )
