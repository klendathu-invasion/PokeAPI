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


class Card(BaseModel):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    tag = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    local_tag = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    regulation_mark = Column(Text, nullable=False)
    suffix = Column(Text, nullable=True)
    evolve_from = Column(Text, nullable=True)
    illustrator = Column(Text, nullable=True)

    rarity = Column(Integer, nullable=True)
    stage = Column(Integer, nullable=True)
    hp = Column(Integer, nullable=True)
    level = Column(Integer, nullable=True)
    retreat = Column(Integer, nullable=True)

    # should be array
    energy_types = Column(ARRAY(Integer), nullable=True)
    pokedex_numbers = Column(ARRAY(Integer), nullable=True)

    expanded = Column(Boolean, nullable=False)
    standard = Column(Boolean, nullable=False)

    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    PrimaryKeyConstraint("id")

    # user = relationship("User", back_populates="wishes")
