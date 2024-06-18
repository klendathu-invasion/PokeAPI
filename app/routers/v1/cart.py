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

router_cart = RouterModelHelper(name="cart", parents=["product", "user"], uniq_list=[])


@router.post("/", response_model=schemas.cart.Cart, status_code=status.HTTP_201_CREATED)
def create_cart(cart: schemas.cart.CartBase, db: Session = Depends(Dependency.get_db)):
    return router_cart.create(db, cart.model_dump())


@router.get("/{cart_id}", response_model=schemas.cart.Cart)
def read_cart(cart_id: int, db: Session = Depends(Dependency.get_db)):
    return router_cart.read(db, cart_id)


@router.get("/user/{user_id}", response_model=list[schemas.cart.CartList])
def list_carts_by_user(user_id: int, db: Session = Depends(Dependency.get_db)):
    return router_cart.list(db, query={"user_id": user_id})


@router.put(
    "/{cart_id}",
    response_model=schemas.cart.Cart,
    description="The endpoint to update information about the cart with the requested id.",
    response_description="The cart updated",
)
def update_cart(
    cart_id: int,
    new_cart: schemas.cart.CartUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_cart.update(db, cart_id, new_cart.model_dump())


@router.delete("/{cart_id}")
def delete_cart(cart_id: int, db: Session = Depends(Dependency.get_db)):
    return router_cart.delete(db, cart_id)
