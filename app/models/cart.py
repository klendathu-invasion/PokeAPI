from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Cart(BaseModel):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)

    PrimaryKeyConstraint("id")
    UniqueConstraint("product_id", "user_id")

    product = relationship("Product", back_populates="carts")
    user = relationship("User", back_populates="carts")
