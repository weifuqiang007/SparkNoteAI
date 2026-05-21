from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.user_session import UserSession


class SessionDAO:

    @staticmethod
    def create(db: Session, **kwargs) -> UserSession:
        session = UserSession(**kwargs)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> list[UserSession]:
        stmt = (
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .order_by(UserSession.last_active_at.desc())
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_token(db: Session, session_token: str, user_id: int) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.session_token == session_token,
            UserSession.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def deactivate_others(db: Session, user_id: int) -> None:
        db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(is_current=False)
        )

    @staticmethod
    def delete_by_id(db: Session, session_id: int, user_id: int) -> bool:
        session = db.get(UserSession, session_id)
        if session and session.user_id == user_id:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_others(db: Session, user_id: int, exclude_id: int) -> int:
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.id != exclude_id,
        )
        sessions = db.execute(stmt).scalars().all()
        count = len(sessions)
        for s in sessions:
            db.delete(s)
        db.commit()
        return count

    @staticmethod
    def delete_expired(db: Session) -> int:
        stmt = select(UserSession).where(UserSession.expires_at < datetime.utcnow())
        sessions = db.execute(stmt).scalars().all()
        count = len(sessions)
        for s in sessions:
            db.delete(s)
        db.commit()
        return count
