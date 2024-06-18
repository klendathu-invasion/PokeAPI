import pytest_check as check
from pydantic import BaseModel
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ...utils.tools import Tools
from ..test_main import TestingSessionLocal
from ..utils import fake_model
from ..utils.switch_fake import SwitchFake


class ModelTest:
    class_name: str
    fake_model: str
    class_model: DeclarativeMeta
    default_columns: dict
    like_test: str | None = None
    relations: list[str] = []
    association_test: str | None = None
    option_relation_test: str | None = None

    def test___repr__(self, session: TestingSessionLocal):
        model_instance = getattr(fake_model, self.fake_model)(session)
        model_str = model_instance.__repr__()
        check.is_in(
            model_instance.__class__.__name__,
            model_str,
            f"The name class '{model_instance.__class__.__name__}' in {model_str}",
        )
        for column in model_instance.__mapper__.columns.keys():
            value = getattr(model_instance, column)
            check.is_in(
                f"{column}={value}",
                model_str,
                f"The attribute '{column}' with the value {value} in {model_str}",
            )

    def test_as_dict(self, session: TestingSessionLocal):
        model_instance = getattr(fake_model, self.fake_model)(session)
        model_dict = model_instance.as_dict()
        for column in model_instance.__mapper__.columns.keys():
            value_dict = model_dict[column]
            value_instance = getattr(model_instance, column)
            check.is_in(column, model_dict, f"The attribute '{column}' in {model_dict}")
            check.equal(
                value_dict,
                value_instance,
                f"The value in the dict for the key '{column}' : '{value_dict} is equal to the value in the instance for the attribute '{column}' : '{value_instance}",
            )

    def test_delete(self, session: TestingSessionLocal):
        model_instance = getattr(fake_model, self.fake_model)(session)
        model_id = model_instance.id
        check.is_true(model_instance.delete(session), "The delete succeed")
        check.is_none(
            self.class_model.find_by(session, id=model_id),
            "The instance can't be find after delete",
        )

    def test_save(self, session: TestingSessionLocal):
        model_instance = self.class_model()
        check.is_false(
            model_instance.save(session),
            f"The save failed with no attribute : {model_instance}",
        )
        check.is_not_none(model_instance._errors, "The failed instance have an error")
        for column, column_type in self.default_columns.items():
            if column_type == "model":
                method = f"fake_{column}"
                if method in dir(fake_model):
                    value = getattr(fake_model, method)(session).id
                column = f"{column}_id"
            else:
                value = SwitchFake.fake(attribute_type=column_type)
            setattr(model_instance, column, value)
        check.is_true(
            model_instance.save(session), f"The save succeed : {model_instance}"
        )
        check.is_none(model_instance._errors, "The instance have no error")

    def test_update(self, session: TestingSessionLocal):
        model_instance = getattr(fake_model, self.fake_model)(session)
        check.is_true(
            model_instance.update(session), f"The update succeed : {model_instance}"
        )
        check.is_none(model_instance._errors, "The instance have no error")
        for column, column_type in self.default_columns.items():
            if column_type == "model":
                method = f"fake_{column}"
                if method in dir(fake_model):
                    value = getattr(fake_model, method)(session).id
                column = f"{column}_id"
            else:
                value = SwitchFake.fake(attribute_type=column_type)
            check.is_true(
                model_instance.update(session, **{column: value}),
                f"The update succeed with attribute '{column}' and value '{value}' : {model_instance}",
            )
            check.is_none(model_instance._errors, "The instance have no error")
        check.is_false(
            model_instance.update(session, wrong_column="wrong test"),
            "The update failed with wrong attribute 'wrong_column'",
        )
        check.is_not_none(model_instance._errors, "The instance have an error")
        check.is_false(
            model_instance.update(session, id="other wrong test"),
            "The update failed with wrong type of value for attribute 'id'",
        )
        check.is_not_none(model_instance._errors, "The instance have an error")

    def test_count(self, session: TestingSessionLocal):
        model_instance1 = getattr(fake_model, self.fake_model)(session)
        model_instance2 = getattr(fake_model, self.fake_model)(session)
        model_instance3 = getattr(fake_model, self.fake_model)(session)
        check.equal(
            self.class_model.count(session, id=model_instance1.id),
            1,
            "The count is 1 (by existing id)",
        )
        check.equal(
            self.class_model.count(session, id=model_instance3.id + 1),
            0,
            "The count is 0 (by not existing id)",
        )
        check.equal(
            self.class_model.count(
                session,
                id={
                    "in_": [model_instance1.id, model_instance2.id, model_instance3.id]
                },
            ),
            3,
            "The count is 3 (by list)",
        )
        check.equal(
            self.class_model.count(
                session,
                id={
                    "in_": (model_instance1.id, model_instance2.id, model_instance3.id)
                },
            ),
            3,
            "The count is 3 (by tuple)",
        )
        check.equal(
            self.class_model.count(
                session,
                id={
                    "in_": {model_instance1.id, model_instance2.id, model_instance3.id}
                },
            ),
            3,
            "The count is 3 (by set)",
        )

    def test_create(self, session: TestingSessionLocal):
        model_instance = self.class_model.create(session)
        check.is_none(
            model_instance.id, f"The instance doesn't have id : {model_instance}"
        )
        check.is_not_none(model_instance._errors, "The instance have an error")
        columns = {}
        for column, column_type in self.default_columns.items():
            if column_type == "model":
                method = f"fake_{column}"
                if method in dir(fake_model):
                    value = getattr(fake_model, method)(session).id
                column = f"{column}_id"
            else:
                value = SwitchFake.fake(attribute_type=column_type)
            columns[column] = value
        model_instance = self.class_model.create(session, **columns)
        check.is_not_none(
            model_instance.id, f"The instance have an id : {model_instance}"
        )
        check.is_none(
            model_instance._errors,
            f"The instance have no error : {model_instance._errors}",
        )

    def test_find_by(self, session: TestingSessionLocal):
        model_instance = getattr(fake_model, self.fake_model)(session)
        model_id = model_instance.id
        check.equal(
            self.class_model.find_by(session, id=model_id),
            model_instance,
            f"The find_by succeed for model '{self.class_model}' and id '{model_id}': {model_instance}",
        )
        check.is_none(
            self.class_model.find_by(session, id=0),
            f"The find_by failed for model '{self.class_model}' and id '0'",
        )
        check.is_none(
            self.class_model.find_by(session),
            f"The find_by failed for model '{self.class_model}' and no column",
        )

    def test_delete_all(self, session: TestingSessionLocal):
        model_instance1 = getattr(fake_model, self.fake_model)(session)
        model_instance2 = getattr(fake_model, self.fake_model)(session)
        model_instance3 = getattr(fake_model, self.fake_model)(session)
        model_id1 = model_instance1.id
        model_id2 = model_instance2.id
        model_id3 = model_instance3.id
        check.is_true(
            self.class_model.delete_all(session, id=model_id1),
            "Delete the first object succeed",
        )
        check.is_none(
            self.class_model.find_by(session, id=model_id1),
            "The instance can't be find after delete",
        )
        check.equal(
            self.class_model.find_by(session, id=model_id2),
            model_instance2,
            "The instance not deleted is found",
        )
        check.is_true(
            self.class_model.delete_all(session, id={"in_": [model_id2, model_id3]}),
            "Delete the other objects succeed",
        )
        check.equal(
            self.class_model.count(session, id={"in_": [model_id2, model_id3]}),
            0,
            "The instances deleted can't be found",
        )

    def test_where(self, session: TestingSessionLocal):
        model_instance1 = getattr(fake_model, self.fake_model)(session)
        model_instance2 = getattr(fake_model, self.fake_model)(session)
        model_instance3 = getattr(fake_model, self.fake_model)(session)
        model_instances = self.class_model.where(session)
        check.is_in(
            model_instance1,
            model_instances,
            "The first instance is in the global search",
        )
        check.is_in(
            model_instance2,
            model_instances,
            "The second instance is in the global search",
        )
        check.is_in(
            model_instance3,
            model_instances,
            "The third instance is in the global search",
        )
        model_instances = self.class_model.where(session, id=model_instance1.id)
        check.equal(
            len(model_instances),
            1,
            f"Search with id={model_instance1.id} have only one result",
        )
        check.is_in(
            model_instance1,
            model_instances,
            "The first instance is the searched instance",
        )
        check.is_not_in(
            model_instance2,
            model_instances,
            "The second instance isn't the searched instance",
        )
        check.is_not_in(
            model_instance3,
            model_instances,
            "The third instance isn't the searched instance",
        )
        model_instances = self.class_model.where(
            session, id={"in_": (model_instance1.id, model_instance2.id)}
        )
        check.equal(
            len(model_instances),
            2,
            f"Search with id in {(model_instance1.id, model_instance2.id)} have two results",
        )
        check.is_in(
            model_instance1, model_instances, "The first instance is in the result"
        )
        check.is_in(
            model_instance2, model_instances, "The second instance is in the result"
        )
        check.is_not_in(
            model_instance3, model_instances, "The third instance isn't in the result"
        )
        model_instances = self.class_model.where(
            session,
            id={"in_": (model_instance1.id, model_instance2.id, model_instance3.id)},
            limit=2,
            offset=1,
        )
        check.equal(
            len(model_instances),
            2,
            f"Search with id in {(model_instance1.id, model_instance2.id, model_instance3.id)}, limit=2 and offset=1 have two results",
        )
        check.is_not_in(
            model_instance1, model_instances, "The first instance isn't in the result"
        )
        check.is_in(
            model_instance2, model_instances, "The second instance is in the result"
        )
        check.is_in(
            model_instance3, model_instances, "The third instance is in the result"
        )
        model_instances = self.class_model.where(
            session,
            id={"in_": (model_instance1.id, model_instance2.id, model_instance3.id)},
            limit=2,
            offset=1,
            order_by={"id": "desc"},
        )
        check.equal(
            len(model_instances),
            2,
            f"Search with id in {(model_instance1.id, model_instance2.id, model_instance3.id)}, limit=2, offset=1 and order by id desc have two results",
        )
        check.is_in(
            model_instance1, model_instances, "The first instance is in the result"
        )
        check.is_in(
            model_instance2, model_instances, "The second instance is in the result"
        )
        check.is_not_in(
            model_instance3, model_instances, "The third instance isn't in the result"
        )
        model_instances = self.class_model.where(
            session, id={"between": [model_instance2.id, model_instance3.id]}
        )
        check.equal(
            len(model_instances),
            2,
            f"Search with id between {model_instance2.id} and {model_instance3.id} have two results",
        )
        check.is_not_in(
            model_instance1,
            model_instances,
            "The id of the first instance isn't between the id of second and third instances",
        )
        check.is_in(
            model_instance2,
            model_instances,
            "The id of the second instance is between the id of second and third instances",
        )
        check.is_in(
            model_instance3,
            model_instances,
            "The id of the third instance is between the id of second and third instances",
        )
        model_instances = self.class_model.where(session, id={"wrong_command": 0})
        check.equal(
            len(model_instances), 0, "Search id with wrong command have no result"
        )
        model_instances = self.class_model.where(session, wrong_column=0)
        check.equal(len(model_instances), 0, "Search with wrong column have no result")

    def test_where_like(self, session: TestingSessionLocal):
        if self.like_test:
            model_instance1 = getattr(fake_model, self.fake_model)(session)
            model_instance2 = getattr(fake_model, self.fake_model)(session)
            model_instance3 = getattr(fake_model, self.fake_model)(session)
            model_like1 = getattr(model_instance1, self.like_test)
            model_like2 = getattr(model_instance2, self.like_test)
            model_like3 = getattr(model_instance3, self.like_test)
            model_instances = self.class_model.where(
                session,
                **{self.like_test: {"like": {"other": model_like1, "escape": "\\"}}},
            )
            check.equal(len(model_instances), 1, "Search with like have one result")
            check.is_in(
                model_instance1,
                model_instances,
                "The first instance is the searched instance by like",
            )
            check.is_not_in(
                model_instance2,
                model_instances,
                "The second instance isn't the searched instance by like",
            )
            check.is_not_in(
                model_instance3,
                model_instances,
                "The third instance isn't the searched instance by like",
            )
            model_instances = self.class_model.where(
                session, **{self.like_test: {"ilike": model_like2.upper()}}
            )
            check.equal(len(model_instances), 1, "Search with ilike have one result")
            check.is_not_in(
                model_instance1,
                model_instances,
                "The first instance isn't the searched instance by ilike",
            )
            check.is_in(
                model_instance2,
                model_instances,
                "The second instance is the searched instance by ilike",
            )
            check.is_not_in(
                model_instance3,
                model_instances,
                "The third instance isn't the searched instance by ilike",
            )
            model_instances = self.class_model.where(
                session,
                **{
                    self.like_test: {
                        "like": [
                            {"other": model_like2},
                            {"other": model_like3},
                        ]
                    }
                },
            )
            check.equal(
                len(model_instances), 2, "Search with list like have two results"
            )
            check.is_not_in(
                model_instance1,
                model_instances,
                "The first instance isn't in the searched instances by list like",
            )
            check.is_in(
                model_instance2,
                model_instances,
                "The second instance is in the searched instances by list like",
            )
            check.is_in(
                model_instance3,
                model_instances,
                "The third instance is in the searched instances by list like",
            )
            model_instances = self.class_model.where(
                session, **{self.like_test: {"like": ["test"]}}
            )
            check.equal(len(model_instances), 0)

    def test_where_relation(self, session: TestingSessionLocal):
        for relation in self.relations:
            model_instance1 = getattr(fake_model, self.fake_model)(session)
            model_instance2 = getattr(fake_model, self.fake_model)(session)
            model_instance3 = getattr(fake_model, self.fake_model)(session)
            model_relation1 = getattr(model_instance1, relation)
            model_instances1 = self.class_model.where(
                session, **{relation: model_relation1}
            )
            model_instances2 = self.class_model.where(
                session, **{relation: {"id": model_relation1.id}}
            )
            model_instances3 = self.class_model.where(
                session, **{relation: {"id": {"in_": [model_relation1.id]}}}
            )
            model_instances4 = self.class_model.where(session, **{relation: "wrong"})
            check.equal(
                len(model_instances1), 1, "Search first relation have only one result"
            )
            check.is_in(
                model_instance1,
                model_instances1,
                "The first instance contains the searched relation",
            )
            check.is_not_in(
                model_instance2,
                model_instances1,
                "The second instance doesn't contain the searched relation",
            )
            check.is_not_in(
                model_instance3,
                model_instances1,
                "The third instance doesn't contain the searched relation",
            )
            check.equal(
                model_instances1, model_instances2, "Search by instance or id is equal"
            )
            check.equal(
                model_instances1,
                model_instances3,
                f"Search by instance '{model_relation1}' or by id in the list '{[model_relation1.id]}' is equal",
            )
            check.equal(
                len(model_instances4), 0, "Search relation wrong type have no result"
            )

    def test_where_association(self, session: TestingSessionLocal):
        if self.association_test:
            model_instance1 = getattr(fake_model, self.fake_model)(session)
            model_instance2 = getattr(fake_model, self.fake_model)(session)
            model_instance3 = getattr(fake_model, self.fake_model)(session)
            association1 = getattr(model_instance1, self.association_test)
            association2 = getattr(model_instance2, self.association_test)
            model_instances = self.class_model.where(
                session, **{self.association_test: "wrong value"}
            )
            check.equal(
                len(model_instances), 0, "Search with wrong type of value is empty"
            )
            model_instances = self.class_model.where(
                session,
                **{
                    self.association_test: association1,
                    "id": {"between": (model_instance1.id, model_instance3.id)},
                },
            )
            check.equal(
                len(model_instances), 1, "Search with association proxy give the result"
            )
            check.is_in(
                model_instance1, model_instances, "The first instance is in the result"
            )
            check.is_not_in(
                model_instance2,
                model_instances,
                "The second instance isn't in the result",
            )
            model_instances = self.class_model.where(
                session,
                **{
                    self.association_test: {
                        "id": {
                            "in_": [
                                association1.id,
                                association2.id,
                            ]
                        }
                    },
                },
            )
            check.equal(
                len(model_instances),
                2,
                "Search with association proxy in interval give the result (2)",
            )
            check.is_in(
                model_instance1, model_instances, "The first instance is in the result"
            )
            check.is_in(
                model_instance2, model_instances, "The second instance is in the result"
            )
            check.is_not_in(
                model_instance3,
                model_instances,
                "The third instance isn't in the result",
            )

    def test_options(self, session: TestingSessionLocal):
        if self.option_relation_test:
            fake_option_relation = f"fake_{self.option_relation_test[:-1]}"
            model_instance = getattr(fake_model, self.fake_model)(session)
            model_option1 = getattr(fake_model, fake_option_relation)(
                session, **{f"{self.class_name}_id": model_instance.id}
            )
            model_option2 = getattr(fake_model, fake_option_relation)(
                session, **{f"{self.class_name}_id": model_instance.id}
            )
            model_option3 = getattr(fake_model, fake_option_relation)(
                session, **{f"{self.class_name}_id": model_instance.id}
            )
            result = self.class_model.find_by(session, id=model_instance.id)
            relations = getattr(result, self.option_relation_test)
            check.equal(len(relations), 3, "All the relations are loaded (3)")
            session.expunge(result)
            result = self.class_model.find_by(
                session,
                id=model_instance.id,
                options={self.option_relation_test: {"id": model_option1.id}},
            )
            relations = getattr(result, self.option_relation_test)
            check.equal(len(relations), 1, "Only the first relation is loaded")
            session.expunge(result)
            result = self.class_model.find_by(
                session,
                id=model_instance.id,
                options={
                    self.option_relation_test: {
                        "id": {"in_": [model_option2.id, model_option3.id]}
                    }
                },
            )
            relations = getattr(result, self.option_relation_test)
            check.equal(len(relations), 2, "Only 2 relations are loaded")

    def test_with_options_join(self, session: TestingSessionLocal):
        for relation in self.relations:
            model_instance1 = getattr(fake_model, self.fake_model)(session)
            model_relation1 = getattr(model_instance1, relation)
            model_instance2 = getattr(fake_model, self.fake_model)(
                session, **{f"{relation}_id": model_relation1.id}
            )
            model_instance3 = getattr(fake_model, self.fake_model)(
                session, **{f"{relation}_id": model_relation1.id}
            )
            result = self.class_model.find_by(
                session,
                id=model_instance1.id,
                options={
                    relation: {
                        "join": {
                            self.class_model.__tablename__: {
                                "id": {"in_": [model_instance2.id, model_instance3.id]}
                            }
                        }
                    }
                },
            )
            model_instances3 = getattr(
                getattr(result, relation), self.class_model.__tablename__
            )
            check.equal(
                len(model_instances3), 2, "Only 2 relations are loaded (by dict)"
            )
            check.is_not_in(
                model_instance1,
                model_instances3,
                "The first instance isn't loaded",
            )
            check.is_in(
                model_instance2,
                model_instances3,
                "The second instance is loaded",
            )
            check.is_in(
                model_instance3,
                model_instances3,
                "The third instance is loaded",
            )
            session.reset()
            result = self.class_model.find_by(
                session,
                id=model_instance1.id,
                options={relation: {"join": self.class_model.__tablename__}},
            )
            model_instances1 = getattr(
                getattr(result, relation), self.class_model.__tablename__
            )
            check.equal(len(model_instances1), 3, "All relations are loaded (by str)")
            session.reset()
            result = self.class_model.find_by(
                session,
                id=model_instance1.id,
                options={relation: {"join": [self.class_model.__tablename__]}},
            )
            model_instances2 = getattr(
                getattr(result, relation), self.class_model.__tablename__
            )
            check.equal(len(model_instances2), 3, "All relations are loaded (by list)")
            session.reset()
            model_instance4 = getattr(fake_model, self.fake_model)(session)
            model_relation4 = getattr(model_instance4, relation)
            result = self.class_model.where(
                session,
                id={"in_": [model_instance1.id, model_instance4.id]},
                options={
                    relation: {
                        self.class_model.__tablename__: {"id": model_instance4.id}
                    }
                },
            )
            result_relation1 = getattr(result[0], relation)
            result_relation2 = getattr(result[1], relation)
            check.is_none(result_relation1, "When filtered, first don't have relation")
            check.equal(
                result_relation2, model_relation4, "When filtered, second have relation"
            )
