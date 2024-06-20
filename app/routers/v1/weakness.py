from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_weakness = RouterModelHelper(name="weakness", parents=[], uniq_list=[])


@router.get("/{weakness_id}", response_model=schemas.weakness.Weakness)
def read_weakness(weakness_id: int, db: Session = Depends(Dependency.get_db)):
    return router_weakness.read(db, weakness_id)


@router.get("", response_model=list[schemas.weakness.WeaknessList])
def list_weaknesss(db: Session = Depends(Dependency.get_db)):
    return router_weakness.list(db, query={})
