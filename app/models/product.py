from sqlalchemy import Column, Float, ForeignKey, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    shop_id = Column(
        Integer,
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    )

    PrimaryKeyConstraint("id")

    shop = relationship("Shop", back_populates="products")
    carts = relationship("Cart", back_populates="product", cascade=CASCADE_ALL_DELETE)

    user_id = association_proxy("shop", "user_id")
    user_ids = association_proxy("shop", "user_ids")
