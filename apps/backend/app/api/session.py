from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user_session import UserSessionResponse, SessionRevokeRequest, SessionRevokeAllRequest
from app.services.session_service import SessionService
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.utils.response import R

router = APIRouter()


@router.get("/me/sessions")
def list_sessions(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    sessions = SessionService.list_sessions(db, current_user.id)
    return R.ok(data=sessions)


@router.post("/me/sessions/{session_id}/revoke")
def revoke_session(
    session_id: int,
    request_data: SessionRevokeRequest = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    password = request_data.password if request_data else None
    result = SessionService.revoke_session(db, session_id, current_user.id, password, current_user)
    return R.ok(data=result)


@router.post("/me/sessions/revoke-all")
def revoke_all_sessions(
    request_data: SessionRevokeAllRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    result = SessionService.revoke_all_others(db, current_user.id, current_user,
                                               request_data.password, token)
    return R.ok(data=result)
