# Click Captcha System

English | [简体中文](#点选验证码系统)

A click-based CAPTCHA generation and verification system implemented with FastAPI. The system generates CAPTCHA images with random Chinese characters, requiring users to click on specific characters as indicated in the prompt.

![image](https://github.com/user-attachments/assets/735bfa85-73e3-4f2d-b2c2-1b3006c4ab9a)


## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Redis Requirements](#redis-requirements)

## ✨ Features

- Generate click CAPTCHAs containing random Chinese characters
- Support for characters with varying sizes and orientations
- Simple and easy-to-use API interface
- Use Redis to store CAPTCHA information and base64 encoded image data
- Customizable CAPTCHA expiration time and configuration
- Support for custom background images
- Supports both strict and relaxed verification modes

## 🔧 Installation

### Using Poetry (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/click_captcha.git
cd click_captcha

# Install dependencies
poetry install
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/click_captcha.git
cd click_captcha

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

## ⚙️ Configuration

### Environment Variables

The following parameters can be configured through environment variables or in a `.env` file:

- `REDIS_URL`: Redis connection URL (default: `redis://:root@localhost:6379`)
- `IMAGES_DIR`: Background images directory path (default: `click_captcha/static/images`)
- `FONTS_DIR`: Font files directory path (default: `click_captcha/static/fonts`)
- `ENVIRONMENT`: Runtime environment (default: `development`)
- `CAPTCHA_WIDTH`: CAPTCHA image width (default: 400)
- `CAPTCHA_HEIGHT`: CAPTCHA image height (default: 200)
- `CAPTCHA_EXPIRATION_SECONDS`: CAPTCHA expiration time (seconds, default: 120)
- `MIN_FONT_SIZE`/`MAX_FONT_SIZE`: Font size range (default: 30-45)
- `MAX_ROTATION_ANGLE`: Maximum character rotation angle (default: 30)
- `CLICK_TOLERANCE`: Click tolerance range (pixels, default: 30)

### Font Files

Please place Chinese font files (.ttf or .otf) in the `click_captcha/static/fonts` directory. The system will randomly select a font. If no font file is provided, the system will try to use the system default font.

### Background Images

The system will look for background images from the `click_captcha/static/images` directory. If there are no images in the directory, a default white background will be generated.

## 🚀 Usage

### Starting the Service

```bash
# Activate virtual environment
poetry shell

# Start the service
uvicorn click_captcha.main:app --reload

# Alternatively, run without activating the virtual environment
poetry run uvicorn click_captcha.main:app --reload
```

Visit http://localhost:8000/docs to view the API documentation

## 🔌 API Endpoints

- `GET /api/captcha/`: Generate a new CAPTCHA, returns CAPTCHA ID and Base64 encoded image data
- `POST /api/captcha/verify`: Verify user clicks

## 💾 Redis Requirements

This project uses Redis to store CAPTCHA information and image data. Please ensure that a Redis server is installed and running on your system.
Compared to file storage, using Redis to store base64 encoded image data has the following advantages:
- No need to handle file system operations, reducing I/O burden
- Simplified deployment and scaling, suitable for distributed systems
- Automatic expiration cleaning, no need for additional cleaning tasks
- Improved performance, reduced request processing time

---

# 点选验证码系统

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)

</div>

[English](#click-captcha-system) | 简体中文

基于 FastAPI 实现的点选验证码生成和验证系统。该系统可以生成包含随机中文字符的验证码图片，用户需要按照提示点击特定字符来完成验证。

![image](https://github.com/user-attachments/assets/6971a7cc-8bad-48ae-b279-293a685a2a94)


## 📋 目录

- [功能特点](#-功能特点)
- [安装方法](#-安装方法)
- [配置说明](#️-配置说明)
- [使用方法](#-使用方法)
- [API接口](#-api接口)
- [Redis要求](#-redis要求)

## ✨ 功能特点

- 生成包含随机中文汉字的点选验证码
- 支持汉字大小不一，旋转角度不同
- 提供简单易用的API接口
- 使用Redis存储验证码信息和图片的base64编码数据
- 验证码有效期和配置可自定义
- 支持自定义背景图片
- 支持严格模式和宽松模式验证

## 🔧 安装方法

### 使用Poetry（推荐）

```bash
# 克隆仓库
git clone https://github.com/yourusername/click_captcha.git
cd click_captcha

# 安装依赖
poetry install
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/click_captcha.git
cd click_captcha

# 安装Poetry（如果尚未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install
```

## ⚙️ 配置说明

### 环境变量

可以通过环境变量或在`.env`文件中配置以下参数：

- `REDIS_URL`: Redis连接URL（默认: `redis://:root@localhost:6379`）
- `IMAGES_DIR`: 背景图片目录路径（默认: `click_captcha/static/images`）
- `FONTS_DIR`: 字体文件目录路径（默认: `click_captcha/static/fonts`）
- `ENVIRONMENT`: 运行环境（默认: `development`）
- `CAPTCHA_WIDTH`: 验证码图片宽度（默认：400）
- `CAPTCHA_HEIGHT`: 验证码图片高度（默认：200）
- `CAPTCHA_EXPIRATION_SECONDS`: 验证码过期时间（秒，默认：120）
- `MIN_FONT_SIZE`/`MAX_FONT_SIZE`: 字体大小范围（默认：30-45）
- `MAX_ROTATION_ANGLE`: 字符最大旋转角度（默认：30）
- `CLICK_TOLERANCE`: 点击偏差容忍度（像素，默认：30）

### 字体文件

请将中文字体文件(.ttf或.otf)放在 `click_captcha/static/fonts` 目录下，系统将随机选择一种字体。如果没有提供字体文件，系统将尝试使用系统默认字体。

### 背景图片

系统会从 `click_captcha/static/images` 目录查找背景图片。如果目录中没有图片，将生成默认的白色背景。

## 🚀 使用方法

### 启动服务

```bash
# 激活虚拟环境
poetry shell

# 启动服务
uvicorn click_captcha.main:app --reload

# 或者，不激活虚拟环境直接运行
poetry run uvicorn click_captcha.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

## 🔌 API接口

- `GET /api/captcha/`: 生成新的验证码，返回验证码ID和Base64编码的图片数据
- `POST /api/captcha/verify`: 验证用户点击是否正确

## 💾 Redis要求

本项目使用Redis存储验证码信息和图片数据，请确保您的系统中已安装并运行Redis服务器。

相比于文件存储，使用Redis存储base64编码的图片数据有以下优势：
- 无需处理文件系统操作，减少I/O负担
- 简化部署和扩展，适合分布式系统
- 自动过期清理，无需额外的清理任务
- 提高性能，减少请求处理时间
