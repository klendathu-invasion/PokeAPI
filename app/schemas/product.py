from typing import Annotated

from pydantic import ConfigDict, StringConstraints, confloat, field_validator

from .custom_base import CustomBase
from .shop import Shop


class ProductUpdate(CustomBase):
    name: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None
    price: confloat(gt=True) | None = None
    description: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None


class ProductBase(CustomBase):
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    shop_id: int
    price: confloat(gt=True)
    description: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None


class Product(ProductBase):
    id: int
    shop: Shop
    model_config = ConfigDict(from_attributes=True)


class ProductComplete(Product):
    pass
