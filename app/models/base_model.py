from fastapi.logger import logger
from sqlalchemy import Column, ForeignKey, Integer, not_
from sqlalchemy.ext.associationproxy import ObjectAssociationProxyInstance
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session, joinedload, relationship
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

from .. import errors
from . import Base


class BaseModel(Base):
    __abstract__ = True
    _errors: Exception | None = None

    def __repr__(self) -> str:
        """This function get the str of an instance.

        :returns: str

        """
        columns = [
            f"{key}={getattr(self, key)}" for key in self.__mapper__.columns.keys()
        ]
        return f"{self.__class__.__name__}({', '.join(columns)})"

    def as_dict(self) -> dict:
        """This function get all the attributes of the instance (except attributes with name starting with _) in a dict.

        :param self: the instance
        :returns: dict

        """
        keys = list(self.__dict__.keys())
        return {key: getattr(self, key) for key in keys if not key.startswith("_")}

    def delete(self, db: Session) -> bool:
        """This function delete the instance from the database and return True.

        :param self: the instance
        :param db: the connection with the database
        :type db: Session
        :returns: True

        """
        self._errors = None
        db.delete(self)
        db.commit()
        return True

    def save(self, db: Session) -> bool:
        """This function save the instance in the database and return a bool.

        :param self: the instance
        :param db: the connection with the database
        :type db: Session
        :returns: bool

        """
        self._errors = None
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
        except Exception as inst:
            self._errors = inst
            db.rollback()
            return False
        return True

    def update(self, db: Session, **columns):
        """This function update the instance in the database and return a bool.

        :param self: the instance
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to change
        :type db: Session
        :returns: bool

        """
        self._errors = None
        invalid_columns = []
        _columns_nullable = []
        for _name, _column in self.__table__.columns.items():
            if _column.nullable:
                _columns_nullable.append(_name)
        for key in columns:
            if key in self.__table__.columns.keys():
                if (
                    columns[key] is not None
                    or key in _columns_nullable
                    and getattr(self, key) != columns[key]
                ):
                    setattr(self, key, columns[key])
            else:
                invalid_columns.append(key)
        if invalid_columns:
            self._errors = errors.columns_error.ColumnsError(
                tablename=self.__tablename__, columns=invalid_columns
            )
            return False
        return self.save(db)

    @classmethod
    def count(cls, db: Session, **columns):
        """This function count all the instances in the database with the requested columns.

        :param cls: the class
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to find
        :type db: Session
        :returns: the number of instances match with requested parameter

        """
        return cls._query(db, **columns).count()

    @classmethod
    def create(cls, db: Session, **columns):
        """This function create an instance in the database.

        :param cls: the class
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to create
        :type db: Session
        :returns: an instance

        """
        # control the existence of the column
        _model_cls = cls(**columns)
        _model_cls.save(db)
        return _model_cls

    @classmethod
    def find_by(cls, db: Session, **columns):
        """This function find the first instance in the database with the requested columns.

        :param cls: the class
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to find
        :type db: Session
        :returns: an instance or None

        """
        if not columns:
            return None
        return cls._query(db, **columns).first()

    @staticmethod
    def _get_like_expression(attribute, operator, values):
        """This function prepare query when operator is a like or ilike and return a BinaryExpression.

        :param attribute: the attribute of the query
        :param operator: the operator of the query (like or ilike)
        :param values: the values to search
        :returns: Union[BinaryExpression, None]

        """
        if isinstance(values, list):
            tmp_expression = None
            for value in values:
                if isinstance(value, dict):
                    if tmp_expression is None:
                        tmp_expression = getattr(attribute, operator)(**value)
                    else:
                        tmp_expression = tmp_expression.__or__(
                            getattr(attribute, operator)(**value)
                        )
                else:
                    return None
            return tmp_expression
        elif isinstance(values, dict):
            return getattr(attribute, operator)(**values)
        return getattr(attribute, operator)(values)

    @classmethod
    def _get_condition_column(
        cls, model_relation, key, **columns
    ) -> BinaryExpression | None:
        """This function prepare query with a column of a model and return a BinaryExpression.

        :param model_relation: the model for the query
        :param key: the name of the column
        :param columns: keyword arguments with the column to find
        :returns: BinaryExpression | None

        """
        operator: str = "__eq__"
        attribute = getattr(model_relation, key)
        value = columns[key]

        # check if the value is a dict
        if isinstance(value, dict):
            common = list(set(value) & set(dir(attribute)))

            # check if the value is a dict and have only one key and is a method of the attribute
            if len(common) == 1 == len(value) and callable(
                getattr(attribute, common[0])
            ):
                operator = common[0]
                value = value[operator]
            else:
                return None

        # call the method operator of attribute with the argument(s) 'value'
        if operator in ["like", "ilike"]:
            return cls._get_like_expression(attribute, operator, value)

        elif operator not in ["in_", "not_in"] and (
            isinstance(value, dict)
            or isinstance(value, list)
            or isinstance(value, set)
            or isinstance(value, tuple)
        ):
            return getattr(attribute, operator)(*value)
        return getattr(attribute, operator)(value)

    @staticmethod
    def _get_condition_relationship(
        model_relation, key, **columns
    ) -> UnaryExpression | BinaryExpression | dict | None:
        """This function prepare query with a relationship of a model and return a BinaryExpression or a dict.

        :param model_relation: the model for the query
        :param key: the name of the relationship
        :param columns: keyword arguments with the column to find
        :returns: BinaryExpression | dict | None

        """
        attribute = getattr(model_relation, key)
        sub_model = attribute.prop.mapper.__dict__["class_"]

        # if the value is an object or list of searched class
        if isinstance(columns[key], list) or isinstance(columns[key], sub_model):
            return getattr(attribute, "__eq__")(columns[key])

        # not any for relationship
        elif columns[key] == "sa_not_":
            return not_(attribute.any())

        # if the value is a dict
        elif isinstance(columns[key], dict):
            sub_relation = {}
            sub_relation["class"] = sub_model
            sub_relation["query"] = attribute

            # check the attribute uselist to know if need to use method 'any' or 'has'
            if model_relation.__mapper__.relationships[key].uselist:
                sub_relation["method"] = "any"
            else:
                sub_relation["method"] = "has"
            return sub_relation
        return None

    @classmethod
    def _query_simple_column(
        cls, attributes: list, model_relation, key, **columns
    ) -> bool:
        """This function prepare query with simple column of a model and return a bool with the state of the request.

        :param cls: the class
        :param attributes: a list of the queries
        :param model_relation: the model for the query
        :param key: the name of the column
        :param columns: keyword arguments with the column to find
        :type attributes: list
        :returns: bool

        """
        attribute = cls._get_condition_column(model_relation, key, **columns)
        if attribute is None:
            return False

        attributes.append(attribute)
        return True

    @classmethod
    def _query_relationship(
        cls, attributes: list, model_relation, key, relations, db_query, **columns
    ) -> tuple:
        """This function prepare query with a relationship of a model and return a tuple.

        :param cls: the class
        :param attributes: a list of the queries
        :param model_relation: the model for the query
        :param key: the name of the relationship
        :param relations: a list of parent relations
        :param db_query: the query
        :param columns: keyword arguments with the column to find
        :type attributes: list
        :returns: tuple

        """
        attribute = cls._get_condition_relationship(model_relation, key, **columns)
        if isinstance(attribute, UnaryExpression | BinaryExpression):
            attributes.append(attribute)
        elif isinstance(attribute, dict):
            # get the query associate with the relation
            db_query = cls._sub_query([attribute] + relations, db_query, **columns[key])
        # if the value is neither an object of searched class neither a dict then is an error
        else:
            return (db_query, False)
        return (db_query, True)

    @classmethod
    def _query_association_proxy(
        cls, attributes: list, model_relation, key, relations, db_query, **columns
    ) -> tuple:
        """This function prepare query with a relationship of a model and return a tuple.

        :param cls: the class
        :param attributes: a list of the queries
        :param model_relation: the model for the query
        :param key: the name of the relationship
        :param relations: a list of parent relations
        :param db_query: the query
        :param columns: keyword arguments with the column to find
        :type attributes: list
        :returns: tuple

        """
        attribute = getattr(model_relation, key)
        tmp_attribute = attribute
        if not isinstance(attribute, ObjectAssociationProxyInstance):
            return (db_query, False)
        while isinstance(tmp_attribute, ObjectAssociationProxyInstance):
            tmp_attribute = getattr(
                tmp_attribute.target_class, tmp_attribute.value_attr
            )
        sub_model = tmp_attribute.prop.mapper.__dict__["class_"]

        # if the value is an object of searched class
        if isinstance(columns[key], sub_model):
            attributes.append(getattr(attribute, "__eq__")(columns[key]))

        # if the value is a dict
        elif isinstance(columns[key], dict):
            sub_relation = {}
            sub_relation["class"] = sub_model
            sub_relation["query"] = attribute
            sub_relation["method"] = "has"

            # get the query associate with the relation
            db_query = cls._sub_query(
                [sub_relation] + relations, db_query, **columns[key]
            )

        # if the value is neither an object of searched class neither a dict then is an error
        else:
            return (db_query, False)
        return (db_query, True)

    @classmethod
    def _query_columns(
        cls, attributes: list, model_relation, key, relations, db_query, **columns
    ) -> tuple:
        """This function check if the key is in the model_relation and return a tuple.

        :param cls: the class
        :param attributes: a list of the queries
        :param model_relation: the model for the query
        :param key: the name to search in the model
        :param relations: a list of parent relations
        :param db_query: the query
        :param columns: keyword arguments with the column to find
        :type attributes: list
        :returns: tuple

        """
        # if key is a column of the class
        if key in model_relation.__mapper__.columns.keys():
            return (
                db_query,
                cls._query_simple_column(attributes, model_relation, key, **columns),
            )
        # if key is a relation of the class
        elif key in model_relation.__mapper__.relationships.keys():
            return cls._query_relationship(
                attributes, model_relation, key, relations, db_query, **columns
            )
        elif key in model_relation.__mapper__.all_orm_descriptors.keys():
            return cls._query_association_proxy(
                attributes, model_relation, key, relations, db_query, **columns
            )

        # if key not in the class
        return (db_query, False)

    @classmethod
    def _build_query_by_attribute(cls, relations, attributes, db_query):
        """This function build a query.

        :param cls: the class
        :param relations: a list of parent relations
        :param attributes: the attributes to build the query
        :param db_query: the query
        :returns: a query

        """
        tmp_query = attributes
        # build the argument of the query from last to first relation
        for relation in relations:
            relation_query = relation["query"]
            relation_method = relation["method"]
            tmp_method = getattr(relation_query, relation_method)
            if isinstance(tmp_query, list):
                tmp = None
                for query in tmp_query:
                    if tmp is None:
                        tmp = query
                    else:
                        tmp = tmp.__and__(query)
                tmp_query = tmp
            tmp_query = tmp_method(tmp_query)

        # build the query with the attributes
        return (
            db_query.where(*tmp_query)
            if isinstance(tmp_query, list)
            else db_query.where(tmp_query)
        )

    @classmethod
    def _sub_query(cls, relations, db_query, **columns):
        """This function is a recursive to prepare a query for the instances in database with the requested columns.

        :param cls: the class
        :param relations: a list of parent relations
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to find
        :type db: Session
        :returns: a query

        """
        # if relations is empty -> use the class cls
        # else we use the class in first relation
        if len(relations) == 0:
            model_relation = cls
        else:
            model_relation = relations[0]["class"]
        attributes = []
        error = False

        # for each key in the columns, check if key is a column or a relation or not in table
        for key in columns:
            db_query, result = cls._query_columns(
                attributes, model_relation, key, relations, db_query, **columns
            )
            if not result:
                error = True

        # if attribute isn't empty
        if attributes:
            db_query = cls._build_query_by_attribute(relations, attributes, db_query)
        # if there is an error then return an empty query
        if error:
            db_query = db_query.where(False)
        return db_query

    @classmethod
    def _get_argument_options(
        cls, model_relation, key: str, options: dict
    ) -> UnaryExpression | BinaryExpression | None:
        """This function get the BinaryExpression of the key from the options parameter.

        :param cls: the class
        :param model_relation: the model for the query
        :param key: the name to search in the model
        :param options: the options of the query
        :type key: str
        :type options: dict
        :returns: BinaryExpression | None

        """
        if key in model_relation.__mapper__.columns.keys():
            return cls._get_condition_column(model_relation, key, **options)
        elif key in model_relation.__mapper__.relationships.keys():
            attribute = cls._get_condition_relationship(model_relation, key, **options)
            if isinstance(attribute, UnaryExpression | BinaryExpression):
                return attribute
            elif isinstance(attribute, dict):
                relation_query = attribute["query"]
                relation_method = attribute["method"]
                tmp_method = getattr(relation_query, relation_method)
                arguments, _ = cls._build_options(attribute["class"], options[key])
                return tmp_method(*arguments)

    @classmethod
    def _build_options_join(cls, model_relation, options) -> list:
        """This function get a list of the join option in the query.

        :param cls: the class
        :param model_relation: the model for the query
        :param options: the options of the query
        :returns: list

        """
        join_options = []
        if isinstance(options, dict):
            for key, value in options.items():
                if key in model_relation.__mapper__.relationships.keys():
                    attribute = getattr(model_relation, key)
                    sub_model = attribute.prop.mapper.__dict__["class_"]
                    attributes, sub_options = cls._build_options(sub_model, value)
                    join_options.append(
                        joinedload(attribute.and_(*attributes)).options(*sub_options)
                    )
        elif isinstance(options, list):
            for key in options:
                if key in model_relation.__mapper__.relationships.keys():
                    attribute = getattr(model_relation, key)
                    join_options.append(joinedload(attribute))
        elif isinstance(options, str):
            if options in model_relation.__mapper__.relationships.keys():
                attribute = getattr(model_relation, options)
                join_options.append(joinedload(attribute))
        return join_options

    @classmethod
    def _build_options(cls, model_relation, options) -> tuple[list, list]:
        """This function build the options queried by giving a tuple of arguments and join options.

        :param cls: the class
        :param model_relation: the model for the query
        :param options: the options of the query
        :returns: tuple[list, list]

        """
        join_options = []
        arguments = []

        if isinstance(options, dict):
            for key, value in options.items():
                if key == "join":
                    join_options = cls._build_options_join(model_relation, value)
                else:
                    argument = cls._get_argument_options(model_relation, key, options)
                    if argument is not None:
                        arguments.append(argument)

        return arguments, join_options

    @classmethod
    def _query_options(cls, db_query, options: dict):
        """This function prepare the query by options.

        :param cls: the class
        :param db_query: the query
        :param options: the options of query
        :type options: dict
        :returns: a query

        """
        joineds = []

        # for each key in the columns, check if key is a column or a relation or not in table
        for key, value in options.items():
            if key in cls.__mapper__.relationships.keys():
                attribute = getattr(cls, key)
                sub_model = attribute.prop.mapper.__dict__["class_"]
                arguments, join_options = cls._build_options(sub_model, value)
                # joineds.append(argument)
                joineds.append(
                    joinedload(attribute.and_(*arguments)).options(*join_options)
                )

        if joineds:
            db_query = db_query.options(*joineds)
        return db_query

    @classmethod
    def _query_order_by(cls, model_relation, db_query, order_by):
        """This function prepare the query by ordering.

        :param cls: the class
        :param model_relation: the model for the query
        :param db_query: the query
        :param order_by: the order_by queried
        :returns: a query

        """
        arguments_order_by = []
        if isinstance(order_by, dict):
            for key, value in order_by.items():
                if key in model_relation.__mapper__.columns.keys():
                    attribute = getattr(model_relation, key)
                    if value in ["asc", "desc"]:
                        attribute = getattr(attribute, value)()
                    arguments_order_by.append(attribute)
        return db_query.order_by(*arguments_order_by)

    @classmethod
    def _query(
        cls,
        db: Session,
        options: dict = {},
        order_by=None,
        limit: int | None = None,
        offset: int | None = None,
        having=None,
        group_by=None,
        **columns,
    ):
        """This function prepare a query for the instances in database with the requested columns.

        :param cls: the class
        :param db: the connection with the database
        :param options: options of the query
        :param order_by: order by for query
        :param limit: limit for query
        :param offset: offset for query
        :param columns: keyword arguments with the columns to find
        :type limit: int
        :type offset: int
        :type db: Session
        :returns: a query

        """
        db_query = db.query(cls)
        db_query = cls._sub_query([], db_query, **columns)
        if options:
            db_query = cls._query_options(db_query, options)
        if order_by:
            db_query = cls._query_order_by(cls, db_query, order_by)
        if limit:
            db_query = db_query.limit(limit)
        if offset:
            db_query = db_query.offset(offset)
        if group_by:
            db_query = db_query.group_by(group_by)
        if having:
            db_query = db_query.having(having)

        return db_query

    @classmethod
    def delete_all(cls, db: Session, **columns):
        """This function find all the instances in the database with the requested columns.

        :param cls: the class
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to find
        :type db: Session
        :returns: a list of instance

        """
        return cls._query(db, **columns).delete(synchronize_session=False)

    @classmethod
    def where(cls, db: Session, **columns):
        """This function find all the instances in the database with the requested columns.

        :param cls: the class
        :param db: the connection with the database
        :param columns: keyword arguments with the columns to find
        :type db: Session
        :returns: a list of instance

        """
        return cls._query(db, **columns).all()
