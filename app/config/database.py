from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .env import settings

engine = create_engine(
    settings.database_url,
    echo=settings.fastapi_env.value == "dev",
    connect_args=(
        {"check_same_thread": False} if settings.database_engine == "sqlite" else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
