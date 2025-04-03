import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from click_captcha.core.config import settings

logger = logging.getLogger(__name__)


class CaptchaTarget:
    """验证码目标对象模型。"""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        font_size: int = 40,
        rotation: int = 0,
    ) -> None:
        """
        初始化验证码目标对象。

        参数:
            name: 目标名称
            x: 目标x坐标
            y: 目标y坐标
            width: 目标宽度
            height: 目标高度
            font_size: 字体大小
            rotation: 旋转角度
        """
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.rotation = rotation

    def check_click(self, click_x: int, click_y: int, tolerance: Optional[int] = None) -> bool:
        """
        检查点击位置是否在目标对象上。

        参数:
            click_x: 点击的x坐标
            click_y: 点击的y坐标
            tolerance: 容差范围（像素），默认使用settings.CLICK_TOLERANCE

        返回:
            bool: 点击是否命中目标
        """
        if tolerance is None:
            tolerance = settings.CLICK_TOLERANCE

        # 计算点击点到目标中心的距离
        distance = math.sqrt((click_x - self.x) ** 2 + (click_y - self.y) ** 2)

        # 考虑到旋转后的文字可能占用更大空间，使用更灵活的判定
        # 文字旋转后的实际区域往往比原始区域大
        radius = max(self.width, self.height) / 2

        # 日志记录点击判定信息
        logger.debug(
            f"目标[{self.name}] - 位置:({self.x},{self.y}) 点击:({click_x},{click_y}) "
            f"距离:{distance:.2f} 允许范围:{radius + tolerance} "
            f"判定:{distance <= (radius + tolerance)}"
        )

        return distance <= (radius + tolerance)

    def to_dict(self) -> Dict[str, Any]:
        """
        将对象转换为字典。

        返回:
            Dict[str, Any]: 目标的字典表示
        """
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "font_size": self.font_size,
            "rotation": self.rotation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptchaTarget":
        """
        从字典创建对象。

        参数:
            data: 包含目标属性的字典数据

        返回:
            CaptchaTarget: 创建的对象
        """
        return cls(
            name=data["name"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            font_size=data.get("font_size", 40),
            rotation=data.get("rotation", 0),
        )


class Captcha:
    """点击验证挑战的验证码数据模型。"""

    def __init__(
        self,
        image_data: str,
        targets: List[CaptchaTarget],
        prompt: str,
        target_count: int,
        captcha_id: str,
        image_width: int = settings.CAPTCHA_WIDTH,
        image_height: int = settings.CAPTCHA_HEIGHT,
    ) -> None:
        """
        初始化验证码。

        参数:
            image_data: Base64编码的图像数据
            targets: 目标对象列表
            prompt: 指令提示
            target_count: 需点击的目标数量
            captcha_id: 验证码ID
            image_width: 验证码图像宽度
            image_height: 验证码图像高度
        """
        self.image_data = image_data
        self.targets = targets
        self.prompt = prompt
        self.captcha_id = captcha_id
        self.target_count = target_count
        self.created_at = datetime.now()
        self.image_width = image_width
        self.image_height = image_height

    def verify_clicks(self, clicks: List[Dict[str, int]], tolerance: Optional[int] = None) -> bool:
        """
        验证用户点击序列是否正确

        参数:
            clicks: 用户点击坐标序列 [{x, y}, {x, y}, ...]
            tolerance: 容差范围（像素），默认使用配置中的值

        返回:
            bool: 是否验证通过
        """
        # 使用配置中的容差值
        if tolerance is None:
            tolerance = settings.CLICK_TOLERANCE

        logger.debug(f"验证点击 - 目标数:{len(self.targets)} 点击数:{len(clicks)} 容差:{tolerance}像素")

        # 如果点击次数与目标数量不符，直接返回失败
        if len(clicks) != len(self.targets):
            logger.warning(f"点击次数({len(clicks)})与目标数量({len(self.targets)})不符")
            return False

        # 严格模式：按顺序验证每个点击是否匹配对应目标
        for i, click in enumerate(clicks):
            click_x = click["x"]
            click_y = click["y"]
            target = self.targets[i]

            # 调用目标的点击检查方法
            if not target.check_click(click_x, click_y, tolerance):
                logger.warning(f"第{i+1}个点击({click_x},{click_y})未命中目标{target.name}({target.x},{target.y})")
                return False

        # 所有点击都匹配对应的目标
        logger.info("所有点击验证通过")
        return True

    def verify_clicks_relaxed(self, clicks: List[Dict[str, int]], tolerance: Optional[int] = None) -> bool:
        """
        宽松模式验证用户点击 - 不考虑顺序，只要每个目标都被点击即可

        参数:
            clicks: 用户点击坐标序列
            tolerance: 容差范围（像素）

        返回:
            bool: 是否验证通过
        """
        if tolerance is None:
            tolerance = settings.CLICK_TOLERANCE

        # 点击次数必须匹配
        if len(clicks) != len(self.targets):
            return False

        # 复制目标列表，用于标记已匹配的目标
        remaining_targets = self.targets.copy()

        # 检查每个点击是否能匹配任一未匹配的目标
        for click in clicks:
            click_x = click["x"]
            click_y = click["y"]

            # 尝试找到匹配的目标
            matched = False
            for i, target in enumerate(remaining_targets):
                if target and target.check_click(click_x, click_y, tolerance):
                    # 找到匹配，移除此目标
                    remaining_targets[i] = None  # type: ignore
                    matched = True
                    break

            if not matched:
                # 有点击没有匹配任何目标
                return False

        # 所有点击都找到了匹配的目标
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        将对象转换为字典用于Redis存储。

        返回:
            Dict[str, Any]: 验证码的字典表示
        """
        return {
            "image_data": self.image_data,
            "targets": [target.to_dict() for target in self.targets],
            "prompt": self.prompt,
            "captcha_id": self.captcha_id,
            "target_count": self.target_count,
            "created_at": self.created_at.isoformat(),
            "image_width": self.image_width,
            "image_height": self.image_height,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Captcha":
        """
        从字典创建对象。

        参数:
            data: 包含验证码属性的字典数据

        返回:
            Captcha: 创建的验证码对象
        """
        captcha = cls(
            image_data=data["image_data"],
            targets=[CaptchaTarget.from_dict(target) for target in data["targets"]],
            prompt=data["prompt"],
            target_count=data["target_count"],
            captcha_id=data["captcha_id"],
            image_width=data.get("image_width", settings.CAPTCHA_WIDTH),
            image_height=data.get("image_height", settings.CAPTCHA_HEIGHT),
        )

        # 设置创建时间
        if "created_at" in data:
            captcha.created_at = datetime.fromisoformat(data["created_at"])

        return captcha

    def to_response_dict(self) -> Dict[str, Any]:
        """
        返回供客户端使用的响应字典。

        返回:
            Dict[str, Any]: 包含面向客户端的验证码信息的字典
        """
        return {
            "captcha_id": self.captcha_id,
            "image_data": self.image_data,
            "prompt": self.prompt,
            "target_count": self.target_count,
            "created_at": self.created_at.isoformat(),
            "image_width": self.image_width,
            "image_height": self.image_height,
        }
