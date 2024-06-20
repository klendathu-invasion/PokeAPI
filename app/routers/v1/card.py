from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_card = RouterModelHelper(name="card", parents=[], uniq_list=[])


@router.get("/{card_id}", response_model=schemas.card.Card)
def read_card(card_id: int, db: Session = Depends(Dependency.get_db)):
    return router_card.read(db, card_id)


@router.get("", response_model=list[schemas.card.CardList])
def list_cards(db: Session = Depends(Dependency.get_db)):
    return router_card.list(db, query={})


@router.get("/name/{name}", response_model=list[schemas.card.CardList])
def list_cards_by_name(name: str, db: Session = Depends(Dependency.get_db)):
    return router_card.list(db, query={"name": {"ilike": f"%{name}%"}})
