from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_attack = RouterModelHelper(name="attack", parents=[], uniq_list=[])


@router.get("/{attack_id}", response_model=schemas.attack.Attack)
def read_attack(attack_id: int, db: Session = Depends(Dependency.get_db)):
    return router_attack.read(db, attack_id)


@router.get("", response_model=list[schemas.attack.AttackList])
def list_attacks(db: Session = Depends(Dependency.get_db)):
    return router_attack.list(db, query={})


@router.get("/name/{name}", response_model=list[schemas.attack.AttackList])
def list_attacks_by_name(name: str, db: Session = Depends(Dependency.get_db)):
    return router_attack.list(db, query={"name": {"ilike": f"%{name}%"}})
