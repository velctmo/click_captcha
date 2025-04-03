import base64
import logging
import math
import os
import random
import uuid
from typing import Dict, List, Optional, Set, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from click_captcha.core.config import settings
from click_captcha.core.redis import RedisManager
from click_captcha.models.captcha import Captcha, CaptchaTarget

logger = logging.getLogger(__name__)
COMMON_CHINESE_CHARS = """
        喝同湿冰是鸡果九蒸父菜买饱咸年里兴牛二千百班原口演站孩证筷帽听块学流小家霜亮六老险地有他纸道码累活
        土司卖安我雷渴蔬爱就因花西七木沙右为高假唱阴钱车痛半坐虾秒工衣奶跳心后病结字近饭看干址乐人前多发味
        一女漠黑来束猪闲苹斤北米友危朋草白肉泥男阳好树三明幼笑鸭和她大鼻海舒云时让鞋忙脑饿林甜喜头条护辣每
        外机十动五面能公了蛋快画厨不锅送星说师等春少经写碗煎万笔晴森今酸空勺冬耳要火夏生猫密这以元走洋光角
        零错名欢找眼医视康风会天运炒过日鸟你煮羊舞红歌警理士雪农板书母昨龄杯太份对雨啡分上跑停包真记热水气
        附绿山民狗月习健咖们收服烤酒四难号中哭石东旁始电香钟读南蕉察手者身它死的作拿放盘爬期帮边试开烧苦黄
        河全鱼考冷炸加子在助员八秋做左叉雾吃间躺骑蓝茶
    """


