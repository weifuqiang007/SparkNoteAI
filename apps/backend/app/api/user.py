from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import (
    User, UserUpdate, UserPasswordUpdate,
    TwoFactorEnableRequest, TwoFactorVerifyRequest, TwoFactorDisableRequest,
)
from app.services.user_service import UserService
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.utils.response import R

router = APIRouter()


@router.put("/me")
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = UserService.update_profile(db, current_user, user_update)
    return R.ok(data=User.model_validate(result).model_dump())


@router.put("/me/password")
def update_password(
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = UserService.update_password(db, current_user, password_data)
    return R.ok(data=result)


@router.post("/me/two-factor/setup")
def setup_2fa(
    request: TwoFactorEnableRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = UserService.setup_2fa(db, current_user, request.password)
    return R.ok(data=result)


@router.post("/me/two-factor/enable")
def enable_2fa(
    request: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = UserService.enable_2fa(db, current_user, request.code)
    return R.ok(data=result)


@router.post("/me/two-factor/disable")
def disable_2fa(
    request: TwoFactorDisableRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = UserService.disable_2fa(db, current_user, request.code, request.password)
    return R.ok(data=result)


@router.get("/me/security")
def get_security(current_user: UserModel = Depends(get_current_user)):
    result = UserService.get_security_info(current_user)
    return R.ok(data=result)
