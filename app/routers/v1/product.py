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

uniq_product = CheckUniqHelper(name="name", equal_list=["shop_id"], ilike_list=["name"])
router_product = RouterModelHelper(
    name="product", parents=["shop"], uniq_list=[uniq_product]
)


@router.post(
    "/", response_model=schemas.product.Product, status_code=status.HTTP_201_CREATED
)
def create_product(
    product: schemas.product.ProductBase, db: Session = Depends(Dependency.get_db)
):
    return router_product.create(db, product.model_dump())


@router.get("/{product_id}", response_model=schemas.product.Product)
def read_product(product_id: int, db: Session = Depends(Dependency.get_db)):
    return router_product.read(db, product_id)


@router.get("/shop/{shop_id}", response_model=list[schemas.product.Product])
def list_products_by_shop(shop_id: int, db: Session = Depends(Dependency.get_db)):
    return router_product.list(db, query={"shop_id": shop_id})


@router.put(
    "/{product_id}",
    response_model=schemas.product.Product,
    description="The endpoint to update information about the product with the requested id.",
    response_description="The product updated",
)
def update_product(
    product_id: int,
    new_product: schemas.product.ProductUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_product.update(db, product_id, new_product.model_dump())


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(Dependency.get_db)):
    return router_product.delete(db, product_id)
