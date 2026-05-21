from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dao.user_dao import UserDAO
from app.schemas.user import UserUpdate, UserPasswordUpdate, TwoFactorSetupResponse
from app.utils.password.crypto import verify_password, get_password_hash
from app.utils.totp.totp_helper import generate_totp_secret, get_totp_uri, verify_totp_code
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserService:

    @staticmethod
    def update_profile(db: Session, current_user: User, user_update: UserUpdate):
        if user_update.username and user_update.username != current_user.username:
            if UserDAO.get_by_username(db, user_update.username):
                raise HTTPException(status_code=400, detail="用户名已被占用")
            current_user.username = user_update.username

        if user_update.email and user_update.email != current_user.email:
            if UserDAO.get_by_email(db, user_update.email):
                raise HTTPException(status_code=400, detail="邮箱已被注册")
            current_user.email = user_update.email

        db.commit()
        db.refresh(current_user)
        return current_user

    @staticmethod
    def update_password(db: Session, current_user: User, password_data: UserPasswordUpdate):
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="当前密码不正确")

        UserDAO.update_password(db, current_user, get_password_hash(password_data.new_password))
        logger.info(f"密码已更新: user_id={current_user.id}")
        return {"message": "密码已更新"}

    @staticmethod
    def setup_2fa(db: Session, current_user: User, password: str):
        if not verify_password(password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="密码不正确")

        secret = generate_totp_secret()
        qr_code_url = get_totp_uri(current_user.username, secret)

        current_user.two_factor_secret = secret
        db.commit()

        return TwoFactorSetupResponse(secret=secret, qr_code_url=qr_code_url)

    @staticmethod
    def enable_2fa(db: Session, current_user: User, code: str):
        if not current_user.two_factor_secret:
            raise HTTPException(status_code=400, detail="请先设置双因素认证")

        if not verify_totp_code(current_user.two_factor_secret, code):
            raise HTTPException(status_code=400, detail="验证码不正确")

        current_user.two_factor_enabled = True
        db.commit()

        return {"message": "双因素认证已启用", "two_factor_enabled": True}

    @staticmethod
    def disable_2fa(db: Session, current_user: User, code: str, password: str):
        if not current_user.two_factor_enabled:
            raise HTTPException(status_code=400, detail="双因素认证未启用")

        if not verify_password(password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="密码不正确")

        if not verify_totp_code(current_user.two_factor_secret, code):
            raise HTTPException(status_code=400, detail="验证码不正确")

        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.commit()

        return {"message": "双因素认证已禁用", "two_factor_enabled": False}

    @staticmethod
    def get_security_info(current_user: User):
        return {
            "username": current_user.username,
            "email": current_user.email,
            "two_factor_enabled": current_user.two_factor_enabled,
            "created_at": current_user.created_at,
        }
