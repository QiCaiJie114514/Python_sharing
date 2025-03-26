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
pygame.display.set_caption("弹幕播放器 | ESC退出 | F:切换字体 | I:图片弹幕 | R:重载配置")

# 配置文件路径（全部整合到config目录）
CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DANMAKU_CONFIG = os.path.join(CONFIG_DIR, "danmaku_config.txt")
IMAGE_CONFIG = os.path.join(CONFIG_DIR, "image_config.txt")

# 默认配置
DEFAULT_CONFIG = {
    "font": {
        "paths": ["fonts/ew.ttf", "fonts/simhei.ttf"],
        "current_index": 0,
        "size": 30
    },
    "danmaku": {
        "text_file": "danmaku.txt",  # 相对路径，会在load_resources中处理
        "color_file": "colors.txt",   # 相对路径，会在load_resources中处理
        "speed_range": [3, 8],
        "max_count": 50
    },
    "image": {
        "dir": "images",
        "speed_range": [1, 3],
        "scale_range": [0.2, 0.4],
        "max_count": 5
    }
}

# 系统状态
current_config = DEFAULT_CONFIG.copy()
danmaku_list = []
image_danmaku_list = []
loaded_images = []
show_image_danmaku = True
danmaku_texts = []
color_list = []

def parse_color(color_str):
    """解析颜色字符串"""
    color_str = color_str.strip()
    
    if color_str.startswith('#'):
        hex_str = color_str[1:]
        try:
            if len(hex_str) == 3:
                return (int(hex_str[0]*2, 16), int(hex_str[1]*2, 16), int(hex_str[2]*2, 16))
            elif len(hex_str) == 6:
                return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
        except ValueError:
            pass
    
    if '(' in color_str and ')' in color_str:
        color_str = color_str.split('(')[1].split(')')[0]
    
    try:
        parts = [p.strip() for p in color_str.replace(',', ' ').split()]
        if len(parts) == 3:
            return (min(255, max(0, int(parts[0]))),
                    min(255, max(0, int(parts[1]))),
                    min(255, max(0, int(parts[2]))))
    except (ValueError, IndexError):
        pass
    
    color_map = {
        'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
        'white': (255, 255, 255), 'black': (0, 0, 0),
        'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255)
    }
    return color_map.get(color_str.lower(), (255, 255, 255))

def valid_color(color_tuple):
    """验证颜色元组是否有效"""
    return (isinstance(color_tuple, tuple) and 
            len(color_tuple) == 3 and
            all(0 <= c <= 255 for c in color_tuple))

def switch_font():
    """切换字体功能"""
    fonts = current_config["font"]["paths"]
    if not fonts:
        return
    
    current_idx = current_config["font"]["current_index"]
    new_idx = (current_idx + 1) % len(fonts)
    current_config["font"]["current_index"] = new_idx
    
    print(f"字体已切换至: {fonts[new_idx]}")
    
    for dmk in danmaku_list:
        dmk.refresh_font()
        dmk.update_surface()

