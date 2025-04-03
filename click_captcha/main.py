import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from click_captcha.core.config import settings
from click_captcha.routes import api_router

# 为这个模块创建独立的logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="click_captcha/static", html=True))

# 注册API路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# 在启动时记录版本信息
logger.info(f"启动 {settings.API_TITLE} v{settings.API_VERSION}, 环境: {settings.ENVIRONMENT}")


@app.on_event("startup")
async def startup_event() -> None:
    """应用启动的事件处理器。"""
    logger.info("应用正在启动...")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """应用关闭的事件处理器。"""
    logger.info("应用已关闭。")
