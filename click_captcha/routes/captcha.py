from datetime import timedelta
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from click_captcha.core.config import settings
from click_captcha.core.redis import RedisManager
from click_captcha.schemas.captcha import (
    CaptchaResponse,
    CaptchaVerifyRequest,
    CaptchaVerifyResponse,
)
from click_captcha.services.captcha_service import CaptchaService

router = APIRouter()


@router.get("", name="Generate Captcha", response_model=CaptchaResponse)
async def generate_captcha() -> CaptchaResponse:
    """
    Generate a new click captcha.

    Returns:
        CaptchaResponse: Contains captcha ID, base64 encoded image data and instruction prompt
    """
    # Generate new captcha
    try:
        captcha = await CaptchaService.new()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Calculate expiration time
    expires_at = captcha.created_at + timedelta(seconds=settings.CAPTCHA_EXPIRATION_SECONDS)

    return CaptchaResponse(
        captcha_id=captcha.captcha_id,
        image_data=captcha.image_data,
        prompt=captcha.prompt,
        target_count=captcha.target_count,
        expires_at=expires_at,
        image_width=captcha.image_width,
        image_height=captcha.image_height,
    )


@router.post("/verify", name="Verify Captcha", response_model=CaptchaVerifyResponse)
async def verify_captcha(request: CaptchaVerifyRequest) -> CaptchaVerifyResponse:
    """
    Verify if user clicks are correct.

    Args:
        request: Contains captcha ID and user click positions

    Returns:
        CaptchaVerifyResponse: Verification result including success status and message
    """
    # Check if captcha exists
    captcha = await CaptchaService.get(request.captcha_id)
    if not captcha:
        return CaptchaVerifyResponse(
            success=False, message="Verification failed: Captcha expired or doesn't exist, please try again"
        )

    # Check click count
    clicks: List[Dict[str, int]] = [{"x": click.x, "y": click.y} for click in request.clicks]
    if len(clicks) != len(captcha.targets):
        # Delete captcha on verification failure
        await RedisManager.delete(request.captcha_id)
        return CaptchaVerifyResponse(
            success=False,
            message=f"Verification failed: Need to click {len(captcha.targets)} targets, but received {len(clicks)} clicks",
        )

    # Verify clicks
    is_valid: bool = await CaptchaService.verify(request.captcha_id, clicks)

    if is_valid:
        return CaptchaVerifyResponse(success=True, message="Verification successful")
    else:
        return CaptchaVerifyResponse(
            success=False, message="Verification failed, please follow the instructions and click correctly"
        )
