from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_resistance = RouterModelHelper(name="resistance", parents=[], uniq_list=[])


@router.get("/{resistance_id}", response_model=schemas.resistance.Resistance)
def read_resistance(resistance_id: int, db: Session = Depends(Dependency.get_db)):
    return router_resistance.read(db, resistance_id)


@router.get("", response_model=list[schemas.resistance.ResistanceList])
def list_resistances(db: Session = Depends(Dependency.get_db)):
    return router_resistance.list(db, query={})
