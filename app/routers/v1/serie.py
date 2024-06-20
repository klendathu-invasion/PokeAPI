from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_serie = RouterModelHelper(name="serie", parents=[], uniq_list=[])


@router.get("/{serie_id}", response_model=schemas.serie.Serie)
def read_serie(serie_id: int, db: Session = Depends(Dependency.get_db)):
    return router_serie.read(db, serie_id)


@router.get("", response_model=list[schemas.serie.SerieList])
def list_series(db: Session = Depends(Dependency.get_db)):
    return router_serie.list(db, query={})


@router.get("/name/{name}", response_model=list[schemas.serie.SerieList])
def list_series_by_name(name: str, db: Session = Depends(Dependency.get_db)):
    return router_serie.list(db, query={"name": {"ilike": f"%{name}%"}})
