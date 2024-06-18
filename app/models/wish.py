from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Wish(BaseModel):
    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    PrimaryKeyConstraint("id")

    user = relationship("User", back_populates="wishes")