def ensure_config_dir():
    """确保配置目录存在"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        print(f"已创建配置目录: {CONFIG_DIR}")

def load_config():
    """加载主配置文件"""
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            
            # 处理旧版单路径配置
            if "font" in config and "path" in config["font"]:
                config["font"]["paths"] = [config["font"]["path"]]
                del config["font"]["path"]
            
            # 合并配置
            for key in DEFAULT_CONFIG:
                if key in config:
                    if isinstance(config[key], dict):
                        current_config[key].update(config[key])
                    else:
                        current_config[key] = config[key]
                        
    except FileNotFoundError:
        print(f"配置文件 {CONFIG_FILE} 不存在，使用默认配置")
        # 创建默认配置文件
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"配置加载错误: {e}")

def load_danmaku_config():
    """加载弹幕动态配置"""
    try:
        with open(DANMAKU_CONFIG, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    key = key.strip().lower()
                    
                    if key == "speed_range":
                        current_config["danmaku"]["speed_range"] = [
                            float(x) for x in value.split(",")]
                    elif key == "max_count":
                        current_config["danmaku"]["max_count"] = int(value)
                    elif key == "text_file":
                        # 保持相对路径，在load_resources中处理
                        current_config["danmaku"]["text_file"] = value.strip()
                    elif key == "color_file":
                        # 保持相对路径，在load_resources中处理
                        current_config["danmaku"]["color_file"] = value.strip()
    except FileNotFoundError:
        print(f"弹幕配置文件 {DANMAKU_CONFIG} 不存在")
        # 创建空配置文件
        with open(DANMAKU_CONFIG, "w", encoding="utf-8") as f:
            f.write("# 弹幕配置\nspeed_range=3,8\nmax_count=50\n")

def load_image_config():
    """加载图片动态配置"""
    try:
        with open(IMAGE_CONFIG, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    key = key.strip().lower()
                    
                    if key == "speed_range":
                        current_config["image"]["speed_range"] = [
                            float(x) for x in value.split(",")]
                    elif key == "scale_range":
                        current_config["image"]["scale_range"] = [
                            float(x) for x in value.split(",")]
                    elif key == "max_count":
                        current_config["image"]["max_count"] = int(value)
                    elif key == "dir":
                        current_config["image"]["dir"] = value.strip()
    except FileNotFoundError:
        print(f"图片配置文件 {IMAGE_CONFIG} 不存在")
        # 创建空配置文件
        with open(IMAGE_CONFIG, "w", encoding="utf-8") as f:
            f.write("# 图片弹幕配置\ndir=images\nspeed_range=1,3\nscale_range=0.2,0.4\nmax_count=5\n")

def load_resources():
    """加载所有资源"""
    global danmaku_texts, color_list, loaded_images
    
    ensure_config_dir()
    
    # 处理弹幕文本文件路径
    text_file = current_config["danmaku"]["text_file"]
    if not os.path.isabs(text_file):  # 如果是相对路径
        text_file = os.path.join(CONFIG_DIR, text_file)
    
    # 加载弹幕文本
    try:
        with open(text_file, "r", encoding="utf-8") as f:
            danmaku_texts = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"弹幕文本文件 {text_file} 不存在")
        danmaku_texts = ["默认弹幕"]
        # 在config目录创建文件
        with open(os.path.join(CONFIG_DIR, "danmaku.txt"), "w", encoding="utf-8") as f:
            f.write("默认弹幕\n")
    except Exception as e:
        print(f"弹幕文本加载错误: {e}")
        danmaku_texts = ["默认弹幕"]
    
    # 处理颜色文件路径
    color_file = current_config["danmaku"]["color_file"]
    if not os.path.isabs(color_file):  # 如果是相对路径
        color_file = os.path.join(CONFIG_DIR, color_file)
    
    # 加载颜色配置
    color_list = []
    try:
        with open(color_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    color = parse_color(line)
                    if valid_color(color):
                        color_list.append(color)
    except FileNotFoundError:
        print(f"颜色文件 {color_file} 不存在")
        color_list = [(255,255,255), (255,0,0), (0,255,0), (0,0,255)]
        # 在config目录创建文件
        with open(os.path.join(CONFIG_DIR, "colors.txt"), "w", encoding="utf-8") as f:
            f.write("# 颜色配置\n255,255,255\n255,0,0\n0,255,0\n0,0,255\n")
    except Exception as e:
        print(f"颜色加载错误: {e}")
        color_list = [(255,255,255)]
    
    # 加载图片
    loaded_images = []
    img_dir = current_config["image"]["dir"]
    try:
        if os.path.exists(img_dir):
            for f in os.listdir(img_dir):
                full_path = os.path.join(img_dir, f)
                if os.path.isfile(full_path) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    loaded_images.append(full_path)
        else:
            print(f"图片目录不存在: {img_dir}")
    except Exception as e:
        print(f"图片加载失败: {e}")

class Danmaku:
    def __init__(self):
        self.refresh_font()
        self.text = random.choice(danmaku_texts)
        self.color = random.choice(color_list)
        self.speed = random.uniform(*current_config["danmaku"]["speed_range"])
        self.x = SCREEN_WIDTH
        self.y = random.randint(0, SCREEN_HEIGHT - current_config["font"]["size"])
        self.update_surface()

    def refresh_font(self):
        fonts = current_config["font"]["paths"]
        if fonts:
            try:
                font_path = fonts[current_config["font"]["current_index"]]
                self.font = pygame.font.Font(font_path, current_config["font"]["size"])
                return
            except Exception as e:
                print(f"字体加载失败: {e}")
        
        self.font = pygame.font.SysFont("simhei", current_config["font"]["size"])

    def update_surface(self):
        self.surface = self.font.render(self.text, True, self.color)

    def update(self):
        self.x -= self.speed
        if self.x < -self.surface.get_width():
            self.__init__()

    def draw(self):
        screen.blit(self.surface, (self.x, self.y))

class ImageDanmaku:
    def __init__(self):
        self.safe_init()

    def safe_init(self):
        try:
            self.load_image()
            self.speed = random.uniform(*current_config["image"]["speed_range"])
            self.x = SCREEN_WIDTH
            max_y = max(0, SCREEN_HEIGHT - self.height)
            self.y = random.randint(0, max_y) if max_y > 0 else 0
        except:
            self.create_fallback()

    def load_image(self):
        try:
            img_path = random.choice(loaded_images)
            self.image = pygame.image.load(img_path).convert_alpha()
            
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            scale = random.uniform(*current_config["image"]["scale_range"])
            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
        except Exception as e:
            print(f"图片加载失败: {e}")
            raise

    def create_fallback(self):
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 128))
        self.width = 50
        self.height = 50

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.safe_init()

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# 初始化配置
load_config()
load_danmaku_config()
load_image_config()
load_resources()

# 创建弹幕实例
danmaku_list = [Danmaku() for _ in range(current_config["danmaku"]["max_count"])]
image_danmaku_list = [ImageDanmaku() for _ in range(current_config["image"]["max_count"])] if loaded_images else []

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:  # 重载配置
                prev_font_idx = current_config["font"]["current_index"]
                load_config()
                load_danmaku_config()
                load_image_config()
                load_resources()
                danmaku_list = [Danmaku() for _ in range(current_config["danmaku"]["max_count"])]
                image_danmaku_list = [ImageDanmaku() for _ in range(current_config["image"]["max_count"])] if loaded_images else []
                current_config["font"]["current_index"] = prev_font_idx
                print("配置已重载")
            elif event.key == pygame.K_i:  # 切换图片弹幕
                show_image_danmaku = not show_image_danmaku
                print(f"图片弹幕 {'显示' if show_image_danmaku else '隐藏'}")
            elif event.key == pygame.K_f:  # 切换字体
                switch_font()

    # 先绘制图片
    if show_image_danmaku and loaded_images:
        for img_dmk in image_danmaku_list:
            img_dmk.update()
            img_dmk.draw()
    
    # 后绘制文字
    for dmk in danmaku_list:
        dmk.update()
        dmk.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
