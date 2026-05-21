from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, User
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.utils.response import R

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    result = AuthService.register(db, user)
    return R.ok(data=User.model_validate(result).model_dump())


@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    result = await AuthService.login(db, request, username, password)
    return R.ok(data=result)


@router.post("/login/2fa")
async def login_2fa(
    request: Request,
    db: Session = Depends(get_db),
    code: str = Form(...),
):
    result = await AuthService.login_2fa(db, request, code)
    return R.ok(data=result)


@router.get("/me")
def get_me(current_user: UserModel = Depends(get_current_user)):
    return R.ok(data=User.model_validate(current_user).model_dump())
