# API 路由

from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .session import router as session_router
from .note import router as note_router
from .knowledge_graph import router as knowledge_graph_router
from .tasks import router as tasks_router

# 新配置系统路由
from .integrations import router as integrations_router
from .feature_settings import router as feature_settings_router
from .preferences import router as preferences_router
from .ai_assistant import router as ai_assistant_router

# 系统状态路由
from .system import router as system_router

# 图片上传路由
from .images import router as images_router

# 管理员路由
from .admin import router as admin_router

router = APIRouter()

# 认证相关
router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 管理员
router.include_router(admin_router, prefix="/admin", tags=["管理员"])

# 用户管理（需要去掉 /auth 前缀，改为 /user）
router.include_router(user_router, prefix="/user", tags=["用户管理"])

# 会话管理
router.include_router(session_router, prefix="/auth", tags=["会话管理"])

# 笔记
router.include_router(note_router, tags=["笔记"])

# 配置
router.include_router(integrations_router, tags=["集成配置"])
router.include_router(feature_settings_router, tags=["场景配置"])
router.include_router(preferences_router, prefix="/preferences", tags=["用户偏好"])
router.include_router(ai_assistant_router, tags=["AI 助手"])

# 系统状态
router.include_router(system_router, tags=["系统状态"])

# 知识图谱 / 任务 / 图片
router.include_router(knowledge_graph_router, tags=["知识图谱"])
router.include_router(tasks_router, tags=["任务管理"])
router.include_router(images_router, tags=["图片"])
