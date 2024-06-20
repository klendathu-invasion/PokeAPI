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


class Block(BaseModel):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    tag = Column(Text, nullable=False)
    logo = Column(Text, nullable=False)

    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    PrimaryKeyConstraint("id")

    series = relationship("Serie", back_populates="block", cascade=CASCADE_ALL_DELETE)
