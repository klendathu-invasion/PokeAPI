from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class ShopMember(BaseModel):
    __tablename__ = "shop_members"

    shop_id = Column(
        Integer,
        ForeignKey("shops.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    PrimaryKeyConstraint("shop_id", "user_id")
    UniqueConstraint("shop_id", "user_id")

    shops = relationship("Shop", back_populates="members")
    members = relationship("User", back_populates="shop_members")

    shop_ids = association_proxy("shops", "id")
    user_ids = association_proxy("members", "id")
