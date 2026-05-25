from datetime import timedelta

from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.dao.user_dao import UserDAO
from app.dao.session_dao import SessionDAO
from app.schemas.user import UserCreate, UserRole, ApprovalStatus
from app.utils.token.jwt_helper import create_access_token, decode_token
from app.utils.password.crypto import verify_password, get_password_hash
from app.utils.totp.totp_helper import verify_totp_code
from app.utils.request.client import get_client_ip, parse_user_agent, generate_device_name, get_location_from_ip
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AuthService:

    @staticmethod
    def register(db: Session, user_data: UserCreate):
        if UserDAO.get_by_username(db, user_data.username):
            raise HTTPException(status_code=400, detail="用户名已存在")

        if UserDAO.get_by_email(db, user_data.email):
            raise HTTPException(status_code=400, detail="邮箱已被注册")

        if user_data.role == UserRole.admin:
            raise HTTPException(status_code=403, detail="不允许注册管理员账号")

        hashed = get_password_hash(user_data.password)
        user = UserDAO.create(
            db,
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed,
            role=user_data.role.value,
            approval_status=ApprovalStatus.pending.value,
            is_active=True,
        )

        logger.info(f"用户注册成功（待审核）: username={user.username}, role={user.role}")
        return user

    @staticmethod
    async def login(db: Session, request: Request, username: str, password: str):
        user = UserDAO.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            ip = get_client_ip(request)
            logger.warning(f"登录失败: username={username}, ip={ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

        if user.approval_status != ApprovalStatus.approved.value:
            if user.approval_status == ApprovalStatus.pending.value:
                raise HTTPException(status_code=403, detail="账号待审核，请等待管理员审批")
            elif user.approval_status == ApprovalStatus.rejected.value:
                raise HTTPException(status_code=403, detail="账号审核未通过，请联系管理员")

        if user.two_factor_enabled:
            temp_token = create_access_token(
                data={"sub": user.username, "temp": True},
                expires_delta=timedelta(minutes=5),
            )
            return {
                "access_token": temp_token,
                "token_type": "bearer",
                "two_factor_required": True,
                "two_factor_secret": user.two_factor_secret,
            }

        access_token = create_access_token(data={"sub": user.username})
        AuthService._create_session(db, user.id, request)

        logger.info(f"用户登录成功: user_id={user.id}, username={user.username}, role={user.role}")
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def login_2fa(db: Session, request: Request, code: str):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少临时 token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        temp_token = auth_header.replace("Bearer ", "")
        payload = decode_token(temp_token)
        if not payload or not payload.get("temp"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="临时 token 已过期或无效",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user = UserDAO.get_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not user.two_factor_enabled or not user.two_factor_secret:
            raise HTTPException(status_code=400, detail="用户未启用 2FA")

        if not verify_totp_code(user.two_factor_secret, code):
            raise HTTPException(status_code=401, detail="验证码不正确")

        access_token = create_access_token(data={"sub": user.username})
        AuthService._create_session(db, user.id, request)

        logger.info(f"用户 2FA 登录成功: user_id={user.id}, username={user.username}")
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def _create_session(db: Session, user_id: int, request: Request):
        import uuid
        from datetime import datetime

        session_token = str(uuid.uuid4())
        user_agent = request.headers.get("User-Agent", "")
        ip_address = get_client_ip(request)

        ua_info = parse_user_agent(user_agent)
        device_name = generate_device_name(ua_info["browser"], ua_info["os"], ua_info["device_type"])
        location = get_location_from_ip(ip_address)
        expires_at = datetime.utcnow() + timedelta(days=7)

        SessionDAO.deactivate_others(db, user_id)
        SessionDAO.create(
            db,
            user_id=user_id,
            session_token=session_token,
            device_type=ua_info["device_type"],
            device_name=device_name,
            browser=ua_info["browser"],
            os=ua_info["os"],
            ip_address=ip_address,
            location=location,
            is_current=True,
            expires_at=expires_at,
        )
