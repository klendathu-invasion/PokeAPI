from pydantic import BaseModel, Field

from .env import settings


class _MetadataTag(BaseModel):
    description: str
    name: str
    prefix: str = Field(pattern=r"^/[a-z0-9_]+$")

    def __init__(self, *, description: str, name: str, prefix: str | None = None):
        super().__init__(
            description=description,
            name=name,
            prefix=f"/{name}" if prefix is None else prefix,
        )


class MetadataTag(BaseModel):
    __tag_login__: _MetadataTag = _MetadataTag(
        name="login", description="Endpoints related to login data."
    )

    __tag_debug__: _MetadataTag = _MetadataTag(
        name="debug",
        description="Endpoints related to debug data (only visible in dev mode).",
    )

    __tag_admin__: _MetadataTag = _MetadataTag(
        name="admin", description="Endpoints related to the admin part."
    )

    __tag_user__: _MetadataTag = _MetadataTag(
        name="user", prefix="/users", description="Endpoints related to user data."
    )

    __tag_shop__: _MetadataTag = _MetadataTag(
        name="shop", description="Endpoints related to shop data."
    )

    __tag_product__: _MetadataTag = _MetadataTag(
        name="product", description="Endpoints related to product data."
    )

    __tag_shop_member__: _MetadataTag = _MetadataTag(
        name="shop_member", description="Endpoints related to shop member data."
    )

    __tag_cart__: _MetadataTag = _MetadataTag(
        name="cart", description="Endpoints related to cart data."
    )

    __tag_wish__: _MetadataTag = _MetadataTag(
        name="wish", description="Endpoints related to wish data."
    )

    __tag_visual__: _MetadataTag = _MetadataTag(
        name="visual", description="Endpoints to test html template."
    )

    @classmethod
    def tag_list(cls) -> list[_MetadataTag]:
        list_tags = [
            cls.__tag_login__.model_dump(),
            (
                cls.__tag_debug__.model_dump()
                if settings.fastapi_env.value in ["dev", "test"]
                else None
            ),
            (
                cls.__tag_visual__.model_dump()
                if settings.fastapi_env.value in ["dev", "test"]
                else None
            ),
            cls.__tag_admin__.model_dump(),
            cls.__tag_user__.model_dump(),
            cls.__tag_shop__.model_dump(),
            cls.__tag_product__.model_dump(),
            cls.__tag_shop_member__.model_dump(),
            cls.__tag_cart__.model_dump(),
            cls.__tag_wish__.model_dump(),
        ]
        while None in list_tags:
            list_tags.remove(None)
        return list_tags
