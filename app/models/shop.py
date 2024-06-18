from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Shop(BaseModel):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    PrimaryKeyConstraint("id")

    user = relationship("User", back_populates="shops")
    products = relationship(
        "Product", back_populates="shop", cascade=CASCADE_ALL_DELETE
    )
    members = relationship(
        "ShopMember", back_populates="shops", cascade=CASCADE_ALL_DELETE
    )

    user_ids = association_proxy("members", "user_ids")
