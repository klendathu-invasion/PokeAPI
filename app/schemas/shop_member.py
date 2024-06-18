from pydantic import ConfigDict

from .custom_base import CustomBase


class ShopMemberBase(CustomBase):
    shop_id: int
    user_id: int


class ShopMember(ShopMemberBase):
    model_config = ConfigDict(from_attributes=True)


class ShopMemberComplete(ShopMember):
    pass
