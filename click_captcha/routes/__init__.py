from fastapi import APIRouter

from click_captcha.routes.captcha import router as captcha_router

api_router = APIRouter()

api_router.include_router(captcha_router, prefix="/captcha", tags=["验证码"])
