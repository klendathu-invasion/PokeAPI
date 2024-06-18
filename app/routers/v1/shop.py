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

uniq_shop = CheckUniqHelper(name="name", equal_list=["user_id"], ilike_list=["name"])
router_shop = RouterModelHelper(name="shop", parents=["user"], uniq_list=[uniq_shop])


@router.post("/", response_model=schemas.shop.Shop, status_code=status.HTTP_201_CREATED)
def create_shop(shop: schemas.shop.ShopBase, db: Session = Depends(Dependency.get_db)):
    return router_shop.create(db, shop.model_dump())


@router.get("/{shop_id}", response_model=schemas.shop.Shop)
def read_shop(shop_id: int, db: Session = Depends(Dependency.get_db)):
    return router_shop.read(db, shop_id)


@router.get("/user/{user_id}", response_model=list[schemas.shop.Shop])
def list_shops_by_user(user_id: int, db: Session = Depends(Dependency.get_db)):
    return router_shop.list(db, query={"user_id": user_id})


@router.put(
    "/{shop_id}",
    response_model=schemas.shop.Shop,
    description="The endpoint to update information about the shop with the requested id.",
    response_description="The shop updated",
)
def update_shop(
    shop_id: int,
    new_shop: schemas.shop.ShopUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_shop.update(db, shop_id, new_shop.model_dump())


@router.delete("/{shop_id}")
def delete_shop(shop_id: int, db: Session = Depends(Dependency.get_db)):
    return router_shop.delete(db, shop_id)
