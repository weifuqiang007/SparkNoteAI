from typing import Any, Optional, TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    class Config:
        from_attributes = True


class PageData(BaseModel):
    items: List[Any] = []
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0


class R:
    """统一响应封装"""

    @staticmethod
    def ok(data: Any = None, message: str = "success") -> dict:
        return {"code": 200, "message": message, "data": data}

    @staticmethod
    def fail(message: str = "error", code: int = 400, data: Any = None) -> dict:
        return {"code": code, "message": message, "data": data}

    @staticmethod
    def unauthorized(message: str = "未授权，请先登录") -> dict:
        return {"code": 401, "message": message, "data": None}

    @staticmethod
    def forbidden(message: str = "无权限访问") -> dict:
        return {"code": 403, "message": message, "data": None}

    @staticmethod
    def not_found(message: str = "资源不存在") -> dict:
        return {"code": 404, "message": message, "data": None}

    @staticmethod
    def page(items: List[Any], total: int, page: int, size: int, message: str = "success") -> dict:
        pages = (total + size - 1) // size if size > 0 else 0
        return {
            "code": 200,
            "message": message,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
            },
        }
