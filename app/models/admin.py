from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Admin(BaseModel):
    __tablename__ = "admins"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )

    PrimaryKeyConstraint("user_id")

    user = relationship("User", back_populates="admin")
