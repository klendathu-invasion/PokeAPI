from sqlalchemy import Column, PrimaryKeyConstraint, String

from .base_model import BaseModel


class AlembicVersion(BaseModel):
    __tablename__ = "alembic_version"

    version_num = Column(String, primary_key=True)
    PrimaryKeyConstraint("version_num")
