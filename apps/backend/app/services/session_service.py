from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dao.session_dao import SessionDAO
from app.utils.password.crypto import verify_password
from app.utils.request.client import get_client_ip
from app.utils.token.jwt_helper import decode_token
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)


class SessionService:

    @staticmethod
    def list_sessions(db: Session, user_id: int):
        return SessionDAO.get_by_user_id(db, user_id)

    @staticmethod
    def revoke_session(db: Session, session_id: int, user_id: int, password: str = None,
                       current_user: User = None):
        if password and current_user:
            if not verify_password(password, current_user.password_hash):
                raise HTTPException(status_code=400, detail="密码不正确")

        success = SessionDAO.delete_by_id(db, session_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")

        return {"message": "会话已注销"}

    @staticmethod
    def revoke_all_others(db: Session, user_id: int, current_user: User, password: str,
                          request_token: str):
        if not verify_password(password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="密码不正确")

        payload = decode_token(request_token)
        current_session_token = payload.get("sub", "") if payload else ""

        current_session = SessionDAO.get_by_token(db, current_session_token, user_id) if current_session_token else None
        current_session_id = current_session.id if current_session else 0

        count = SessionDAO.delete_others(db, user_id, current_session_id)

        return {"message": f"已注销 {count} 个其他会话", "revoked_count": count}

    @staticmethod
    def cleanup_expired(db: Session) -> int:
        return SessionDAO.delete_expired(db)
