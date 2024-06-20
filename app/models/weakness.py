from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Weakness(BaseModel):
    __tablename__ = "weaknesses"

    id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=False)
    energy_type = Column(Integer, nullable=True)

    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    PrimaryKeyConstraint("id")

    # user = relationship("User", back_populates="wishes")
