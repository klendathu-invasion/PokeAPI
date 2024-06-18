from pydantic import ConfigDict, conint

from .custom_base import CustomBase
from .product import Product
from .user import User


class CartUpdate(CustomBase):
    quantity: conint(gt=True) | None = None


class CartBase(CustomBase):
    product_id: int
    user_id: int
    quantity: conint(gt=True)


class Cart(CartBase):
    id: int
    product: Product
    user: User
    model_config = ConfigDict(from_attributes=True)


class CartList(CartBase):
    product: Product


class CartComplete(Cart):
    pass
