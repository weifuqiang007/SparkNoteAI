from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.token.jwt_helper import decode_token
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.schemas.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserDAO.get_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return user


def require_role(*allowed_roles: UserRole):
    """角色权限校验依赖工厂"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问该资源",
            )
        return current_user
    return role_checker


require_admin = require_role(UserRole.admin)
require_teacher = require_role(UserRole.teacher, UserRole.admin)
require_student = require_role(UserRole.student, UserRole.admin)
