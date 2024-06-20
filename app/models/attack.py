from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Attack(BaseModel):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    effect = Column(Text, nullable=False)
    dammage = Column(Text, nullable=True)

    costs = Column(ARRAY(Integer), nullable=True)

    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    PrimaryKeyConstraint("id")

    # user = relationship("User", back_populates="wishes")
