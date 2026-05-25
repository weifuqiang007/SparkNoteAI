from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.schemas.user import UserApproval, UserStatusUpdate, User, PendingUser, ApprovalStatus
from app.api.deps import require_admin
from app.utils.response import R

router = APIRouter()


@router.get("/pending-users")
def get_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = UserDAO.get_pending_users(db)
    return R.ok(data=[PendingUser.model_validate(u).model_dump() for u in users])


@router.post("/approve")
def approve_user(
    data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = UserDAO.get_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if data.action == "approve":
        UserDAO.update(
            db, user,
            approval_status=ApprovalStatus.approved.value,
            approved_by=current_user.id,
            approved_at=datetime.utcnow(),
            approval_note=data.note,
        )
    elif data.action == "reject":
        UserDAO.update(
            db, user,
            approval_status=ApprovalStatus.rejected.value,
            approved_by=current_user.id,
            approved_at=datetime.utcnow(),
            approval_note=data.note,
        )

    return R.ok(data=User.model_validate(user).model_dump())


@router.get("/users")
def get_all_users(
    role: str | None = None,
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = UserDAO.get_all_users(db, role=role, approval_status=approval_status)
    return R.ok(data=[User.model_validate(u).model_dump() for u in users])


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = UserDAO.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    UserDAO.update(db, user, is_active=data.is_active)
    return R.ok(data=User.model_validate(user).model_dump())
