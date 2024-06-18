import json
import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from fastapi.logger import logger
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from sqlalchemy import MetaData, create_mock_engine
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config.env import settings
from ..config.metadata_tag import MetadataTag
from ..config.seeds import Seed
from ..utils.dependency import Dependency

api_router = APIRouter(
    prefix=MetadataTag.__tag_debug__.prefix, tags=[MetadataTag.__tag_debug__.name]
)


def get_table_json(
    columns: list, table_all: list, tablename: str, result: dict, save: bool
):
    table_json = [
        {columns[i]: value for i, value in enumerate(row)} for row in table_all
    ]
    result[tablename] = table_json
    filename = f"app/config/seeds/{tablename}.json"
    if not os.path.isfile(filename) and save:
        with open(filename, mode="w") as f:
            f.write(json.dumps(table_json, ensure_ascii=False, indent=4))


def get_table_sql(columns: list, table_all: list, tablename: str, result: dict):
    values_str = ""
    for value in table_all:
        values_str = f"{values_str}, {value}" if values_str else str(value)
    table_insert = f"INSERT INTO {tablename} {tuple(columns)} VALUES {values_str};"
    result[tablename] = table_insert


def get_tablenames():
    tables = models.Base.metadata.tables.values()
    tablenames = [table.name for table in tables]
    tablenames.sort()
    return tablenames


def write_coverage():
    coverage_lock_file = "coverage.lock"
    path = Path(coverage_lock_file)
    if not path.is_file():
        logger.info("create file coverage.lock")
        Path(coverage_lock_file).touch()
        subprocess.run(
            [
                "pytest",
                "--cov=app",
                "--cov-report",
                "term-missing",
                "--cov-report",
                "term:skip-covered",
                "--cov-report",
                "html",
            ]
        )
        Path(coverage_lock_file).unlink()


def write_schema(db: Session, schema_sql_file: str):
    def dump(sql, *multiparams, **params):
        f = sql.compile(dialect=db.bind.dialect)
        with open(schema_sql_file, "a") as fi:
            fi.write(str(f))

    metadata = MetaData()
    metadata.reflect(db.bind)
    e = create_mock_engine(
        str(db.bind.url),
        connect_args=(
            {"check_same_thread": False} if settings.database_engine == "sqlite" else {}
        ),
        executor=dump,
    )
    metadata.create_all(e, checkfirst=True)


@api_router.get("/all_users", response_model=list[schemas.user.UserBase])
def get_all_users(db: Session = Depends(Dependency.get_db)):
    list_users = db.query(models.user.User).all()
    return [schemas.user.UserBase(**user.as_dict()) for user in list_users]


@api_router.get("/tables")
def get_tables(
    mode: str = Query(enum=["json", "sql"]),
    save: bool = Query(enum=[False, True]),
    name: str = Query(None, enum=get_tablenames()),
    db: Session = Depends(Dependency.get_db),
):
    result = {}
    tables = list(models.Base.metadata.tables.values())
    tables.sort(key=lambda x: x.name)
    if name is not None:
        tables = [table for table in tables if table.name == name]
    for tablename in tables:
        table_all = db.query(tablename).all()
        columns = tablename.columns.keys()
        if table_all:
            if mode == "json":
                get_table_json(columns, table_all, tablename.name, result, save)
            elif mode == "sql":
                get_table_sql(columns, table_all, tablename.name, result)
    return result


@lru_cache()
@api_router.get("/coverage")
async def get_coverage(background_tasks: BackgroundTasks):
    if not Path("htmlcov/").exists():
        background_tasks.add_task(write_coverage)
        return JSONResponse(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            content={"message": "Please, wait..."},
        )
    coverage_zip = shutil.make_archive("coverage", "zip", "htmlcov/")
    return FileResponse(
        status_code=status.HTTP_200_OK,
        path=coverage_zip,
        filename="coverage.zip",
        media_type="application/zip",
    )


@lru_cache()
@api_router.get("/info")
def get_info():
    return settings


@lru_cache()
@api_router.get("/schema", response_class=PlainTextResponse)
def get_schema(db: Session = Depends(Dependency.get_db)):
    schema_sql_file = "./sql/schema.sql"
    if not Path(schema_sql_file).is_file():
        write_schema(db, schema_sql_file)
    with open(schema_sql_file) as f:
        response = "".join(f.readlines())
    return response


@api_router.get("/fill_tables")
def get_fill_tables(db: Session = Depends(Dependency.get_db)):
    logger.debug("fill the empty tables")
    Seed.initialize_table(db.bind)
    return {"message": "done"}


@api_router.get("/reset")
async def get_reset_database(
    background_tasks: BackgroundTasks, db: Session = Depends(Dependency.get_db)
):
    background_tasks.add_task(Seed.reset_database, db.bind)
    return {"message": "database is reseting"}
