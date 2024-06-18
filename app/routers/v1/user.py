import i18n
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from ... import models, schemas
from ...config.auth import Auth
from ...helpers.check import Check
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)


@router.get("/me", response_model=schemas.user.User)
def read_user_me(
    tuple_user: tuple[schemas.user.UserComplete, Session] = Depends(
        Auth.get_current_user
    )
):
    current_user, _ = tuple_user
    return current_user


@router.post("/", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.user.UserBase, db: Session = Depends(Dependency.get_db)):
    query_matricule = {"matricule": user.matricule}
    Check.model_exist(
        db=db,
        model_class=models.user.User,
        query=query_matricule,
        status_code=status.HTTP_400_BAD_REQUEST,
        attribute="matricule",
        check=True,
    )
    query_email = {"email": user.email}
    Check.model_exist(
        db=db,
        model_class=models.user.User,
        query=query_email,
        status_code=status.HTTP_400_BAD_REQUEST,
        attribute="email",
        check=True,
    )
    return models.user.User.create(db, **user.model_dump())


@router.get("/all_admin", response_model=list[schemas.user.UserBase])
def get_all_admin(db: Session = Depends(Dependency.get_db)):
    list_users = models.user.User.where(db, admin={"user_id": {"isnot": None}})
    return [schemas.user.UserBase(**user.as_dict()) for user in list_users]


@router.get("/{user_id}", response_model=schemas.user.User)
def read_user(user_id: int, db: Session = Depends(Dependency.get_db)):
    db_user = Check.model_exist(
        db=db,
        model_class=models.user.User,
        query={"id": user_id},
        status_code=status.HTTP_404_NOT_FOUND,
    )
    return db_user


@router.put(
    "/{user_id}/is_admin",
    response_model=schemas.user.User,
    description="The endpoint to update the attribute is_admin of the user with the requested id.",
    response_description="The user updated",
)
def update_user_is_admin(
    user_id: int,
    is_admin: bool = Form(examples=[False]),
    tuple_user: tuple[schemas.user.UserComplete, Session] = Depends(
        Auth.get_current_user
    ),
):
    current_user, db = tuple_user
    db_user = Check.model_exist(
        db=db,
        model_class=models.user.User,
        query={"id": user_id},
        status_code=status.HTTP_404_NOT_FOUND,
    )
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=i18n.t("errors.user_self")
        )
    if is_admin and not db_user.admin:
        models.admin.Admin.create(db, user_id=user_id)
    elif not is_admin and db_user.admin:
        models.admin.Admin.find_by(db, user_id=user_id).delete
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    tuple_user: tuple[schemas.user.UserComplete, Session] = Depends(
        Auth.get_current_user
    ),
):
    current_user, db = tuple_user
    db_user = Check.model_exist(
        db=db,
        model_class=models.user.User,
        query={"id": user_id},
        status_code=status.HTTP_404_NOT_FOUND,
    )
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=i18n.t("errors.user_delete_self"),
        )
    return {"message": db_user.delete(db)}
