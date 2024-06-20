from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.orm import relationship

from ..config.constants import CASCADE_ALL_DELETE
from .base_model import BaseModel


class Serie(BaseModel):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    tag = Column(Text, nullable=False)
    logo = Column(Text, nullable=False)
    symbol_tag = Column(Text, nullable=False)

    first_edition_count = Column(Integer, nullable=True)
    holo_count = Column(Integer, nullable=True)
    normal_count = Column(Integer, nullable=True)
    official_count = Column(Integer, nullable=True)
    reverse_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)

    expanded = Column(Boolean, nullable=False)
    standard = Column(Boolean, nullable=False)

    realease = Column(Date)

    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    PrimaryKeyConstraint("id")

    block_id = Column(
        Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False
    )
    block = relationship("Block", back_populates="series")
