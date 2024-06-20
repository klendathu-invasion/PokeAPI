from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_variant = RouterModelHelper(name="variant", parents=[], uniq_list=[])


@router.get("/{variant_id}", response_model=schemas.variant.Variant)
def read_variant(variant_id: int, db: Session = Depends(Dependency.get_db)):
    return router_variant.read(db, variant_id)


@router.get("", response_model=list[schemas.variant.VariantList])
def list_variants(db: Session = Depends(Dependency.get_db)):
    return router_variant.list(db, query={})
