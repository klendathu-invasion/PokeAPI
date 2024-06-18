from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    PrimaryKeyConstraint,
    Text,
    sql,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    matricule = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    is_pro = Column(Boolean, nullable=False, default=False)
    last_connection_at = Column(TIMESTAMP)
    legals_at = Column(TIMESTAMP)
    legals_version = Column(Text)
    PrimaryKeyConstraint("id")

    admin = relationship("Admin", back_populates="user", cascade=CASCADE_ALL_DELETE)
    shops = relationship("Shop", back_populates="user", cascade=CASCADE_ALL_DELETE)
    shop_members = relationship(
        "ShopMember", back_populates="members", cascade=CASCADE_ALL_DELETE
    )
    wishes = relationship("Wish", back_populates="user", cascade=CASCADE_ALL_DELETE)
    carts = relationship("Cart", back_populates="user", cascade=CASCADE_ALL_DELETE)

    shop_ids = association_proxy("shop_members", "shop_ids")
