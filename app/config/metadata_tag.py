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

    __tag_user__: _MetadataTag = _MetadataTag(
        name="user", prefix="/users", description="Endpoints related to user data."
    )
    __tag_block__: _MetadataTag = _MetadataTag(
        name="block", prefix="/blocks", description="Endpoints related to block data."
    )
    __tag_serie__: _MetadataTag = _MetadataTag(
        name="serie", prefix="/series", description="Endpoints related to serie data."
    )

    __tag_card__: _MetadataTag = _MetadataTag(
        name="card", prefix="/cards", description="Endpoints related to cards data."
    )

    __tag_variant__: _MetadataTag = _MetadataTag(
        name="variant",
        prefix="/variants",
        description="Endpoints related to variant data.",
    )
    __tag_attack__: _MetadataTag = _MetadataTag(
        name="attack",
        prefix="/attacks",
        description="Endpoints related to attack data.",
    )
    __tag_weakness__: _MetadataTag = _MetadataTag(
        name="weakness",
        prefix="/weaknesss",
        description="Endpoints related to weakness data.",
    )
    __tag_resistance__: _MetadataTag = _MetadataTag(
        name="resistance",
        prefix="/resistances",
        description="Endpoints related to resistance data.",
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
            cls.__tag_user__.model_dump(),
            cls.__tag_block__.model_dump(),
            cls.__tag_serie__.model_dump(),
            cls.__tag_card__.model_dump(),
            cls.__tag_variant__.model_dump(),
            cls.__tag_attack__.model_dump(),
            cls.__tag_weakness__.model_dump(),
            cls.__tag_resistance__.model_dump(),
        ]
        while None in list_tags:
            list_tags.remove(None)
        return list_tags
