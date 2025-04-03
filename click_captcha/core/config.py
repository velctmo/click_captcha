from typing import List, Optional, Union

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    包含应用程序所有部分配置的应用设置类。
    """

    # API设置
    API_TITLE: str = "Click Captcha API"
    API_DESCRIPTION: str = "Click Captcha system based on FastAPI"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # CORS设置
    ALLOWED_ORIGINS: Union[str, List[str]] = "*"

    # Redis设置
    REDIS_URL: str = "redis://:root@localhost:6379"

    # 文件系统路径
    IMAGES_DIR: str = "app/static/images"
    FONTS_DIR: str = "app/static/fonts"

    # 环境
    ENVIRONMENT: str = "development"

    # 验证码配置
    CAPTCHA_WIDTH: int = 400
    CAPTCHA_HEIGHT: int = 200
    CAPTCHA_EXPIRATION_SECONDS: int = 120  # 验证码过期时间（秒）
    MIN_FONT_SIZE: int = 30  # 最小字体大小
    MAX_FONT_SIZE: int = 45  # 最大字体大小
    MAX_ROTATION_ANGLE: int = 30  # 最大旋转角度
    CLICK_TOLERANCE: int = 30  # 点击容差范围（像素），增加以提高验证成功率
    BASE_FONT_SIZE: int = 36  # 基础字体大小

    class Config:
        """BaseSettings行为的配置。"""

        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("ALLOWED_HOSTS", pre=True, check_fields=False)
    def CommaSeparatedStrings(cls, v: Optional[str]) -> List[str]:
        if not v:
            return []
        return [item.strip() for item in v.split(",")]


# 创建设置实例
settings = Settings()
