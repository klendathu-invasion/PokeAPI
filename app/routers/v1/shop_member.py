from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.router import RouterLinkHelper
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)

router_shop_member = RouterLinkHelper(name="shop_member", relations=["shop", "user"])


@router.post(
    "/",
    response_model=schemas.shop_member.ShopMember,
    status_code=status.HTTP_201_CREATED,
)
def create_shop_member(
    shop_member: schemas.shop_member.ShopMemberBase,
    db: Session = Depends(Dependency.get_db),
):
    return router_shop_member.create(db, shop_member.model_dump())


@router.delete("/{shop_id}/{member_id}")
def delete_shop_member(
    shop_id: int, member_id: int, db: Session = Depends(Dependency.get_db)
):
    return router_shop_member.delete(db, {"shop_id": shop_id, "user_id": member_id})