class CaptchaService:
    """负责生成和验证点击验证码的验证码服务。"""

    @classmethod
    def get_random_base_image(cls) -> np.ndarray:
        """
        获取随机背景图片。

        返回:
            np.ndarray: 所选背景的OpenCV图像数组
        """
        # 检查背景目录
        if settings.IMAGES_DIR and os.path.exists(settings.IMAGES_DIR):
            background_files = [
                f for f in os.listdir(settings.IMAGES_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

            if background_files:
                image_path = os.path.join(settings.IMAGES_DIR, random.choice(background_files))
                return cv2.imread(image_path)

        # 如果没有背景或目录为空，则使用默认背景
        default_img = np.ones((settings.CAPTCHA_HEIGHT, settings.CAPTCHA_WIDTH, 3), dtype=np.uint8) * 255
        return default_img

    @classmethod
    def get_font_path(cls) -> str:
        """
        获取字体文件路径。

        返回:
            str: 适合的字体文件路径

        抛出:
            FileNotFoundError: 如果找不到合适的字体
        """

        # 检查字体目录中是否存在字体文件
        if os.path.exists(settings.FONTS_DIR):
            font_files = [f for f in os.listdir(settings.FONTS_DIR) if f.lower().endswith((".ttf", ".otf"))]
            if font_files:
                return os.path.join(settings.FONTS_DIR, random.choice(font_files))

        logger.info("字体目录中未找到字体文件，尝试使用系统字体")

        # 不同系统的默认字体路径
        system_fonts = [
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Windows
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\msyh.ttf",
            "C:\\Windows\\Fonts\\simsun.ttc",
            # Linux
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            # 自定义字体位置
            "simhei.ttf",
            "fonts/simhei.ttf",
        ]

        # 尝试查找并使用系统字体
        for font_path in system_fonts:
            if os.path.exists(font_path):
                try:
                    # 检查字体是否可用
                    ImageFont.truetype(font_path, settings.BASE_FONT_SIZE)
                    return font_path
                except Exception:
                    continue

        # 如果绝对找不到合适的字体，则抛出错误
        error_msg = "未找到中文字体文件。请将中文字体文件添加到app/static/fonts目录"
        logger.critical(error_msg)
        raise FileNotFoundError(error_msg)

    @classmethod
    def get_random_chinese_char(cls) -> str:
        """生成随机的中文字符"""

        while True:
            char = random.choice(COMMON_CHINESE_CHARS).strip()
            if char:
                break
        return char

    @classmethod
    def get_unique_chars(cls, count: int) -> List[str]:
        """生成指定数量的不重复汉字"""
        chars: Set[str] = set()
        while len(chars) < count:
            chars.add(cls.get_random_chinese_char())
        return list(chars)

    @classmethod
    def get_random_target_objects(cls) -> Tuple[List[CaptchaTarget], str, int]:
        """
        生成随机目标对象。

        返回:
            Tuple[List[CaptchaTarget], str, int]: 目标对象列表，提示文本和目标数量
        """

        # 随机选择需要点击的字符
        num_targets = random.randint(2, 4)
        target_chars = cls.get_unique_chars(num_targets)

        # 添加额外的1-2个字符
        num_extra_chars = random.randint(1, 2)
        # 保持额外字符的唯一性
        extra_chars: List[str] = []
        while len(extra_chars) < num_extra_chars:
            new_char = cls.get_random_chinese_char()
            if new_char not in target_chars and new_char not in extra_chars:
                extra_chars.append(new_char)

        # 合并所有要显示的字符并随机打乱顺序
        display_chars = target_chars + extra_chars
        random.shuffle(display_chars)  # 打乱顺序

        # 创建提示文本
        prompt = "请依次点击: {}".format("、".join(target_chars))

        # 字符位置计算
        positions: List[Tuple[int, int]] = []
        for _ in range(len(display_chars)):
            # 尝试找到不重叠的位置
            max_attempts = 20
            for attempt in range(max_attempts):
                # 随机位置，考虑边距
                margin = 40
                x = random.randint(margin, settings.CAPTCHA_WIDTH - margin)
                y = random.randint(margin, settings.CAPTCHA_HEIGHT - margin)

                # 检查是否与现有位置重叠
                overlap = False
                min_distance = 45  # 最小间距
                for pos in positions:
                    distance = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
                    if distance < min_distance:
                        overlap = True
                        break

                if not overlap or attempt == max_attempts - 1:
                    positions.append((x, y))
                    break

        # 生成所有字符的目标对象
        all_targets = []
        for i, char in enumerate(display_chars):
            if i < len(positions):
                # 随机字体大小
                font_size = random.randint(settings.MIN_FONT_SIZE, settings.MAX_FONT_SIZE)

                # 随机旋转角度
                rotation = random.randint(-settings.MAX_ROTATION_ANGLE, settings.MAX_ROTATION_ANGLE)

                # 估计宽度和高度
                width = font_size
                height = font_size

                # 创建目标对象
                target = CaptchaTarget(
                    name=char,
                    x=positions[i][0],
                    y=positions[i][1],
                    width=width,
                    height=height,
                    font_size=font_size,
                    rotation=rotation,
                )

                all_targets.append(target)

        return all_targets, prompt, num_targets

    @classmethod
    def image_to_base64(cls, image: np.ndarray) -> str:
        """
        将OpenCV图像转换为base64编码的字符串。

        参数:
            image: OpenCV图像数组

        返回:
            str: Base64编码的图像字符串（数据URI格式）
        """
        # 将BGR转换为RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 将图像编码为PNG
        _, buffer = cv2.imencode(".png", image_rgb)

        # 转换为base64 - 首先将缓冲区转换为字节
        img_str = base64.b64encode(buffer.tobytes()).decode()
        return f"data:image/png;base64,{img_str}"

    @classmethod
    def draw_rotated_text(
        cls,
        img: np.ndarray,
        text: str,
        x: int,
        y: int,
        font_size: int,
        rotation: int,
        font_path: str,
    ) -> Tuple[np.ndarray, int, int]:
        """
        在图像上绘制旋转文本

        参数:
            img: 目标图像
            text: 要绘制的文本
            x: X坐标
            y: Y坐标
            font_size: 字体大小
            rotation: 旋转角度
            font_path: 字体文件路径

        返回:
            Tuple[np.ndarray, int, int]: 带有文本的图像，文本宽度，文本高度
        """
        # 将OpenCV图像转换为PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # 创建字体对象
        font = ImageFont.truetype(font_path, font_size)

        # 创建临时绘图对象来计算文本大小
        temp_draw = ImageDraw.Draw(img_pil)

        # 使用textbbox而不是textsize（在较新的Pillow版本中已弃用）
        try:
            # 对于较新的Pillow版本
            left, top, right, bottom = temp_draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:
            # 对于旧版Pillow的回退方案
            text_width, text_height = temp_draw.textsize(text, font=font)  # type: ignore

        # 创建新的透明层用于旋转文本
        txt_img = Image.new("RGBA", (text_width * 2, text_height * 2), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)

        # 在中心位置绘制文本
        txt_draw.text((text_width // 2, text_height // 2), text, font=font, fill=(0, 0, 0, 255))

        # 旋转文本层
        rotated_txt = txt_img.rotate(rotation, expand=True)

        # 将旋转后的PIL图像转换为OpenCV格式
        rotated_np = np.array(rotated_txt)

        # 处理alpha通道
        if rotated_np.shape[2] == 4:
            # 从alpha通道创建遮罩
            alpha = rotated_np[:, :, 3] / 255.0
            alpha = np.dstack([alpha, alpha, alpha])

            # 提取RGB
            foreground = rotated_np[:, :, :3]

            # 计算粘贴位置
            paste_x = max(0, x - rotated_txt.width // 2)
            paste_y = max(0, y - rotated_txt.height // 2)

            # 定义感兴趣区域
            roi_width = min(rotated_np.shape[1], img.shape[1] - paste_x)
            roi_height = min(rotated_np.shape[0], img.shape[0] - paste_y)

            if roi_width > 0 and roi_height > 0:
                # 获取感兴趣区域
                roi = img[paste_y : paste_y + roi_height, paste_x : paste_x + roi_width]  # noqa

                # 如果需要裁剪前景和alpha
                fg_cropped = foreground[:roi_height, :roi_width]
                alpha_cropped = alpha[:roi_height, :roi_width]

                # 混合图像
                blended = cv2.convertScaleAbs(roi * (1 - alpha_cropped) + fg_cropped * alpha_cropped)

                # 将混合区域放回原始图像
                img[paste_y : paste_y + roi_height, paste_x : paste_x + roi_width] = blended

        return img, rotated_txt.width, rotated_txt.height

    @classmethod
    async def new(cls) -> Captcha:
        """
        生成新的验证码

        返回:
            Captcha: 生成的验证码对象
        """
        # 获取随机背景图
        base_image = cls.get_random_base_image()

        # 调整背景图大小
        base_image = cv2.resize(base_image, (settings.CAPTCHA_WIDTH, settings.CAPTCHA_HEIGHT))

        # 获取随机目标对象和所有显示字符
        all_targets, prompt, target_count = cls.get_random_target_objects()

        # 获取字体
        font_path = cls.get_font_path()

        # 在图像上绘制所有字符（包括干扰字符）
        click_targets = []  # 存储需要点击的目标

        for target in all_targets:
            # 绘制旋转文字
            base_image, text_width, text_height = cls.draw_rotated_text(
                base_image,
                target.name,
                target.x,
                target.y,
                target.font_size,
                target.rotation,
                font_path,
            )

            # 更新目标的宽度和高度
            target.width = text_width
            target.height = text_height

            # 从提示中提取需要点击的字符
            prompt_chars = prompt.split(": ")[1].split("、")
            # 如果是需要点击的目标，添加到列表中
            if target.name in prompt_chars:
                click_targets.append(target)

        # 将图像转换为base64
        image_data = cls.image_to_base64(base_image)

        # 创建验证码对象（只使用需要点击的目标）
        captcha_id = str(uuid.uuid4())
        captcha = Captcha(image_data, click_targets, prompt, target_count, captcha_id)

        # 将验证码存储到Redis
        await RedisManager.set(captcha_id, captcha.to_dict(), ttl=settings.CAPTCHA_EXPIRATION_SECONDS)

        return captcha

    @classmethod
    async def get(cls, captcha_id: str) -> Optional[Captcha]:
        """
        获取验证码对象

        参数:
            captcha_id: 验证码ID

        返回:
            Optional[Captcha]: 验证码对象，如果不存在则返回None
        """
        captcha_data = await RedisManager.get(captcha_id)
        if captcha_data:
            return Captcha.from_dict(captcha_data)
        return None

    @classmethod
    async def verify(cls, captcha_id: str, clicks: List[Dict[str, int]]) -> bool:
        """
        验证用户点击是否正确

        参数:
            captcha_id: 验证码ID
            clicks: 用户点击坐标序列 [{x, y}, {x, y}, ...]

        返回:
            bool: 是否验证通过
        """
        captcha = await cls.get(captcha_id)

        # 验证码不存在
        if not captcha:
            logger.warning(f"验证失败: 验证码ID不存在 - {captcha_id}")
            return False

        # 点击次数与目标数量不符
        if len(clicks) != len(captcha.targets):
            logger.info(f"验证失败: 点击次数({len(clicks)})与目标数量({len(captcha.targets)})不符 - {captcha_id}")
            await RedisManager.delete(captcha_id)
            return False

        # 尝试两种验证模式
        # 1. 严格模式 - 按顺序匹配
        strict_valid = captcha.verify_clicks(clicks, settings.CLICK_TOLERANCE)

        # 2. 宽松模式 - 不考虑顺序
        # 当严格模式失败时才使用宽松模式
        relaxed_valid = False
        if not strict_valid:
            logger.debug("严格匹配失败，尝试宽松模式验证")
            relaxed_valid = captcha.verify_clicks_relaxed(clicks, settings.CLICK_TOLERANCE)

        # 最终验证结果
        is_valid = strict_valid or relaxed_valid

        # 无论验证结果如何，都删除验证码以防止重复尝试
        await RedisManager.delete(captcha_id)

        if is_valid:
            logger.info(f"验证成功: {captcha_id}, 模式: {'严格' if strict_valid else '宽松'}")
        else:
            logger.info(f"验证失败: 点击位置错误 - {captcha_id}")

            # 更详细地记录每个点击信息，帮助调试
            for i, click in enumerate(clicks):
                logger.debug(f"点击{i+1}: x={click['x']}, y={click['y']}")

        return is_valid

    @classmethod
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

        # 这里应该实现具体的检查逻辑，目前只返回False作为示例
        return False
