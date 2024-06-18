from datetime import datetime, timedelta

import i18n
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from .. import models
from ..config.constants import TIME_ZONE_APP
from ..config.env import settings
from ..config.metadata_tag import MetadataTag
from ..utils.dependency import Dependency

ACCESS_TOKEN_EXPIRE_MINUTES = 120

api_router = APIRouter(
    prefix=MetadataTag.__tag_login__.prefix, tags=[MetadataTag.__tag_login__.name]
)


@api_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(Dependency.get_db),
):
    user = models.user.User.find_by(db, email=form_data.username)
    if not user or user.matricule != form_data.password:
        raise HTTPException(status_code=400, detail=i18n.t("errors.invalid_login"))

    to_encode = {
        "matricule": user.matricule,
        "email": user.email,
        "exp": datetime.now(tz=TIME_ZONE_APP)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key_jwt, algorithm=settings.algorithm
    )
    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
    }
