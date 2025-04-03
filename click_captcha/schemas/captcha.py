from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ClickPosition(BaseModel):
    """Click position model for capturing user interaction coordinates."""

    x: int = Field(..., description="X-coordinate of click")
    y: int = Field(..., description="Y-coordinate of click")


class CaptchaResponse(BaseModel):
    """Captcha generation response model returned to clients."""

    captcha_id: str = Field(..., description="Unique captcha identifier")
    image_data: str = Field(..., description="Base64 encoded image data")
    prompt: str = Field(..., description="Instruction prompt for user")
    target_count: int = Field(..., description="target count")
    expires_at: datetime = Field(..., description="Captcha expiration timestamp")
    image_width: int = Field(..., description="Width of the captcha image")
    image_height: int = Field(..., description="Height of the captcha image")


class CaptchaVerifyRequest(BaseModel):
    """Captcha verification request model sent by clients."""

    captcha_id: str = Field(..., description="Captcha identifier to verify")
    clicks: List[ClickPosition] = Field(..., description="User click positions in order")


class CaptchaVerifyResponse(BaseModel):
    """Captcha verification response model with verification results."""

    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Result message")
