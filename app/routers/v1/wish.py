from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)

uniq_wish = CheckUniqHelper(name="name", equal_list=["user_id"], ilike_list=["name"])
router_wish = RouterModelHelper(name="wish", parents=["user"], uniq_list=[uniq_wish])


@router.post("/", response_model=schemas.wish.Wish, status_code=status.HTTP_201_CREATED)
def create_wish(wish: schemas.wish.WishBase, db: Session = Depends(Dependency.get_db)):
    return router_wish.create(db, wish.model_dump())


@router.get("/{wish_id}", response_model=schemas.wish.Wish)
def read_wish(wish_id: int, db: Session = Depends(Dependency.get_db)):
    return router_wish.read(db, wish_id)


@router.get("/user/{user_id}", response_model=list[schemas.wish.Wish])
def list_wishes_by_user(user_id: int, db: Session = Depends(Dependency.get_db)):
    return router_wish.list(db, query={"user_id": user_id})


@router.put(
    "/{wish_id}",
    response_model=schemas.wish.Wish,
    description="The endpoint to update information about the wish with the requested id.",
    response_description="The wish updated",
)
def update_wish(
    wish_id: int,
    new_wish: schemas.wish.WishUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_wish.update(db, wish_id, new_wish.model_dump())


@router.delete("/{wish_id}")
def delete_wish(wish_id: int, db: Session = Depends(Dependency.get_db)):
    return router_wish.delete(db, wish_id)
