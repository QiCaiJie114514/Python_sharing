# -*- coding: utf-8 -*-
import pygame
import random
import sys
import os
import json

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("弹幕播放器 | ESC退出")

# 配置文件
CONFIG_FILE = "font_config.json"        # 按键-字体映射配置文件
FONT_DIR = "fonts"                      # 字体文件目录
TEXT_FILE = "danmaku.txt"               # 弹幕文本文件
COLOR_FILE = "colors.txt"               # 颜色配置文件

# 默认配置
DEFAULT_CONFIG = {
    "K_1": "ew.ttf"
}

# 系统状态
current_font = "ew.ttf"               # 当前使用字体
font_mapping = {}                       # 按键-字体映射字典

def load_config():
    """加载按键-字体映射配置"""
    global font_mapping
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 转换字符串按键名为PyGame常量
            font_mapping = {
                getattr(pygame, k): v 
                for k, v in config.items() 
                if hasattr(pygame, k)
            }
    except FileNotFoundError:
        print("配置文件不存在，使用默认配置")
        font_mapping = {
            getattr(pygame, k): v 
            for k, v in DEFAULT_CONFIG.items()
        }
    except Exception as e:
        print(f"加载配置失败: {e}")
        font_mapping = {}

def load_resources():
    """加载所有资源"""
    global danmaku_texts, color_list
    # 加载弹幕文本
    danmaku_texts = load_file(TEXT_FILE, ["默认弹幕"], lambda x: x)
    # 加载颜色配置
    raw_colors = load_file(COLOR_FILE, [(255,255,255)], parse_color)
    color_list = [c for c in raw_colors if valid_color(c)]

def load_file(file_path, default, parser):
    """通用文件加载函数"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [parser(line.strip()) for line in f if line.strip()]
    except:
        return default

def parse_color(color_str):
    """解析颜色字符串"""
    try:
        if color_str.startswith("#"):
            hex = color_str.lstrip("#")
            return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        return tuple(map(int, color_str.split(",")))
    except:
        return None

def valid_color(color):
    """验证颜色有效性"""
    return color and len(color)==3 and all(0<=v<=255 for v in color)

class Danmaku:
    def __init__(self):
        self.refresh_font()
        self.text = random.choice(danmaku_texts)
        self.color = random.choice(color_list)
        self.speed = random.randint(3, 8)
        self.x = SCREEN_WIDTH
        self.y = random.randint(0, SCREEN_HEIGHT - FONT_SIZE)
        self.update_surface()

    def refresh_font(self):
        """刷新字体（切换时调用）"""
        try:
            font_path = os.path.join(FONT_DIR, current_font)
            self.font = pygame.font.Font(font_path, FONT_SIZE)
        except Exception as e:
            print(f"字体加载失败: {e}")
            self.font = pygame.font.SysFont("simhei", FONT_SIZE)

    def update_surface(self):
        """更新文字表面"""
        self.surface = self.font.render(self.text, True, self.color)

    def update(self):
        self.x -= self.speed
        if self.x < -self.surface.get_width():
            self.__init__()

    def draw(self):
        screen.blit(self.surface, (self.x, self.y))

# 初始化配置和资源
FONT_SIZE = 30
MAX_DANMAKU = 50
load_config()
load_resources()
danmaku_list = [Danmaku() for _ in range(MAX_DANMAKU)]

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in font_mapping:  # 字体切换
                new_font = font_mapping[event.key]
                if os.path.exists(os.path.join(FONT_DIR, new_font)):
                    current_font = new_font
                    # 更新所有弹幕字体
                    for dmk in danmaku_list:
                        dmk.refresh_font()
                        dmk.update_surface()
                    print(f"已切换字体：{current_font}")
                else:
                    print(f"字体文件不存在：{new_font}")
            elif event.key == pygame.K_r:  # 重载配置
                load_config()
                load_resources()
                print("配置已重载")

    # 更新并绘制弹幕
    for dmk in danmaku_list:
        dmk.update()
        dmk.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
