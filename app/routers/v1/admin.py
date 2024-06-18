from fastapi import APIRouter, Depends, Form, status
from pydantic import StringConstraints
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from ... import helpers
from ...config.auth import Auth
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)
