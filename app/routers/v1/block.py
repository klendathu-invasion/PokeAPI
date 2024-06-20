from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter()

router_block = RouterModelHelper(name="block", parents=[], uniq_list=[])


@router.get("/{block_id}", response_model=schemas.block.Block)
def read_block(block_id: int, db: Session = Depends(Dependency.get_db)):
    return router_block.read(db, block_id)


@router.get("", response_model=list[schemas.block.BlockList])
def list_blocks(db: Session = Depends(Dependency.get_db)):
    return router_block.list(db, query={})


@router.get("/name/{name}", response_model=list[schemas.block.BlockList])
def list_blocks_by_name(name: str, db: Session = Depends(Dependency.get_db)):
    return router_block.list(db, query={"name": {"ilike": f"%{name}%"}})
