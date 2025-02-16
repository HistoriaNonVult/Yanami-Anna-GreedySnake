"""
贪吃蛇游戏配置文件
包含游戏中使用的所有常量和配置项
"""

from enum import Enum

# 窗口样式配置
class WindowStyle(Enum):
    DARK = "dark"          # 深色主题
    MICA = "mica"          # 云母效果（Windows 11）
    AERO = "aero"          # 玻璃效果（经典）
    TRANSPARENT = "transparent"  # 透明效果
    ACRYLIC = "acrylic"    # 亚克力效果
    WIN7 = "win7"          # Windows 7风格
    INVERSE = "inverse"    # 反色效果
    POPUP = "popup"        # 弹出窗口风格
    NATIVE = "native"      # 原生风格
    OPTIMISED = "optimised"  # 优化风格
    LIGHT = "light"        # 浅色主题

# 音频配置
AUDIO_CONFIG = {
    'SAMPLE_RATE': 44100,
    'SAMPLE_SIZE': -16,
    'CHANNELS': 2,
    'BUFFER': 2048,
    'MAX_CHANNELS': 32
}

# 游戏模式
class GameMode(Enum):
    FORBID = "Forbid"      # 禁止模式
    NORMAL = "Normal"      # 普通模式
    HARD = "Hard"          # 困难模式

# 食物配置
FOOD_CONFIG = {
    'REGULAR': {'color': 'red', 'points': 1, 'effect': None},
    'GOLDEN': {'color': 'yellow', 'points': 3, 'effect': 'speed_boost'},
    'PURPLE': {'color': 'purple', 'points': 5, 'effect': 'slow_down'},
    'MANA': {'color': 'gradient', 'points': 10, 'effect': 'special'},
    'FLOWER': {'color': 'changing', 'points': 6, 'effect': 'switch_background'}
}

# 游戏配置
GAME_CONFIG = {
    'WINDOW_WIDTH': 410,
    'WINDOW_HEIGHT': 780,
    'DIRECTION_CHANGE_INTERVAL': 0.10,  # 方向改变间隔（秒）
    'BASE_SPEED': 1.0,
    'BOOST_SPEED_MULTIPLIER': 1.5,
    'SLOW_SPEED_MULTIPLIER': 0.7
}

# 颜色配置
COLORS = {
    'BACKGROUND': '#050505',
    'TITLE_BAR': '#0D1526',
    'BORDER_PRIMARY': '#00F2FF',
    'BORDER_SECONDARY': '#FF2D55',
    'TEXT_PRIMARY': '#FFD700',
    'TEXT_HOVER': '#FF2D55'
}

# 音效配置
SOUND_EFFECTS = {
    'eat': ('eat.mp3', 1.0),
    'milestone': ('milestone.wav', 1.0),
    'death': ('death.wav', 0.08),
    'water_ripple': ('water_ripple.wav', 0.2)
}
