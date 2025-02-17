import tkinter as tk
from PIL import Image, ImageTk
import random
import pygame
import os
import math
import time
import sys
from pathlib import Path
import customtkinter as ctk
from collections import deque
import ctypes
import pywinstyles  # 导入窗口样式库
import array
from concurrent.futures import ThreadPoolExecutor
last_direction_change_time = 0
direction_change_interval = 0.10  # 0.05秒的时间间隔
# 窗口样式对照表
WINDOW_STYLES = {
    0: "dark",       # 深色主题
    1: "mica",       # 云母效果（Windows 11）
    2: "aero",       # 玻璃效果（经典）
    3: "transparent", # 透明效果
    4: "acrylic",    # 亚克力效果
    5: "win7",       # Windows 7风格
    6: "inverse",    # 反色效果
    7: "popup",      # 弹出窗口风格
    8: "native",     # 原生风格
    9: "optimised",  # 优化风格
    10: "light"      # 浅色主题
}
# For YOLO!!!!!!
# 初始化 pygame
# 在初始化 pygame 时设置更高的音频质量
pygame.mixer.pre_init(44100, -16, 2, 2048)  # 设置更高的采样率和缓冲区
pygame.mixer.init()

# 设置混音器质量
pygame.mixer.set_num_channels(32)  # 增加同时播放的声道数
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

Game_Mode = "Forbid"  # 默认为 Forbid 模式
high_score = 0
# 添加音效管理器类
class SoundManager:
    def __init__(self):
        self._sounds = {}
        self._sound_paths = {
            'eat': ('eat.mp3', 1.0),
            'milestone': ('milestone.wav', 1.0),
            'death': ('death.wav', 0.08),
            'water_ripple': ('water_ripple.wav', 0.2)
        }
        # 分离音效和音乐的控制
        self.sfx_enabled = True
        self.bgm_enabled = True
        # 预加载所有音效
        self._preload_sounds()
        
        # 创建音效通道池
        self._channels = [pygame.mixer.Channel(i) for i in range(8)]
        self._channel_index = 0
    
    def _preload_sounds(self):
        """预加载所有音效"""
        try:
            for sound_name, (filename, volume) in self._sound_paths.items():
                path = os.path.join(current_dir, "assets", "music", filename)
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                # 转换音频格式以减少CPU使用
                sound = pygame.mixer.Sound(sound.get_raw())
                self._sounds[sound_name] = sound
        except Exception as e:
            print(f"预加载音效失败: {e}")
    
    def set_mode(self, mode):
        """根据模式设置音频状态"""
        if mode == "off":
            self.bgm_enabled = False
            self.sfx_enabled = True
        else:
            self.bgm_enabled = True
            self.sfx_enabled = True
    
    def play(self, sound_name):
        """播放音效"""
        if not self.sfx_enabled or sound_name not in self._sounds:
            return
            
        try:
            # 使用通道池循环播放音效
            channel = self._channels[self._channel_index]
            if not channel.get_busy():
                channel.play(self._sounds[sound_name])
                self._channel_index = (self._channel_index + 1) % len(self._channels)
        except Exception as e:
            print(f"播放音效 {sound_name} 失败: {e}")
    
    def play_bgm(self, music_name):
        """播放背景音乐"""
        if not self.bgm_enabled:
            return
            
        try:
            bgm_path = os.path.join(current_dir, "assets", "music", f"{music_name}.mp3")
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"播放背景音乐失败: {e}")
    
    def stop_bgm(self):
        """停止背景音乐"""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"停止背景音乐失败: {e}")
    
    def cleanup(self):
        """清理音效资源"""
        try:
            self.stop_bgm()
            # 停止所有通道
            for channel in self._channels:
                channel.stop()
            self._sounds.clear()
        except Exception as e:
            print(f"清理音效资源失败: {e}")

def get_data_dir():
    """获取数据存储目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的程序
        if os.name == 'nt':  # Windows
            data_dir = os.path.join(os.environ['APPDATA'], 'GreedySnake')
        else:  # Linux/Mac
            data_dir = os.path.join(str(Path.home()), '.greedysnake')
    else:
        # 如果是开发环境
        data_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确保目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    return data_dir

def initialize_high_score_file():
    """初始化最高分文件"""
    data_dir = get_data_dir()
    high_score_path = os.path.join(data_dir, 'high_score.txt')
    high_score_path_2 = os.path.join(data_dir, 'high_score_2.txt')
    if Game_Mode == "Pass":
        high_score_path = high_score_path_2
    # 如果文件不存在，创建它并初始化为0
    if not os.path.exists(high_score_path):
        try:
            with open(high_score_path, 'w') as file:
                file.write('0')
            print(f"Created high score file at: {high_score_path}")
        except Exception as e:
            print(f"Error creating high score file: {e}")

def load_high_score():
    """加载最高分"""
    data_dir = get_data_dir()
    high_score_path = os.path.join(data_dir, 'high_score.txt')
    high_score_path_2 = os.path.join(data_dir, 'high_score_2.txt')
    if Game_Mode == "Pass":
        high_score_path = high_score_path_2
    try:
        # 如果文件不存在，先创建它
        if not os.path.exists(high_score_path):
            initialize_high_score_file()
            
        # 读取最高分
        with open(high_score_path, 'r') as file:
            return int(file.read())
    except Exception as e:
        print(f"Error loading high score: {e}")
        return 0

def save_high_score(score):
    """保存最高分"""
    data_dir = get_data_dir()
    high_score_path = os.path.join(data_dir, 'high_score.txt')
    high_score_path_2 = os.path.join(data_dir, 'high_score_2.txt')
    if Game_Mode == "Pass":
        high_score_path = high_score_path_2
    try:
        with open(high_score_path, 'w') as file:
            file.write(str(score))
    except Exception as e:
        print(f"Error saving high score: {e}")
        
class TransparentWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Instructions")
        
        # Set window size and position
        window_width = 480
        window_height = 880
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set window properties
        self.window.attributes('-alpha', 0.95)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # Create main frame
        self.main_frame = tk.Frame(
            self.window,
            bg='#070B14'
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create neon border effects
        self.outer_border = tk.Frame(
            self.main_frame,
            bg='#070B14',
            highlightbackground='#00F2FF',
            highlightthickness=2
        )
        self.outer_border.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        self.inner_border = tk.Frame(
            self.outer_border,
            bg='#070B14',
            highlightbackground='#FF2D55',
            highlightthickness=1
        )
        self.inner_border.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title bar
        self.title_bar = tk.Frame(
            self.inner_border,
            bg='#0D1526',
            height=40
        )
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # Add decorative lines
        self.create_tech_lines()
        
        # Bind drag events
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        
        # Close button
        close_frame = tk.Frame(self.title_bar, bg='#0D1526')
        close_frame.pack(side=tk.RIGHT, padx=5)
        
        close_button = tk.Label(
            close_frame,
            text='⬡',
            bg='#0D1526',
            fg='#00F2FF',
            font=('Consolas', 20)
        )
        close_button.pack(side=tk.RIGHT)
        close_button.bind('<Button-1>', lambda e: self.window.destroy())
        close_button.bind('<Enter>', lambda e: self.pulse_effect(close_button))
        
        # Title
        self.title_label = tk.Label(
            self.title_bar,
            text='INSTRUCTIONS',
            bg='#0D1526',
            fg='#00F2FF',
            font=('Orbitron', 14, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, padx=15)
        
        # 创建装饰线Canvas
        self.deco_canvas = tk.Canvas(
            self.title_bar,
            width=100,
            height=20,
            bg='#0D1526',
            highlightthickness=0
        )
        self.deco_canvas.pack(side=tk.LEFT)
        self.window.bind('<Left>', lambda e: self._move_window('left'))
        self.window.bind('<Right>', lambda e: self._move_window('right'))
        self.window.bind('<Up>', lambda e: self._move_window('up'))
        self.window.bind('<Down>', lambda e: self._move_window('down'))
        # 创建能量脉冲动画
        def animate_pulse():
            self.deco_canvas.delete('all')
            
            # 基础线
            self.deco_canvas.create_line(
                0, 10, 100, 10,
                fill='#0A2A40',
                width=1
            )
            
            # 计算脉冲位置
            t = time.time() * 1.3  # 加快脉冲速度
            pulse_pos = (t % 1) * 100  # 控制脉冲移动速度
            
            # 绘制脉冲效果
            for x in range(100):
                dist = abs(x - pulse_pos)
                if dist < 15:  # 缩短脉冲长度使其更锐利
                    intensity = (1 - dist/15) * 255
                    color = f'#00{int(intensity):02x}FF'
                    self.deco_canvas.create_line(
                        x, 10, x+1, 10,
                        fill=color,
                        width=2
                    )
            
            self.window.after(20, animate_pulse)  # 提高刷新率
            
        animate_pulse()
        
        # Content area
        content_frame = tk.Frame(
            self.inner_border,
            bg='#070B14'
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Add instruction text
        instructions = [
            ("Basic Controls", [
                "Arrow Keys ↑←↓→: Control snake movement",
                "WASD Keys: Alternative movement controls",
                "Mouse: Alternative movement controls",
                "Space Bar: Pause/Resume game",
                "P Key: Pause/Resume game",
                "R Key: Restart game",
                "B Key: Return to main menu",
                "Shift/Control + Arrow/WASD: Move window",
                "Shift + H: Show this instruction window"
            ]),
            ("Food System", [
                "Regular Food: Red, +1 point",
                "Golden Food: Yellow, +3 points, Speed boost effect",
                "Purple Food: Purple, +5 points, Slow down effect",
                "Mana Food: Gradient, +10 points, Special effect",
                "Flower Food: Changing, +6 points, Switch background"
            ]),
            ("Game Features", [
                "Scoring System: Different foods give different points",
                "Speed Changes: Certain foods modify movement speed",
                "High Score: Automatically saves your best score"
            ]),
            ("Interface Guide", [
                "Top Left: Current score display",
                "Game Area: Picture background main playing field",
                "Pause Menu: Shows game control options"
            ]),
            ("Sound System", [
                "Eating Sound: Plays when consuming food",
                "Milestone Sound: Plays at specific score thresholds",
                "Death Sound: Plays on game over",
                "Background Music: Plays during gameplay"
            ]),
            ("Game Tips", [
                "Focus on collecting high-value special foods",
                "Be extra careful during speed boost effects",
                "Maintain safe distance between snake segments"
            ])
        ]
        
        for section, items in instructions:
            # 添加带有动态效果的标题
            section_frame = tk.Frame(content_frame, bg='#070B14')
            section_frame.pack(fill=tk.X, pady=(10,5))
            
            section_label = tk.Label(
                section_frame,
                text=section,
                bg='#070B14',
                fg='#00F2FF',
                font=('Orbitron', 12, 'bold')
            )
            section_label.pack(side=tk.LEFT)
            
            # 添加动态装饰线
            line_canvas = tk.Canvas(
                section_frame,
                height=2,
                bg='#070B14',
                highlightthickness=0
            )
            line_canvas.pack(fill=tk.X, side=tk.LEFT, padx=(10,0), pady=8)
            
            # Add items
            for item in items:
                item_label = tk.Label(
                    content_frame,
                    text=f"• {item}",
                    bg='#070B14',
                    fg='#FFD700',
                    font=('Consolas', 10)
                )
                item_label.pack(anchor='w', padx=10)
                
                # 添加悬停效果
                item_label.bind('<Enter>', 
                    lambda e, lbl=item_label: lbl.configure(fg='#FF2D55'))
                item_label.bind('<Leave>', 
                    lambda e, lbl=item_label: lbl.configure(fg='#FFD700'))
        
        # Bind shortcuts
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        # Add fade-in effect
        self.window.attributes('-alpha', 0.0)
        self.advanced_fade_in()
        
        # Start animations
        self.start_animations()
    
    def create_tech_lines(self):
        """Create decorative tech lines"""
        canvas = tk.Canvas(
            self.title_bar,
            height=3,
            bg='#0D1526',
            highlightthickness=0
        )
        canvas.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.tech_lines = []
        for i in range(5):
            line = canvas.create_line(
                0, 1, 0, 1,
                fill='#00F2FF',
                width=2,
                smooth=True
            )
            self.tech_lines.append(line)
    
    def pulse_effect(self, widget):
        """Create pulsing glow effect"""
        def pulse():
            if not self.window.winfo_exists():
                return
            t = time.time()
            intensity = int(200 + 55 * math.sin(t * 4))
            widget.configure(fg=f'#{intensity:02x}{intensity:02x}FF')
            self.window.after(50, pulse)
        pulse()
    
    def advanced_fade_in(self, alpha=0.0):
        """Fade-in effect"""
        if alpha < 0.95:
            alpha = min(alpha + 0.05, 0.95)
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.advanced_fade_in(alpha))
    
    def start_animations(self):
        """Start animation effects"""
        self.animate_tech_lines()
        self.animate_borders()
    
    def animate_tech_lines(self):
        """Animation effect: tech lines"""
        if not self.window.winfo_exists():
            return
        width = self.title_bar.winfo_width()
        t = time.time()
        
        # 外边框颜色
        r1 = int(128 + 127 * math.sin(t * 2.0))
        g1 = int(128 + 127 * math.sin(t * 2.0 + 2.0))
        outer_color = f'#{r1:02x}{g1:02x}FF'
        
        # 内边框颜色
        r2 = int(128 + 127 * math.sin(t * 2.0 + 3.0))
        inner_color = f'#FF{r2:02x}{r2:02x}'
        
        self.outer_border.config(highlightbackground=outer_color)
        self.inner_border.config(highlightbackground=inner_color)
        
        self.window.after(50, self.animate_borders)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    def _move_window(self, direction):
        """移动窗口"""
        print(f"Moving window: {direction}")  # 添加调试输出
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        
        step = 20  # 每次移动的像素数
        
        if direction == 'left':
            x -= step
        elif direction == 'right':
            x += step
        elif direction == 'up':
            y -= step
        elif direction == 'down':
            y += step
        
        # 确保窗口不会移出屏幕
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        # 限制x坐标范围
        x = max(0, min(x, screen_width - window_width))
        # 限制y坐标范围
        y = max(0, min(y, screen_height - window_height))
        
        print(f"New position: x={x}, y={y}")  # 添加调试输出
        self.window.geometry(f"+{x}+{y}")
# 创建开始页面类
class StartPage:
    def show_transparent_window(self, event):
        TransparentWindow(self.window)
    def __init__(self):
        # 直接创建主窗口
        self.window = tk.Tk()
        
        # 在创建后立即设置大小为0并移到屏幕外
        self.window.geometry("1x1+-100+-100")
        
        # 设置所有属性
        self.window.focus_force()  # 强制获取焦点
        self.window.lift()         # 将窗口提升到最前面
        self.window.bind('<Shift-h>', self.show_transparent_window)
        self.window.bind('<Shift-H>', self.show_transparent_window)
        
        # 立即更新窗口以应用初始设置
        self.window.update_idletasks()
        
        # 如果是Windows系统，可以使用系统主题
        if os.name == 'nt':  # Windows
            # 初始设置完全透明
            self.window.attributes('-alpha', 0.0)
            
            # 创建淡入效果
            def fade_in():
                alpha = self.window.attributes('-alpha')
                if alpha < 0.920:
                    alpha += 0.058
                    self.window.attributes('-alpha', alpha)
                    self.window.after(20, fade_in)
            
            # 启动淡入效果
            self.window.after(100, fade_in)
            
        self.window.title("Greedy Snake")
        self.window.configure(bg='#050505')  # 设置背景色
        self.window.resizable(False, False)
        try:
            # 使用亚克力效果（推荐）
            pywinstyles.apply_style(self.window, "dark")
            
            # 或者使用透明效果
            # pywinstyles.apply_style(self.window, "transparent")
        except Exception as e:
            print(f"应用窗口样式失败: {e}")
         
        # 然后再处理音乐模式变量
        if not hasattr(StartPage, 'music_mode'):
            StartPage.music_mode = tk.StringVar(value="always")  # 现在可以安全地创建变量
        self.music_mode = StartPage.music_mode  # 使用类变量
        
        # 设置窗口大小和位置
        window_width = 410
        window_height = 780
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 添加图标
        icon_path = os.path.join(current_dir, "assets", "images", "snake_icon.ico")
        self.window.iconbitmap(icon_path)
        
        # 创建主框架
        main_frame = tk.Frame(self.window, bg='#050505')
        main_frame.pack(fill='both', expand=True)
        
        # 创建三个独立的画布用于边框（添加测试背景色）
        self.left_canvas = tk.Canvas(
            self.window,  # 改用self.window作为父容器
            width=10,     # 增加宽度
            height=780,
            bg='#050505',     # 改回黑色
            highlightthickness=0
        )
        self.left_canvas.place(x=0, y=0)
        
        self.bottom_canvas = tk.Canvas(
            self.window,  # 改用self.window作为父容器
            width=410,
            height=10,    # 增加高度
            bg='#050505',     # 改回黑色
            highlightthickness=0
        )
        self.bottom_canvas.place(x=0, y=770)  # 调整y坐标
        
        self.right_canvas = tk.Canvas(
            self.window,  # 改用self.window作为父容器
            width=10,     # 增加宽度
            height=780,
            bg='#050505',     # 改回黑色
            highlightthickness=0
        )
        self.right_canvas.place(x=400, y=0)
        
        
        # 添加霓虹灯颜色列表
        self.neon_colors = [
            '#FF1493',  # 深粉红
            '#00FFFF',  # 青色
            '#FF69B4',  # 粉红
            '#4169E1',  # 皇家蓝
            '#9400D3',  # 紫罗兰
            '#00FF7F',  # 春绿
            '#FF4500',  # 橙红色
            '#1E90FF'   # 道奇蓝
        ]
        self.color_index = 0
        self.color_transition = 0.0
        
        # 初始化霓虹效果
        self.window.after(50, self.start_neon_effect)
        
        # 创建画布（用于霓虹边框）
        self.canvas = tk.Canvas(
            main_frame,
            width=400,
            height=780,
            bg='#050505',
            highlightthickness=0
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)  # 使用place而不是pack
        
        # 添加标题
        # 创建标题标签
        title_label = tk.Label(
            main_frame,
            text="Greedy Snake",
            font=("Verdana", 37, "bold"),
            fg="#4CAF50",
            bg="#050505",
        )
        
        # 定义更加明显的颜色渐变范围
        base_colors = [
            (76, 175, 80),    # #4CAF50 基础绿色
            (96, 195, 100),   # 亮绿色
            (116, 215, 120),  # 更亮的绿色
            (136, 235, 140),  # 最亮的绿色
            (116, 215, 120),  # 回到更亮
            (96, 195, 100),   # 回到亮色
            (76, 175, 80),    # 回到基础
            (56, 155, 60),    # 暗绿色
        ]
        
        def smooth_interpolate(color1, color2, factor):
            # 使用三次方插值实现更平滑的过渡
            smooth_factor = factor * factor * (3 - 2 * factor)
            r = int(color1[0] + (color2[0] - color1[0]) * smooth_factor)
            g = int(color1[1] + (color2[1] - color1[1]) * smooth_factor)
            b = int(color1[2] + (color2[2] - color1[2]) * smooth_factor)
            return f'#{r:02x}{g:02x}{b:02x}'
        
        def gentle_breathing(step=0):
            # 使用适中的周期(0.001)实现缓慢但可察觉的变化
            t = step * 0.001
            # 使用余弦函数使过渡更加平滑
            factor = (math.cos(t) + 1) / 2
            
            # 计算当前应该在哪两个颜色之间插值
            total_colors = len(base_colors)
            index = int(factor * (total_colors - 1))
            next_index = min(index + 1, total_colors - 1)
            local_factor = factor * (total_colors - 1) - index
            
            # 生成当前颜色
            color = smooth_interpolate(
                base_colors[index],
                base_colors[next_index],
                local_factor
            )
            
            # 更新标题颜色
            title_label.config(fg=color)
            # 使用100ms的间隔使变化平滑但可察觉
            main_frame.after(100, lambda: gentle_breathing(step + 1))
        
        # 启动温和的呼吸效果
        gentle_breathing()
        title_label.pack(pady=(20, 10))
        
        # 添加简单
        line_canvas = tk.Canvas(
            main_frame,
            width=300,  # 条长度
            height=2,   # 线条高度
            bg="#050505",
            highlightthickness=0
        )
        line_canvas.pack(pady=(0, 10))  # 上边距0，下边距20
        
        # 画一条简单的渐变线
        for i in range(300):
            # 简单的绿色渐变
            if i < 150:  # 左半部分，从深到浅
                alpha = i / 150
            else:        # 右半部分，从浅到深
                alpha = (300 - i) / 150
            
            color = f"#{int(76*alpha + 40):02x}{int(175*alpha + 40):02x}{int(80*alpha + 40):02x}"
            line_canvas.create_line(
                i, 1, i+1, 1,
                fill=color,
                width=2
            )
        
        # 使用更宽但较低的画
        self.canvas = tk.Canvas(
            main_frame,
            width=400,  # 保持宽度
            height=420,  # 增加高度以容纳说明文本
            bg='#050505',
            highlightthickness=0
        )
        self.canvas.pack(pady=0)
        
        # 绑定鼠标点击事到整个窗口
        self.window.bind("<Button-1>", self.create_firework)
        self.window.bind("<Button-2>", self.create_firework)
        self.window.bind("<Button-3>", self.create_firework)
        self.particle_trails = []
        # 存储烟花粒子
        self.particles = []
        
        # 彩色表
        self.firework_palettes = {
            "rainbow_deluxe": [  # 优化彩虹配色
                "#FF0000",  # 鲜艳红
                "#FF4500",  # 橙红
                "#FFA500",  # 明亮橙
                "#FFD700",  # 金色
                "#32CD32",  # 青翠绿
                "#00BFFF",  # 深天蓝
                "#4169E1",  # 皇家蓝
                "#8A2BE2",  # 紫罗兰
                "#FF69B4",  # 粉红
                "#FF1493"   # 深粉红
            ],
            
            "sunset_dream": [  # 优化晚霞配色
                "#FF6B6B",  # 珊瑚红
                "#FF8C42",  # 橙色
                "#FFA07A",  # 浅鲑鱼色
                "#FFB6C1",  # 浅粉红
                "#FFC3A0",  # 杏色
                "#FFD700",  # 金色
                "#FF9AA2",  # 浅珊瑚色
                "#FFB7B2",  # 浅玫瑰色
                "#FF1493",  # 深粉红
                "#FF69B4"   # 热粉红
            ],
            
            "ocean_deep": [  # 优化深海配色
                "#00FFFF",  # 青色
                "#1E90FF",  # 道奇蓝
                "#00CED1",  # 深青色
                "#4169E1",  # 皇家蓝
                "#0000CD",  # 中蓝色
                "#191970",  # 午夜蓝
                "#7B68EE",  # 中紫罗兰
                "#B0E0E6",  # 粉蓝色
                "#48D1CC",  # 中绿宝石
                "#40E0D0"   # 绿宝石
            ],
            
            "galaxy": [  # 优化星系配色
                "#9400D3",  # 暗紫
                "#8A2BE2",  # 紫罗兰
                "#9932CC",  # 暗兰花
                "#E6E6FA",  # 薰衣草
                "#B39DDB",  # 柔和紫
                "#9575CD",  # 中紫
                "#7E57C2",  # 深紫
                "#673AB7",  # 靛紫
                "#5E35B1",  # 深靛紫
                "#4527A0"   # 极深紫
            ],
            
            "aurora": [  # 优化极光配色
                "#00FF7F",  # 春绿
                "#00FA9A",  # 中春绿
                "#40E0D0",  # 绿宝石
                "#48D1CC",  # 中绿宝石
                "#87CEEB",  # 天蓝
                "#B0C4DE",  # 淡钢蓝
                "#9370DB",  # 中紫
                "#DDA0DD",  # 梅红
                "#20B2AA",  # 浅海绿
                "#5F9EA0"   # 军蓝
            ],
            
            "fire_ice": [  # 优化冰火配色
                "#FF4500",  # 橙红
                "#FF6347",  # 番茄红
                "#FF7F50",  # 珊瑚色
                "#00BFFF",  # 深天蓝
                "#87CEEB",  # 天蓝
                "#B0E0E6",  # 粉蓝
                "#E0FFFF",  # 淡青
                "#F0FFFF",  # 天蓝白
                "#FF8C00",  # 深橙
                "#4682B4"   # 钢蓝
            ],
            
            "mystic": [  # 优化神秘配色
                "#9370DB",  # 中紫
                "#BA55D3",  # 兰花紫
                "#DA70D6",  # 兰花
                "#DDA0DD",  # 梅红
                "#EE82EE",  # 紫罗兰
                "#FF00FF",  # 洋红
                "#FF69B4",  # 热粉红
                "#FFB6C1",  # 浅粉红
                "#C71585",  # 中紫红
                "#DB7093"   # 古老玫瑰
            ],
            
            "enchanted_forest": [  # 优化魔��森林配色
                "#004B23",  # 深森林绿
                "#006400",  # 深绿
                "#228B22",  # 森林绿
                "#32CD32",  # 青柠绿
                "#90EE90",  # 淡绿
                "#98FB98",  # 淡绿薄荷
                "#E3F2C1",  # 嫩芽绿
                "#C1E1C1",  # 淡灰绿
                "#2E8B57",  # 海绿
                "#3CB371"   # 中海绿
            ],
            
            "candy": [  # 已优化的糖果配色
                "#FF1493",  # 深粉红
                "#FF69B4",  # 热粉红
                "#FFB6C1",  # 浅粉红
                "#FFC0CB",  # 粉红色
                "#FFE4E1",  # 迷雾玫瑰
                "#F8BBD0",  # 浅莓粉
                "#FF80AB",  # 糖果粉
                "#EC407A",  # 玫瑰粉
                "#E91E63",  # 莓红色
                "#F48FB1"   # 珊瑚粉
            ],
            
            "electric": [  # 优化电光配色
                "#00FF00",  # 亮绿
                "#7FFF00",  # 查特酸绿
                "#00FFFF",  # 青色
                "#FF00FF",  # 洋红
                "#FF1493",  # 深粉红
                "#FFFF00",  # 黄色
                "#FFA500",  # 橙色
                "#FF4500",  # 橙红色
                "#00FF7F",  # 春绿
                "#40E0D0"   # 绿宝石
            ],
            
            "ethereal_dream": [  # 优化梦幻紫罗兰配色
                "#B39DDB",  # 柔和紫
                "#9575CD",  # 中紫
                "#7E57C2",  # 深紫
                "#D1C4E9",  # 淡紫
                "#E1BEE7",  # 浅紫
                "#CE93D8",  # 梅红紫
                "#BA68C8",  # 中兰花紫
                "#AB47BC",  # 深兰花紫
                "#9C27B0",  # 紫色
                "#8E24AA"   # 深紫
            ],
            
            "fairy_dust": [  # 优化童话粉色配色
                "#FFD1DC",  # 浅粉
                "#FFC0CB",  # 粉红
                "#FFB6C1",  # 浅粉红
                "#FFE4E1",  # 迷雾玫瑰
                "#F8B195",  # 浅橙粉
                "#F67280",  # 珊瑚粉
                "#C06C84",  # 暗玫瑰
                "#6C5B7B",  # 暗紫
                "#FFB7B2",  # 浅珊瑚
                "#FF9AA2"   # 浅玫瑰
            ],
            
            "crystal_aurora": [  # 优化水晶极光配色
                "#00FFFF",  # 青色
                "#1E90FF",  # 道奇蓝
                "#4169E1",  # 皇家蓝
                "#87CEEB",  # 天空蓝
                "#B0E0E6",  # 粉蓝色
                "#E0FFFF",  # 淡青色
                "#F0F8FF",  # 爱丽丝蓝
                "#00CED1",  # 深青色
                "#48D1CC",  # 中绿宝石
                "#40E0D0"   # 绿宝石
            ],
            "neon_nights": [  # 霓虹之夜
                "#FF1E1E",  # 霓虹红
                "#FF3399",  # 霓虹粉
                "#FF00FF",  # 霓虹紫
                "#7B00FF",  # 深紫光
                "#00FFFF",  # 青光
                "#00FF00",  # 霓虹绿
                "#FFFF00",  # 霓虹黄
                "#FF8C00",  # 霓虹橙
                "#FF0066",  # 亮粉
                "#00CCFF"   # 电光蓝
            ],

            "jade_dream": [  # 翡翠梦境
                "#3CB371",  # 中碧绿
                "#20B2AA",  # 浅海绿
                "#48D1CC",  # 中绿宝石
                "#40E0D0",  # 绿宝石
                "#7FFFD4",  # 碧绿
                "#98FF98",  # 薄荷绿
                "#00FA9A",  # 春绿
                "#00FF7F",  # 春绿
                "#2E8B57",  # 海绿
                "#66CDAA"   # 中碧蓝
            ],

            "golden_sunset": [  # 金色黄昏
                "#FFD700",  # 金色
                "#FFA500",  # 橙色
                "#FF8C00",  # 深橙色
                "#FF7F50",  # 珊瑚色
                "#FF6347",  # 番茄红
                "#FF4500",  # 橙红色
                "#FFB6C1",  # 浅粉红
                "#FFA07A",  # 浅鲑鱼色
                "#FF8247",  # 暗橙
                "#FFD39B"   # 浅黄褐色
            ],
            "starry_night": [  # 星夜梦境
                "#1A237E",  # 深夜蓝
                "#3949AB",  # 星空蓝
                "#5C6BC0",  # 暮光蓝
                "#7986CB",  # 薄暮蓝
                "#9FA8DA",  # 雾蓝
                "#C5CAE9",  # 星尘蓝
                "#E8EAF6",  # 星光白
                "#B39DDB",  # 梦幻紫
                "#9575CD",  # 暗紫
                "#7E57C2",  # 深紫罗兰
                "#673AB7",  # 神秘紫
                "#5E35B1"   # 午夜紫
            ],

            "pearl_dream": [  # 珍珠梦境
                "#FFF5EE",  # 贝壳白
                "#FFE4E1",  # 珍珠粉
                "#E6E6FA",  # 薰衣草白
                "#F0F8FF",  # 爱丽丝蓝
                "#F0FFFF",  # 天青色
                "#E0FFFF",  # 浅青色
                "#F5FFFA",  # 薄荷白
                "#FFF0F5",  # 淡紫红
                "#FFDEAD",  # 淡金色
                "#FFE4B5",  # 淡褐色
                "#F0FFF0",  # 蜜瓜绿
                "#FFFAFA"   # 雪白
            ],

            "rainbow_mist": [  # 彩虹迷雾
                "#FF99CC",  # 浅粉红
                "#FFB366",  # 浅橙色
                "#FFFF99",  # 浅黄色
                "#99FF99",  # 浅绿色
                "#99FFFF",  # 浅青色
                "#99CCFF",  # 浅蓝色
                "#CC99FF",  # 浅紫色
                "#FF99FF",  # 浅洋红
                "#FFB7C5",  # 浅玫瑰
                "#87CEFA",  # 浅天蓝
                "#98FB98",  # 浅绿
                "#DDA0DD"   # 浅梅红
            ],

            "unicorn_dream": [  # 独角兽梦境
                "#FF80AB",  # 独角兽粉
                "#B388FF",  # 梦幻紫
                "#8C9EFF",  # 梦幻蓝
                "#82B1FF",  # 天空蓝
                "#80D8FF",  # 浅蓝
                "#84FFFF",  # 亮青
                "#A7FFEB",  # 薄荷绿
                "#B9F6CA",  # 嫩绿
                "#CCFF90",  # 柠檬绿
                "#F4FF81",  # 柠檬黄
                "#FFE57F",  # 金黄
                "#FFD740"   # 琥珀
            ],

            "northern_lights": [  # 北极光
                "#80CBC4",  # 极光青
                "#4DB6AC",  # 深极光青
                "#26A69A",  # 极光绿
                "#009688",  # 深极光绿
                "#00BCD4",  # 极光蓝
                "#00ACC1",  # 深极光蓝
                "#0097A7",  # 极光深蓝
                "#00838F",  # 极光墨蓝
                "#4DD0E1",  # 浅极光蓝
                "#B2EBF2",  # 极光白
                "#84FFFF",  # 亮极光
                "#18FFFF"   # 荧光极光
            ],

            "cotton_candy": [  # 棉花糖
                "#F8BBD0",  # 浅棉花糖粉
                "#F48FB1",  # 棉花糖粉
                "#F06292",  # 深棉花糖粉
                "#EC407A",  # 玫瑰棉花糖
                "#E91E63",  # 深玫瑰棉花糖
                "#D81B60",  # 紫红棉花糖
                "#C2185B",  # 深紫红棉花糖
                "#AD1457",  # 暗紫红棉花糖
                "#880E4F",  # 深暗紫红棉花糖
                "#FF80AB",  # 亮棉花糖粉
                "#FF4081",  # 亮玫瑰棉花糖
                "#F50057"   # 亮紫红棉花糖
            ],

            "pastel_dream": [  # 柔和梦境
                "#FFE4E1",  # 迷雾玫瑰
                "#F8BBD0",  # 浅莓粉
                "#E1BEE7",  # 浅紫色
                "#D1C4E9",  # 薰衣草灰
                "#C5CAE9",  # 浅靛蓝
                "#BBDEFB",  # 浅蓝
                "#B3E5FC",  # 浅青
                "#B2EBF2",  # 浅青绿
                "#B2DFDB",  # 浅绿松石
                "#C8E6C9",  # 浅绿
                "#DCEDC8",  # 浅黄绿
                "#F0F4C3"   # 浅柠檬
            ]
        }
        
        # 调整两条蛇的初始位置（y坐标改为居中）
        self.snake1_pos = [(120, 45), (138, 45), (156, 45), (174, 45)]
        self.snake1_direction = "Right"
        self.snake1_colors = [
            "#FF69B4",  # 粉红
            "#FF1493",  # 深粉红
            "#DA70D6",  # 兰花紫
            "#9370DB",  # 中紫色
            "#8A2BE2",  # 紫罗兰
            "#4B0082"   # 靛青
        ]
        
        self.snake2_pos = [(280, 45), (262, 45), (244, 45), (226, 45)]
        self.snake2_direction = "Left"
        self.snake2_colors = [
            "#4B0082",  # 靛青
            "#6A5ACD",  # 石板蓝
            "#483D8B",  # 暗石板蓝
            "#7B68EE",  # 中紫罗兰
            "#9400D3",  # 暗紫罗兰
            "#8B008B"   # 暗洋红
        ]
        
        # 添加方向权重
        self.directions_weight = {
            "Left": 35,
            "Right": 35,
            "Up": 10,
            "Down": 10
        }
        
        # 定义两套色方案
        self.color_schemes = {
            "scheme1": {
                "snake1": [
                    "#FF50B8", "#FF2FA1", "#FF0F87", 
                    "#FF0099", "#FF00AA"
                ],  # 粉紫色系（融合了多个最佳效果）
                "snake2": [
                    "#4B0082", "#6A5ACD", "#483D8B", 
                    "#7B68EE", "#9400D3", "#8B008B"
                ]   # 靛蓝紫罗兰渐变色
            },
            "scheme2": {
                "snake1": [
                    "#00FFFF", "#00F0F5", "#00E5EE", 
                    "#00CCE6", "#00A8E8"
                ],  # 青色系（结合了通透感和深邃感）
                "snake2": [
                    "#FF69B4", "#FF1493", "#C71585", 
                    "#DB7093", "#BA55D3", "#9400D3"
                ]   # 粉紫色系
            },
            
            "spring_sakura": {  # 春日樱花
            "snake1": [
                "#FFF0F5",  # 淡雅粉红
                "#FFE4E1",  # 晨曦玫瑰
                "#FFB6C1",  # 浅樱粉
                "#FF69B4",  # 绚丽粉
                "#DB7093"   # 暮光紫红
            ],
            "snake2": [
                "#F5FFFA",  # 薄荷白
                "#E0FFFF",  # 清水青
                "#B0E0E6",  # 粉蓝
                "#87CEEB",  # 天空蓝
                "#4682B4"   # 钢青蓝
            ]
            },
            "summer_ocean": {  # 夏日海洋
                "snake1": [
                    "#F0FFFF",  # 天青色
                    "#E0FFFF",  # 清水青
                    "#AFEEEE",  # 淡绿松石
                    "#7FFFD4",  # 碧绿
                    "#40E0D0"   # 绿松石
                ],
                "snake2": [
                    "#F0F8FF",  # 爱丽丝蓝
                    "#87CEEB",  # 天蓝
                    "#4169E1",  # 皇家蓝
                    "#1E90FF",  # 道奇蓝
                    "#00BFFF"   # 深天蓝
                ]
            },
            "autumn_maple": {  # 秋日枫叶
                "snake1": [
                    "#FFE4B5",  # 淡褐色
                    "#FFA07A",  # 浅鲑鱼色
                    "#FF7F50",  # 珊瑚色
                    "#FF6347",  # 番茄红
                    "#FF4500"   # 橙红色
                ],
                "snake2": [
                    "#FFF8DC",  # 玉米丝色
                    "#FFD700",  # 金色
                    "#FFA500",  # 橙色
                    "#FF8C00",  # 暗橙色
                    "#FF7F50"   # 珊瑚色
                ]
            },
            "winter_snow": {  # 冬日飘雪
                "snake1": [
                    "#F0FFFF",  # 天青色
                    "#E0FFFF",  # 淡青色
                    "#B0E0E6",  # 粉蓝色
                    "#87CEEB",  # 天蓝色
                    "#4682B4"   # 钢蓝色
                ],
                "snake2": [
                    "#F5FFFA",  # 薄荷奶油
                    "#F0FFF0",  # 蜜瓜绿
                    "#E0FFF0",  # 淡绿色
                    "#98FB98",  # 淡绿色
                    "#90EE90"   # 淡绿色
                ]
            },
            "moonlight_dream": {  # 月光梦境
                "snake1": [
                    "#E6E6FA",  # 薰衣草色
                    "#DDA0DD",  # 梅红色
                    "#DA70D6",  # 兰花紫
                    "#BA55D3",  # 中兰花紫
                    "#9370DB"   # 中紫色
                ],
                "snake2": [
                    "#F0F8FF",  # 爱丽丝蓝
                    "#E6E6FA",  # 薰衣草色
                    "#B0C4DE",  # 淡钢蓝
                    "#6495ED",  # 矢车菊蓝
                    "#4169E1"   # 皇家蓝
                ]
            },
            "rose_dream": {  # 玫瑰梦境
                "snake1": [
                    "#FF80AB",  # 明亮粉
                    "#FF4081",  # 活力粉
                    "#FF69B4",  # 亮粉红
                    "#FFB6C1",  # 浅粉红
                    "#FF99CC",  # 糖果粉
                    "#FF66B2"   # 甜心粉
                ],
                "snake2": [
                    "#B0E0E6",  # 粉蓝色
                    "#87CEEB",  # 天空蓝
                    "#87CEFA",  # 淡天蓝
                    "#99CCFF",  # 晴空蓝
                    "#B4E4FF",  # 清澈蓝
                    "#A6E3FF"   # 浅湖蓝
                ]
            },
            
            "spring_blossom": {  # 春日花语
                "snake1": [
                    "#FFB7C5",  # 春樱粉
                    "#FF99CC",  # 花瓣粉
                    "#FF80AB",  # 桃花粉
                    "#FF69B4",  # 杜鹃粉
                    "#FF99FF",  # 紫罗兰粉
                    "#FF85AD"   # 芍药粉
                ],
                "snake2": [
                    "#98FB98",  # 嫩绿
                    "#90EE90",  # 淡绿
                    "#A7FFEB",  # 薄荷绿
                    "#B9F6CA",  # 清新绿
                    "#CCFF90",  # 柠檬绿
                    "#8EE5EE"   # 青绿
                ]
            },
            
            "summer_ocean": {  # 夏日海洋
                "snake1": [
                    "#40E0D0",  # 绿松石
                    "#48D1CC",  # 中绿宝石
                    "#00CED1",  # 深青色
                    "#7FFFD4",  # 碧绿色
                    "#66CDAA",  # 中绿松石
                    "#4EDFCC"   # 海蓝绿
                ],
                "snake2": [
                    "#87CEEB",  # 天蓝
                    "#00BFFF",  # 深天蓝
                    "#1E90FF",  # 道奇蓝
                    "#66B2FF",  # 明亮蓝
                    "#99CCFF",  # 淡蓝
                    "#80B3FF"   # 海洋蓝
                ]
            },
            
            "candy_dream": {  # 糖果梦境
                "snake1": [
                    "#FF99CC",  # 糖果粉
                    "#FF80AB",  # 明亮粉
                    "#FF69B4",  # 亮粉红
                    "#FFB6C1",  # 浅粉红
                    "#FF85AD",  # 甜心粉
                    "#FF99FF"   # 梦幻粉
                ],
                "snake2": [
                    "#99CCFF",  # 晴空蓝
                    "#80B3FF",  # 海洋蓝
                    "#66B2FF",  # 明亮蓝
                    "#B4E4FF",  # 清澈蓝
                    "#A6E3FF",  # 浅湖蓝
                    "#87CEEB"   # 天空蓝
                ]
            },
            "rainbow_mist": {  # 彩虹迷雾
                "snake1": [
                    "#FF80AB",  # 独角兽粉
                    "#FFB366",  # 浅橙色
                    "#FFFF99",  # 浅黄色
                    "#99FF99",  # 浅绿色
                    "#99FFFF",  # 浅青色
                    "#99CCFF",  # 浅蓝色
                    "#CC99FF",  # 浅紫色
                    "#FF99FF",  # 浅洋红
                    "#FFB7C5",  # 浅玫瑰
                    "#87CEFA",  # 浅天蓝
                    "#98FB98",  # 浅绿
                    "#DDA0DD"   # 浅梅红
                ],
                "snake2": [
                    "#FF1493",  # 亮粉红
                    "#FF8C00",  # 亮橙色
                    "#FFD700",  # 金黄色
                    "#7FFF00",  # 查特酸绿
                    "#00FFFF",  # 青色
                    "#1E90FF",  # 道奇蓝
                    "#9370DB",  # 中紫色
                    "#FF69B4",  # 热粉红
                    "#FFA07A",  # 浅鲑鱼色
                    "#00CED1",  # 深青色
                    "#90EE90",  # 淡绿色
                    "#DA70D6"   # 兰花紫
                ]
            }
        }
        
        # 随机选择一个配色方案
        selected_scheme = random.choice(list(self.color_schemes.keys()))
        self.snake1_colors = self.color_schemes[selected_scheme]["snake1"]
        self.snake2_colors = self.color_schemes[selected_scheme]["snake2"]
        
        # 添加涟漪效果的属性
        self.ripple_radius = 0
        self.is_rippling = False
        
        self.draw_decorative_snakes()
        self.animate_snakes()
        
        # 在画布上绘制说明文本
        self.draw_instructions()
        
        # 创建框架纳两个按钮
        button_frame = tk.Frame(main_frame, bg='#050505')
        button_frame.pack(pady=(20,20))
        
        # 根据当前音乐模式设置按钮文本
        current_mode = self.music_mode.get()
        button_text = {
            "always": "🎵 Music: Always",
            "conditional": "🎵 Music: Conditional",
            "off": "🎵 Music: OFF"
        }[current_mode]
        # 音乐按钮样式
        self.music_button = tk.Button(
            button_frame,
            text=button_text,  # 使用当前模式对应的文本
            command=self.toggle_music,
            width=24,
            height=1,
            bg="#2196F3",
            fg="white",
            font=("Verdana", 14, "bold"),
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        self.music_button.pack(pady=10)
        
        # 开始按钮
        self.start_button = tk.Button(
            button_frame,
            text="Start Game",
            command=self.start_game,
            width=24,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Verdana", 14, "bold"),
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        self.start_button.pack(pady=10)
        
        # ... existing code ...

        # 创建一个新的框架用于底部按钮
        button_row_frame = tk.Frame(button_frame, bg='#050505')
        button_row_frame.pack(fill='x', pady=10)
        self.mode = Game_Mode
        # 左边的按钮 - 与Start Game左对齐
        self.left_button = tk.Button(
            button_row_frame,
            text=self.mode,
            command=self.toggle_mode,
            width=12,
            height=1,
            bg="#FFA726" if self.mode == "Forbid" else "#9B59B6",  # 根据模式设置颜色,
            fg="white",
            font=("Verdana", 14, "bold"),
            relief="flat",
            borderwidth=0,
            activebackground="#FFC266" if self.mode == "Forbid" else "#B39DDB",  # 根据模式设置悬停颜色  # 鼠标悬停时的颜色
            cursor="hand2"
        )
        self.left_button.pack(side=tk.LEFT, padx=(0, 0))  # 移除所有padding

        # 退出按钮 - 与Start Game右对齐
        self.quit_button = tk.Button(
            button_row_frame,
            text="Quit",
            command=self.window.destroy,
            width=11,
            height=1,
            bg="#FF5722",
            fg="white",
            font=("Verdana", 14, "bold"),
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        self.quit_button.pack(side=tk.RIGHT, padx=(0, 0))  # 使用RIGHT对齐，移除所有padding
        self.window.bind("<Escape>", lambda event: self.window.destroy())

        # 为按钮添加悬停效果
        for button in [self.music_button, self.start_button, self.quit_button,self.left_button]:
            button.bind("<Enter>", lambda e, b=button: self.on_hover(e, b))
            button.bind("<Leave>", lambda e, b=button: self.on_leave(e, b))
        
        # 在初始化函中添加音效加载
        self.firework_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets", "music", "firework.wav"))
        self.firework_sound.set_volume(0.3)  # 设置音量为 30%
        self.window.bind("<Control_L>", lambda event: self.toggle_music())  # 左Ctrl键
        self.window.bind("<Control_R>", lambda event: self.toggle_music())  # 右Ctrl键
        #self.window.bind("<Tab>", lambda event: self.toggle_music())  # Tab键
        self.window.bind("<Return>", lambda event: self.start_game())   

        # 在初始化方法中添加以下代码
        # 窗口移动步长
        self.move_step = 20
        
        # 绑定箭头键事件
        self.window.bind("<Left>", lambda e: self.move_window("Left"))
        self.window.bind("<Right>", lambda e: self.move_window("Right"))
        self.window.bind("<Up>", lambda e: self.move_window("Up"))
        self.window.bind("<Down>", lambda e: self.move_window("Down"))
        self.window.bind("<Control-Left>", lambda e: self.move_window("Left"))
        self.window.bind("<Control-Right>", lambda e: self.move_window("Right"))
        self.window.bind("<Control-Up>", lambda e: self.move_window("Up"))
        self.window.bind("<Control-Down>", lambda e: self.move_window("Down"))

        # 添加Shift键加速功能
        self.window.bind("<Shift-Left>", lambda e: self.move_window("Left", True))
        self.window.bind("<Shift-Right>", lambda e: self.move_window("Right", True))
        self.window.bind("<Shift-Up>", lambda e: self.move_window("Up", True))
        self.window.bind("<Shift-Down>", lambda e: self.move_window("Down", True))
        
        # 添加Control键加速功能
        self.window.bind("<a>", lambda e: self.move_window("Left"))
        self.window.bind("<d>", lambda e: self.move_window("Right")) 
        self.window.bind("<w>", lambda e: self.move_window("Up"))
        self.window.bind("<s>", lambda e: self.move_window("Down"))
        self.window.bind("<A>", lambda e: self.move_window("Left"))
        self.window.bind("<D>", lambda e: self.move_window("Right")) 
        self.window.bind("<W>", lambda e: self.move_window("Up"))
        self.window.bind("<S>", lambda e: self.move_window("Down"))
        self.window.bind("<Control-a>", lambda e: self.move_window("Left"))
        self.window.bind("<Control-d>", lambda e: self.move_window("Right")) 
        self.window.bind("<Control-w>", lambda e: self.move_window("Up"))
        self.window.bind("<Control-s>", lambda e: self.move_window("Down"))
        self.window.bind("<Shift-a>", lambda e: self.move_window("Left"))
        self.window.bind("<Shift-d>", lambda e: self.move_window("Right")) 
        self.window.bind("<Shift-w>", lambda e: self.move_window("Up"))
        self.window.bind("<Shift-s>", lambda e: self.move_window("Down"))
        self.window.bind("<Control-A>", lambda e: self.move_window("Left"))
        self.window.bind("<Control-D>", lambda e: self.move_window("Right")) 
        self.window.bind("<Control-W>", lambda e: self.move_window("Up"))
        self.window.bind("<Control-S>", lambda e: self.move_window("Down"))
        self.window.bind("<Shift-A>", lambda e: self.move_window("Left"))
        self.window.bind("<Shift-D>", lambda e: self.move_window("Right")) 
        self.window.bind("<Shift-W>", lambda e: self.move_window("Up"))
        self.window.bind("<Shift-S>", lambda e: self.move_window("Down"))
        
        # 添加窗口关闭处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            # 停止所有音乐和音效
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            # 销毁窗口
            self.window.destroy()
            
            # 确保程序完全退出
            sys.exit()
            
        except Exception as e:
            print(f"关闭程序时出错: {e}")
            sys.exit(1)
    
    def get_transition_color(self):
        """计算渐变颜色"""
        current_color = self.neon_colors[self.color_index]
        next_color = self.neon_colors[(self.color_index + 1) % len(self.neon_colors)]
        
        # 将颜色转换为RGB值
        r1, g1, b1 = int(current_color[1:3], 16), int(current_color[3:5], 16), int(current_color[5:7], 16)
        r2, g2, b2 = int(next_color[1:3], 16), int(next_color[3:5], 16), int(next_color[5:7], 16)
        
        # 计算渐变
        r = int(r1 + (r2 - r1) * self.color_transition)
        g = int(g1 + (g2 - g1) * self.color_transition)
        b = int(b1 + (b2 - b1) * self.color_transition)
        
        # 返回十六进制颜色代码
        return f'#{r:02x}{g:02x}{b:02x}'

    def start_neon_effect(self):
        """启动霓虹灯效果"""
        # 清除旧的线条
        self.left_canvas.delete("all")
        self.bottom_canvas.delete("all") 
        self.right_canvas.delete("all")
        
        # 更新颜色过渡
        self.color_transition += 0.02
        if self.color_transition >= 1.0:
            self.color_transition = 0.0
            self.color_index = (self.color_index + 1) % len(self.neon_colors)
        
        # 获取当前渐变颜色
        t = time.time()
        
        # 外边框颜色
        r1 = int(128 + 127 * math.sin(t * 2.0))
        g1 = int(128 + 127 * math.sin(t * 2.0 + 2.0))
        outer_color = self.get_transition_color()
        
        # 内边框颜色
        r2 = int(128 + 127 * math.sin(t * 2.0 + 3.0))
        inner_color = self.get_transition_color()
        
        # 设置画布尺寸和背景色
        border_width = 3  # 减小边框宽度
        
        # 调整画布位置和尺寸
        self.left_canvas.configure(width=border_width)
        self.left_canvas.place(x=0, y=0, height=780)
        
        self.bottom_canvas.configure(height=border_width)
        self.bottom_canvas.place(x=0, y=777, width=410)  # 调整y位置到底部
        
        self.right_canvas.configure(width=border_width)
        self.right_canvas.place(x=407, y=0, height=780)  # 调整x位置到右侧
        
        # 填充整个画布区域
        # 左边框
        self.left_canvas.create_rectangle(
            0, 0, border_width, 780,
            fill=outer_color,
            outline="",
            width=0
        )
        
        # 底边框
        self.bottom_canvas.create_rectangle(
            0, 0, 410, border_width,
            fill=outer_color,
            outline="",
            width=0
        )
        
        # 右边框
        self.right_canvas.create_rectangle(
            0, 0, border_width, 780,
            fill=outer_color,
            outline="",
            width=0
        )
        
        # 添加发光效果
        for canvas, coords in [
            (self.left_canvas, (0, 0, border_width, 780)),
            (self.bottom_canvas, (0, 0, 410, border_width)),
            (self.right_canvas, (0, 0, border_width, 780))
        ]:
            # 添加内发光
            canvas.create_rectangle(
                *coords,
                fill=inner_color,
                outline="",
                stipple='gray50'
            )
            
            # 添加外发光
            canvas.create_rectangle(
                *coords,
                fill=outer_color,
                outline="",
                stipple='gray25'
            )
        
        # 每25毫秒更新一次
        self.window.after(25, self.start_neon_effect)
    
    def draw_instructions(self):
        # 加载最高分
        global high_score
        high_score = load_high_score()
        
        # 创建渐变颜色（使用更鲜艳的配色）
        def generate_gradient_colors(steps):
            colors = [
                "#FF6B6B",  # 珊瑚红
                "#4ECDC4",  # 青绿色
                "#45B7D1",  # 天蓝色
                "#96CEB4",  # 薄荷绿
                "#FFEEAD",  # 淡黄色
                "#FF9999"   # 红色
            ]
            
            gradient = []
            for i in range(steps):
                index = (i / steps) * (len(colors) - 1)
                color1 = colors[int(index)]
                color2 = colors[min(int(index) + 1, len(colors) - 1)]
                
                t = index - int(index)
                r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
                r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
                
                r = int(r1 * (1-t) + r2 * t)
                g = int(g1 * (1-t) + g2 * t)
                b = int(b1 * (1-t) + b2 * t)
                
                gradient.append(f'#{r:02x}{g:02x}{b:02x}')
            return gradient
        
        # 生成20个渐变色
        gradient_colors = generate_gradient_colors(20)
        
        # 绘制"BEST SCORE:"文本（注意这里添加了冒号）
        text = "BEST SCORE:"  # 添冒号
        high_score = load_high_score()
        score_text = str(high_score)
        char_width = 14
        start_x = 200 - ((len(text) * char_width + 40) / 2)  # 调整整体位置，为分数留出空间
        
        # 绘制文字阴影效果
        for i, char in enumerate(text):
            # 阴影
            self.canvas.create_text(
                start_x + i * char_width + 2,
                150 + 2,
                text=char,
                fill='#222222',
                font=("Impact", 20, "bold"),
                anchor="center",
                tags="instructions"
            )
            # 主文字
            color = gradient_colors[int((i / len(text)) * len(gradient_colors))]
            self.canvas.create_text(
                start_x + i * char_width,
                150,
                text=char,
                fill=color,
                font=("Impact", 20, "bold"),
                anchor="center",
                tags="instructions"
            )
        
        # 绘制分数稍微调整了位置）
        score_x = start_x + (len(text)) * char_width - 5  # 微调分数位置
        # 分数阴影
        self.canvas.create_text(
            score_x + 2,
            150 + 2,
            text=score_text,
            fill='#222222',
            font=("Impact", 24, "bold"),
            anchor="w",
            tags="instructions"
        )
        # 分数主体
        self.canvas.create_text(
            score_x,
            150,
            text=score_text,
            fill='#FFD700',  # 金色
            font=("Impact", 24, "bold"),
            anchor="w",
            tags="instructions"
        )
        
        # 游戏说明文本
        instructions = """
        🎮 Instructions: Shift+H
        
        🎯 Controls:
        • Arrow or WASD or Mouse to move snake
        • P/SPACE to pause/continue
        • R to restart
        
        🍎 Food Types:
        • Normal Food (Red Square)   : +1 point
        • Golden Food (Gold Circle)  : +3 points, Speed Up
        • Special Food (Purple Star) : +5 points, Slow Down
        """
        
        y = 180
        for line in instructions.split('\n'):
            if not line.strip():
                y += 15
                continue
            
            # 只修改三个特定标题的字体
            if "Instructions:" in line or "Controls:" in line or "Food Types:" in line:
                self.canvas.create_text(
                    0, y,  # 保持原来的x坐标
                    text=line,
                    fill="#FFD900",
                    font=("Impact", 14),  # 只改这三个标题的字体
                    anchor="w",
                    tags="instructions"
                )
            else:
            # 其他所有内容保持原样
                self.canvas.create_text(
                0, y,  # 保持原来的x坐标
                text=line,
                fill="#FFD900",
                font=("Helvetica", 12),  # 保持原有字体
                anchor="w",
                tags="instructions" 
            )
            y += 20
    
    def draw_decorative_snakes(self):
        self.canvas.delete("snake", "ripple")
        
        # 检查两条蛇头部是否接近
        snake1_head = self.snake1_pos[-1]
        snake2_head = self.snake2_pos[-1]
        distance = math.sqrt(
            (snake1_head[0] - snake2_head[0])**2 + 
            (snake1_head[1] - snake2_head[1])**2
        )
        
        # 当蛇头接近时创建涟漪效果
        if distance < 30:
            if not self.is_rippling:
                self.is_rippling = True
                self.ripple_radius = 5
            
            center_x = (snake1_head[0] + snake2_head[0]) / 2
            center_y = (snake1_head[1] + snake2_head[1]) / 2
            
            # 使用正弦函数创建平滑的扩散效果
            progress = self.ripple_radius / 40
            fade = math.sin((1 - progress) * math.pi / 2)
            
            # 绘制涟漪
            self.canvas.create_oval(
                center_x - self.ripple_radius,
                center_y - self.ripple_radius,
                center_x + self.ripple_radius,
                center_y + self.ripple_radius,
                outline="#FF69B4",  # 原来的粉色
                width=1.7,  # 稍微调整线条宽度
                tags="ripple",
                stipple='gray75' if fade > 0.5 else 'gray50'  # 平滑的透明度过渡
            )
            
            # 更平滑的扩散速度
            self.ripple_radius += 1.8
            
            # 重置涟漪
            if self.ripple_radius > 40:
                self.is_rippling = False
                self.ripple_radius = 5
        else:
            self.is_rippling = False
        
        # 绘制蛇
        for i, pos in enumerate(self.snake1_pos):
            self.canvas.create_rectangle(
                pos[0], pos[1],
                pos[0] + 16, pos[1] + 16,
                fill=self.snake1_colors[i % len(self.snake1_colors)],
                outline="",
                tags="snake"
            )
        
        for i, pos in enumerate(self.snake2_pos):
            self.canvas.create_rectangle(
                pos[0], pos[1],
                pos[0] + 16, pos[1] + 16,
                fill=self.snake2_colors[i % len(self.snake2_colors)],
                outline="",
                tags="snake"
            )
    
    def update_snake_direction(self, head_pos, current_direction):
        head_x, head_y = head_pos
        
        # 扩大活动范围，让蛇的运动更自由
        if (head_x >= 380 or head_x <= 20 or  # 扩大水平活动范围
            head_y >= 100 or head_y <= 20):    # 扩大垂直活动范围
            possible_directions = []
            weights = []
            
            if head_x < 380:
                possible_directions.append("Right")
                weights.append(self.directions_weight["Right"])
            if head_x > 20:
                possible_directions.append("Left")
                weights.append(self.directions_weight["Left"])
            if head_y < 100:  # 调上边界
                possible_directions.append("Down")
                weights.append(self.directions_weight["Down"])
            if head_y > 20:  # 调整下边界
                possible_directions.append("Up")
                weights.append(self.directions_weight["Up"])
            
            if possible_directions:
                return random.choices(
                    possible_directions,
                    weights=weights,
                    k=1
                )[0]
        elif random.random() < 0.015:  # 降低随机转向概
            directions = list(self.directions_weight.keys())
            weights = list(self.directions_weight.values())
            return random.choices(
                directions,
                weights=weights,
                k=1
            )[0]
        
        return current_direction
    
    def animate_snakes(self):
        if not hasattr(self, 'window'):
            return
        
        # 更新两条蛇的方向和位置
        self.snake1_direction = self.update_snake_direction(
            self.snake1_pos[-1],
            self.snake1_direction
        )
        self.snake1_pos = self.move_snake(
            self.snake1_pos,
            self.snake1_direction
        )
        
        self.snake2_direction = self.update_snake_direction(
            self.snake2_pos[-1],
            self.snake2_direction
        )
        self.snake2_pos = self.move_snake(
            self.snake2_pos,
            self.snake2_direction
        )
        
        self.draw_decorative_snakes()
        self.window.after(20, self.animate_snakes)
    
    def move_snake(self, positions, direction):
        head_x, head_y = positions[-1]
        
        # 计算新的蛇头位置
        if direction == "Right":
            new_head = (head_x + 3, head_y)
        elif direction == "Left":
            new_head = (head_x - 3, head_y)
        elif direction == "Up":
            new_head = (head_x, head_y - 3)
        else:  # Down
            new_head = (head_x, head_y + 3)
        
        positions.append(new_head)
        positions.pop(0)
        return positions
    
    def create_firework(self, event):
        # 播放烟花音效
        self.firework_sound.play()
        
        # 随机选择一个颜色主题
        palette = random.choice(list(self.firework_palettes.values()))
        
        # 创建主要爆炸
        num_particles = random.randint(65, 85)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3.0, 7.0)
            size = random.uniform(2, 5)
            
            # 添加随机扰动
            speed_variation = random.uniform(0.9, 1.1)
            angle_variation = random.uniform(-0.1, 0.1)
            
            # 创建渐变色
            base_color = random.choice(palette)
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            
            # 添加随机色彩变化
            r = min(255, max(0, r + random.randint(-20, 20)))
            g = min(255, max(0, g + random.randint(-20, 20)))
            b = min(255, max(0, b + random.randint(-20, 20)))
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            particle = {
                "x": event.x,
                "y": event.y,
                "speed_x": math.cos(angle + angle_variation) * speed * speed_variation,
                "speed_y": math.sin(angle + angle_variation) * speed * speed_variation,
                "color": color,
                "base_color": base_color,
                "size": size,
                "alpha": 1.0,
                "decay_rate": random.uniform(0.01, 0.03),
                "sparkle_timer": random.randint(0, 10)
            }
            self.particles.append(particle)
            self.particle_trails.append([])  # 初始化每个粒子的轨迹为空列表
            
        # 添加次要爆炸效果
        for _ in range(random.randint(2, 4)):
            self.create_secondary_explosion(event.x, event.y, palette)
            
        self.animate_firework()
    
    def create_secondary_explosion(self, x, y, color_scheme):
        # 创建较小的次要爆炸
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)
        delay = random.randint(10, 20)
        
        def delayed_explosion():
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2.0, 4.0)
                particle = {
                    "x": x + offset_x,
                    "y": y + offset_y,
                    "speed_x": math.cos(angle) * speed,
                    "speed_y": math.sin(angle) * speed,
                    "color": random.choice(color_scheme),
                    "size": random.uniform(1, 3),
                    "alpha": 1.0,
                    "trail": [],
                    "decay_rate": random.uniform(0.02, 0.04),
                    "sparkle_timer": random.randint(0, 10)
                }
                self.particles.append(particle)
                
        self.window.after(delay * 50, delayed_explosion)
        
    def animate_firework(self):
        self.canvas.delete("particle")
        
        # 使用 enumerate 和切片时要小心，因为我们会修改列表
        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            
            # 更新位置
            particle["x"] += particle["speed_x"]
            particle["y"] += particle["speed_y"]
            particle["alpha"] -= particle["decay_rate"]
            
            if particle["alpha"] <= 0:
                self.particles.pop(i)
                if i < len(self.particle_trails):
                    self.particle_trails.pop(i)
                continue
            
            # 确保 particle_trails 有足够的空间
            while len(self.particle_trails) <= i:
                self.particle_trails.append([])
                
            # 更新轨迹
            self.particle_trails[i].append((particle["x"], particle["y"]))
            if len(self.particle_trails[i]) > 10:  # 限制轨迹长度
                self.particle_trails[i].pop(0)
            
            # 绘制粒子
            size = particle["size"] * particle["alpha"]
            
            self.canvas.create_oval(
                particle["x"] - size,
                particle["y"] - size,
                particle["x"] + size,
                particle["y"] + size,
                fill=particle["color"],
                outline="",
                tags="particle"
            )
            
            # 添加发光效果
            if particle["alpha"] > 0.5:
                glow_size = size * 1.5
                self.canvas.create_oval(
                    particle["x"] - glow_size,
                    particle["y"] - glow_size,
                    particle["x"] + glow_size,
                    particle["y"] + glow_size,
                    fill="",
                    outline=particle["color"],
                    width=0.5,
                    tags="particle",
                    stipple='gray25'
                )
                
            i += 1
        
        if self.particles:
            self.canvas.after(16, self.animate_firework)
    
    def toggle_music(self):
        """切换音乐状态"""
        current_mode = self.music_mode.get()
        
        # 定义每种模式对应的按钮样式
        button_styles = {
            "always": {
                "text": "🎵 Music: Always",
                "bg": "#1976D2"  # 深蓝色
            },
            "conditional": {
                "text": "🎵 Music: Conditional",
                "bg": "#4FC3F7"  # 天蓝色
            },
            "off": {
                "text": "🎵 Music: OFF",
                "bg": "#9E9E9E"  # 灰色
            }
        }
        
        # 切换模式
        if current_mode == "always":
            new_mode = "conditional"
        elif current_mode == "conditional":
            new_mode = "off"
        else:  # off
            new_mode = "always"
        
        # 更新模和按钮样式
        self.music_mode.set(new_mode)
        self.music_button.config(
            text=button_styles[new_mode]["text"],
            bg=button_styles[new_mode]["bg"]
        )
    def toggle_mode(self):
        """切换 Pass/Forbid 模式"""
        global high_score
        high_score = load_high_score()
        global Game_Mode  # 声明使用全局变量
        if self.mode == "Forbid":
            Game_Mode = "Pass"
            self.mode = "Pass"
            self.left_button.config(
                text="Pass",
                bg="#9B59B6",  # 优雅的紫色
                activebackground="#B39DDB",  # 鼠标悬停时的颜色
            )
        else:
            self.mode = "Forbid"
            Game_Mode = "Forbid"
            self.left_button.config(
                text="Forbid",
                bg="#FFA726",  # 原来的橙色
                activebackground="#FFC266",  # 鼠标悬停时的颜色
            )
        high_score = load_high_score()
        
        # 清除旧的分数显示
        self.canvas.delete("instructions")
        self.draw_instructions()
    
    def start_game(self):
        """开始游戏，带平滑圆润的波纹扩散特效"""
        charge_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets", "music", "charge.wav"))
        charge_sound.set_volume(0.5)  # 设置音量为50%
        charge_sound.play()
        # 获取窗口中心点
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()
        center_x = window_width*1.0 / 2.0
        center_y = window_height*1.0 / 2.0
        
        # 计算最大半径
        max_radius = int(((center_x)**2 + (center_y)**2)**0.5)
        def create_opening_firework():
            particles = []
            colors = [
                # 核心色系：深邃梦幻青
                "#00ffff",  # 纯青
                "#26ffff",  # 浅青
                "#4dffff",  # 天青
                "#73ffff",  # 晴空青
                
                # 高光层：极光珠光
                "#91ffff",  # 珠光青
                "#aaffff",  # 浅珠光
                "#c2ffff",  # 中珠光
                "#d9ffff",  # 淡珠光
                
                # 梦幻层：海洋之心
                "#00e6e6",  # 深海青
                "#00f2f2",  # 海洋青
                "#1affff",  # 浅海青
                "#66ffff",  # 碧波青
                
                # 点缀层：星光闪烁
                "#80ffff",  # 星光青
                "#99ffff",  # 晨曦青
                "#b3ffff",  # 微光青
                "#ccffff",  # 晶莹青
                
                # 幻彩层：极光幻境
                "#e6ffff",  # 极光白
                "#f0ffff",  # 天境白
                "#f5ffff",  # 梦境白
                "#faffff",  # 纯净白
            ]
            def get_color_with_variation(angle):
                # 基础偏转因子
                base_deviation = random.uniform(-0.15, 0.15)  # ±15% 的基础偏移
                
                # 动态偏转 - 使用多重正弦叠加产生更复杂的光效
                dynamic_deviation = (math.sin(angle * 3) * 0.08 + 
                                  math.sin(angle * 5) * 0.05 +
                                  math.sin(angle * 7) * 0.03)
                
                # 随机扰动
                noise = random.gauss(0, 0.06)
                
                # 合并所有偏转效果
                total_deviation = base_deviation + dynamic_deviation + noise
                
                # 确保总偏转在合理范围内
                total_deviation = max(-0.3, min(0.3, total_deviation))
                
                # 计算最终的角度索引
                adjusted_angle = angle + (2 * math.pi * total_deviation)
                color_index = int(((adjusted_angle % (2 * math.pi)) / (2 * math.pi)) * len(colors))
                
                # 确保索引在有效范围内
                color_index = color_index % len(colors)
                
                # 随机添加光晕效果
                if random.random() < 0.2:  # 20%概率产生光晕
                    return "#FFFFFF"  # 纯白色光晕
                    
                base_color = colors[color_index]
                # 15%概率增加彩虹光晕
                if random.random() < 0.15:
                    rainbow_colors = ["#FFD700", "#FF69B4", "#00FFFF", "#FF1493"]
                    return random.choice(rainbow_colors)
                    
                return base_color
                
            # 在粒子创建时添加特殊效果
            for i in range(60):  # 保持原有粒子数量
                angle = random.uniform(0, 2 * math.pi)
                color = get_color_with_variation(angle)
                
                # 保持原有速度范围
                base_speed = random.uniform(2, 5)
                if i < 20:  # 内圈
                    speed = base_speed * 0.8
                    size = random.uniform(3, 5)
                elif i < 40:  # 中圈
                    speed = base_speed
                    size = random.uniform(2, 4)
                else:  # 外圈
                    speed = base_speed * 1.2
                    size = random.uniform(1, 3)
                
                particle = {
                    'x': center_x,
                    'y': center_y,
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'color': color,
                    'alpha': 1.0,
                    'size': size,
                    'trail': [],
                    'sparkle': random.random() < 0.6,  # 60%的粒子会闪烁
                    'glow': random.random() < 0.4,     # 40%的粒子会发光
                    'rainbow_trail': random.random() < 0.3  # 30%的粒子会有彩虹轨迹
                }
                particles.append(particle)
            
            def animate_firework(frame=0):
                if frame >= 40:  # 动画持续40帧
                    # 切换到波纹效果
                    animate_circle()
                    return
                
                self.canvas.delete("firework")  # 清除前一帧
                
                for p in particles:
                    # 更新位置
                    p['x'] += p['dx']
                    p['y'] += p['dy']
                    
                    # 添加轨迹点
                    p['trail'].append((p['x'], p['y']))
                    if len(p['trail']) > 5:  # 保持轨迹长度
                        p['trail'].pop(0)
                    
                    # 绘制轨迹
                    for i in range(len(p['trail']) - 1):
                        alpha = (i / len(p['trail'])) * p['alpha']
                        if alpha > 0.1:
                            self.canvas.create_line(
                                p['trail'][i][0], p['trail'][i][1],
                                p['trail'][i+1][0], p['trail'][i+1][1],
                                fill=p['color'],
                                width=p['size'] * alpha,
                                tags="firework"
                            )
                    
                    # 更新透明度
                    p['alpha'] = max(0, 1 - frame/50)
                    
                    # 绘制粒子
                    size = p['size'] * p['alpha']
                    self.canvas.create_oval(
                        p['x'] - size, p['y'] - size,
                        p['x'] + size, p['y'] + size,
                        fill=p['color'],
                        outline='',
                        tags="firework"
                    )
                
                self.window.after(16, lambda: animate_firework(frame + 1))
            
            animate_firework()
        
        # 开始烟花动画
        create_opening_firework()
        # 创建主波纹圆
        main_circle = self.canvas.create_oval(
            center_x, center_y,
            center_x, center_y,
            outline='#00ffff',  # 青色
            width=2.5,  # 稍微减小主线条宽度使其更柔和
            fill=''
        )
        
        # 创建内环（明亮层）
        inner_circle1 = self.canvas.create_oval(
            center_x, center_y,
            center_x, center_y,
            outline='#80ffff',  # 浅青色
            width=2,
            fill=''
        )
        
        inner_circle2 = self.canvas.create_oval(
            center_x, center_y,
            center_x, center_y,
            outline='#40ffff',  # 较浅青色
            width=1.5,
            fill=''
        )
        
        # 创建外环（暗色层）
        outer_circle1 = self.canvas.create_oval(
            center_x, center_y,
            center_x, center_y,
            outline='#004040',  # 深青色
            width=2,
            fill=''
        )
        
        outer_circle2 = self.canvas.create_oval(
            center_x, center_y,
            center_x, center_y,
            outline='#002020',  # 更深青色
            width=1.5,
            fill=''
        )
        
        def animate_circle(radius=0):
            """平滑的波纹动画"""
            if radius <= max_radius:
                # 使用正弦函数使透明度变化更平滑
                progress = radius / max_radius
                alpha = max(0, math.cos(progress * math.pi / 2))
                
                # 主圆更新（稍微提高基础透明度）
                alpha_hex = int(alpha * 255)
                main_color = f'#{alpha_hex:02x}ffff'
                main_radius = radius
                
                # 内环偏移和颜色（减小间距使其更紧凑）
                inner_radius1 = max(0, radius - 8)  # 减小间距
                inner_radius2 = max(0, radius - 15)
                inner_alpha1 = int(alpha * 230)  # 提高亮度
                inner_alpha2 = int(alpha * 200)
                
                # 外环偏移和颜色
                outer_radius1 = radius + 8  # 减小间距
                outer_radius2 = radius + 15
                outer_alpha1 = int(alpha * 200)  # 提高亮度使过渡更平滑
                outer_alpha2 = int(alpha * 170)
                
                # 更新所有圆形
                # 主圆
                self.canvas.coords(
                    main_circle,
                    center_x - main_radius,
                    center_y - main_radius,
                    center_x + main_radius,
                    center_y + main_radius
                )
                self.canvas.itemconfig(main_circle, outline=main_color)
                
                # 内环1
                self.canvas.coords(
                    inner_circle1,
                    center_x - inner_radius1,
                    center_y - inner_radius1,
                    center_x + inner_radius1,
                    center_y + inner_radius1
                )
                self.canvas.itemconfig(
                    inner_circle1,
                    outline=f'#{inner_alpha1:02x}ffff'
                )
                
                # 内环2
                self.canvas.coords(
                    inner_circle2,
                    center_x - inner_radius2,
                    center_y - inner_radius2,
                    center_x + inner_radius2,
                    center_y + inner_radius2
                )
                self.canvas.itemconfig(
                    inner_circle2,
                    outline=f'#{inner_alpha2:02x}ffff'
                )
                
                # 外环1
                self.canvas.coords(
                    outer_circle1,
                    center_x - outer_radius1,
                    center_y - outer_radius1,
                    center_x + outer_radius1,
                    center_y + outer_radius1
                )
                self.canvas.itemconfig(
                    outer_circle1,
                    outline=f'#{outer_alpha1:02x}4040'
                )
                
                # 外环2
                self.canvas.coords(
                    outer_circle2,
                    center_x - outer_radius2,
                    center_y - outer_radius2,
                    center_x + outer_radius2,
                    center_y + outer_radius2
                )
                self.canvas.itemconfig(
                    outer_circle2,
                    outline=f'#{outer_alpha2:02x}2020'
                )
                
                # 继续动画
                self.window.after(16, lambda: animate_circle(radius + 8))
            else:
                # 淡出效果
                def fade_out():
                    alpha = self.window.attributes('-alpha')
                    if alpha > 0:
                        alpha -= 0.14
                        # 加快淡出速度
                        self.window.attributes('-alpha', alpha)
                        self.window.after(10, fade_out)  # 减少延迟时间
                    else:
                        # 切换到游戏
                        if self.music_mode.get() in ["always", "conditional"]:
                            # 从5首背景音乐中随机选择一首
                            background_music = random.choice([
                                "background.mp3",
                                "background2.mp3", 
                                "background3.mp3",
                                "background4.mp3",
                                "background5.mp3"
                            ])
                            pygame.mixer.music.load(os.path.join(current_dir, "assets", "music", background_music))
                            pygame.mixer.music.play(-1)
                        self.window.destroy()
                        start_main_game()
                
                # 启动淡出效果
                fade_out()
        
        # 开始动画
        animate_circle()
    
    def on_hover(self, event, button):
        """鼠标悬停效果"""
        if button == self.music_button:
            button.config(bg="#64B5F6")  # 渐变为浅蓝色
        elif button == self.start_button:
            button.config(bg="#81C784")  # 渐变为浅绿色
        elif button == self.quit_button:
            button.config(bg="#FF8A65")  # 渐变为浅橙色
        elif button == self.left_button:
            button.config(bg=button.cget("activebackground")) 

    def on_leave(self, event, button):
        """鼠标离开效果"""
        if button == self.music_button:
            current_mode = self.music_mode.get()
            if current_mode == "always":
                button.config(bg="#1976D2")
            elif current_mode == "conditional":
                button.config(bg="#4FC3F7")
            else:  # off
                button.config(bg="#9E9E9E")
        if button == self.start_button:
            button.config(bg="#4CAF50")
        if button == self.quit_button:
            button.config(bg="#FF5722")
        if button == self.left_button:
            if self.mode == "Forbid":
                button.config(bg="#FFA726")
            else:
                button.config(bg="#9B59B6")

    def move_window(self, direction, fast_mode=False):
        """移动窗口
        Args:
            direction: 移动方向 ("Left", "Right", "Up", "Down")
            fast_mode: 是否快速移动模式(按住Shift键)
        """
        # 获取当前窗口位置
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        
        # 快速模式时移动速度翻倍
        step = self.move_step * 2 if fast_mode else self.move_step
        
        # 根据方向移动窗口
        if direction == "Left":
            x -= step
        elif direction == "Right":
            x += step
        elif direction == "Up":
            y -= step
        elif direction == "Down":
            y += step
            
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 获取窗口尺寸
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        # 确保窗口不会移出屏幕
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        # 创建轨迹特效
        trail = tk.Toplevel(self.window)
        trail.overrideredirect(True)
        trail.attributes('-alpha', 0.4)
        trail.lift()
        
        # 设置轨迹窗口位置和大小
        size = 10
        if direction in ["Left", "Right"]:
            trail_width = step
            trail_height = size
            trail_x = x + (window_width if direction == "Left" else -step)
            trail_y = y + (window_height // 2) - (size // 2)
        else:
            trail_width = size 
            trail_height = step
            trail_x = x + (window_width // 2) - (size // 2)
            trail_y = y + (window_height if direction == "Up" else -step)
            
        trail.geometry(f"{trail_width}x{trail_height}+{trail_x}+{trail_y}")
        
        # 创建Canvas
        canvas = tk.Canvas(
            trail,
            width=trail_width,
            height=trail_height,
            highlightthickness=0
        )
        canvas.pack()
        
        # 根据模式设置颜色
        if fast_mode:
            color1, color2 = "#FF1493", "#FF00FF"  # 深粉色和亮紫色,更鲜艳的搭配
        else:
            color1, color2 = "#1E90FF", "#00BFFF"  # 道奇蓝和深天蓝,更清新的搭配
            
        # 优化渐变效果绘制
        if direction in ["Left", "Right"]:
            # 水平方向每5个像素绘制一条线以减少绘制次数
            for i in range(0, trail_width, 5):
                ratio = i / trail_width
                color = self.gradient_color(color1, color2, ratio)
                canvas.create_rectangle(i, 0, i+5, trail_height, fill=color, outline="")
        else:
            # 垂直方向每5个像素绘制一条线以减少绘制次数
            for i in range(0, trail_height, 5):
                ratio = i / trail_height
                color = self.gradient_color(color1, color2, ratio)
                canvas.create_rectangle(0, i, trail_width, i+5, fill=color, outline="")
        
        # 设置平滑淡出
        def fade_out(alpha=0.4, step=0.05):
            if alpha > 0:
                trail.attributes('-alpha', alpha)
                trail.after(20, lambda: fade_out(alpha - step))
            else:
                trail.destroy()
                
        trail.after(10, fade_out)
        
        # 立即更新窗口位置
        self.window.geometry(f"+{x}+{y}")
        
    def gradient_color(self, color1, color2, ratio):
        """创建两个颜色之间的渐变色"""
        # 将十六进制颜色转换为RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # 计算渐变色的RGB值
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        # 转换回十六进制颜色
        return f"#{r:02x}{g:02x}{b:02x}"

def start_main_game():
    
    color_chose = random.randint(3, 5)
    trail_windows = []  # 用于存储所有尾痕窗口
    # 创建音效管理器
    sound_manager = SoundManager()
    sound_manager.enabled = StartPage.music_mode.get() != "off"
    
    # 获取音乐模式
    music_mode = StartPage.music_mode.get()
    
    # 初始化背景音乐
    if music_mode in ["always", "conditional"]:
        try:
            bgm_name = random.choice(["background", "background2", "background3", "background4", "background5"])
            bgm_path = os.path.join(current_dir, "assets", "music", f"{bgm_name}.mp3")
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.play(-1)
            
        except Exception as e:
            print(f"Failed to load background music: {e}")
    
    # 创建主窗口
    try:
        window = tk.Tk()
        window.title("Greedy Snake")
        
        # 设置窗口属性
        if os.name == 'nt':  # Windows系统
            try:
                # 初始设置完全透明
                window.attributes('-alpha', 0.0)
                
                # 创建淡入效果
                def fade_in(alpha=0.0):
                    try:
                        if alpha < 1.0:
                            # 使用正弦函数实现更自然的淡入效果
                            # sin(x)在[0,π/2]区间从0渐变到0.98
                            progress = alpha / 1.0  # 归一化进度到[0,1]
                            next_alpha = 0.98 * math.sin(progress * math.pi/2)
                            window.attributes('-alpha', next_alpha)
                            window.after(20, lambda: fade_in(alpha + 0.05))
                    except Exception as e:
                        print(f"淡入效果出错: {e}")
                        window.attributes('-alpha', 0.98)
                
                # 启动淡入效果
                window.after(100, fade_in)
            except Exception as e:
                print(f"设置窗口透明度失败: {e}")
                # 如果透明度设置失败,使用默认不透明
                window.attributes('-alpha', 1.0)
    
        # 添加图标
        try:
            icon_path = os.path.join(current_dir, "assets", "images", "snake_icon.ico")
            if os.path.exists(icon_path):
                window.iconbitmap(icon_path)
        except Exception as e:
            print(f"加载图标失败: {e}")
        
        window.resizable(False, False)
       
        # 设置窗口大小和位置
        window_width = 407
        window_height = 445
        
        # 获取屏幕尺寸
        try:
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
        except Exception as e:
            # 如果获取失败使用默认值
            screen_width = 1024
            screen_height = 768
        try:
            pywinstyles.apply_style(window, "immersive")
            window.overrideredirect(True)     # 移除标准窗口边框
            # 或者使用透明效果
            # pywinstyles.apply_style(self.window, "transparent")
        except Exception as e:
            print(f"应用窗口样式失败: {e}")    
        # 计算窗口位置,确保在屏幕内
        x = max(0, min((screen_width - window_width) // 2, screen_width - window_width))
        y = max(0, min((screen_height - window_height) // 2, screen_height - window_height))
        
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口焦点和层级
        try:
            window.focus_force()  # 强制获得焦点
            window.lift()         # 将窗口提升到最前
            window.attributes('-topmost', True)  # 暂时设置为最顶层
            window.after(1000, lambda: window.attributes('-topmost', False))  # 1秒后取消顶层
        except Exception as e:
            print(f"设置窗口焦点失败: {e}")
            
    except Exception as e:
        print(f"创建主窗口失败: {e}")
        sys.exit(1)
    window.bind("<Left>", lambda event: change_direction("Left"))
    window.bind("<Right>", lambda event: change_direction("Right"))
    window.bind("<Up>", lambda event: change_direction("Up"))
    window.bind("<Down>", lambda event: change_direction("Down"))
    def move_window(direction, fast_mode=False):
        """移动窗口位置"""
        x = window.winfo_x()
        y = window.winfo_y()
        step = 40 if fast_mode else 20  # 快速模式时移动步长加倍
        
        if direction == "Left":
            x -= step
        elif direction == "Right":
            x += step
        elif direction == "Up":
            y -= step
        elif direction == "Down":
            y += step
            
        # 确保窗口不会移出屏幕
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        # 创建轨迹特效
        nonlocal trail_windows
        trail = tk.Toplevel(window)
        trail.overrideredirect(True)
        trail.attributes('-alpha', 0.4)
        trail.lift()
        trail_windows.append(trail)  # 将新创建的尾痕窗口添加到列表中
        # 设置轨迹窗口位置和大小
        size = 10
        if direction in ["Left", "Right"]:
            trail_width = step
            trail_height = size
            trail_x = x + (window_width if direction == "Left" else -step)
            trail_y = y + (window_height // 2) - (size // 2)
        else:
            trail_width = size
            trail_height = step
            trail_x = x + (window_width // 2) - (size // 2)
            trail_y = y + (window_height if direction == "Up" else -step)
            
        trail.geometry(f"{trail_width}x{trail_height}+{trail_x}+{trail_y}")
        
        # 创建Canvas并添加渐变效果
        canvas = tk.Canvas(
            trail,
            width=trail_width,
            height=trail_height,
            highlightthickness=0
        )
        canvas.pack()
        
        # 根据模式设置不同的颜色
        if fast_mode:
            color1 = "#FF1493"  # 亮粉色
            color2 = "#FF69B4"  # 粉红色
        else:
            color1 = "#4169E1"  # 皇家蓝
            color2 = "#87CEEB"  # 天蓝色
        # 创建渐变效果
        def gradient_color(color1, color2, ratio):
            """计算渐变颜色"""
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            return f"#{r:02x}{g:02x}{b:02x}"
            
        if direction in ["Left", "Right"]:
            for i in range(trail_width):
                ratio = i / trail_width
                color = gradient_color(color1, color2, ratio)
                canvas.create_line(i, 0, i, trail_height, fill=color)
        else:
            for i in range(trail_height):
                ratio = i / trail_height
                color = gradient_color(color1, color2, ratio)
                canvas.create_line(0, i, trail_width, i, fill=color)
        
        # 设置平滑淡出
        def fade_out(alpha=0.4, step=0.05):
            if alpha > 0:
                trail.attributes('-alpha', alpha)
                trail.after(20, lambda: fade_out(alpha - step))
            else:
                trail.destroy()
                
        trail.after(10, fade_out)
        
        window.geometry(f"+{x}+{y}")
    def clear_trails():
        nonlocal trail_windows
        for trail in trail_windows:
            try:
                trail.destroy()
            except Exception as e:
                print(f" failed: {e}")
        trail_windows.clear()
    window.bind("<Control-Left>", lambda e: move_window("Left"))
    window.bind("<Control-Right>", lambda e: move_window("Right")) 
    window.bind("<Control-Up>", lambda e: move_window("Up"))
    window.bind("<Control-Down>", lambda e: move_window("Down"))
    window.bind("<Shift-Left>", lambda e: move_window("Left",True))
    window.bind("<Shift-Right>", lambda e: move_window("Right",True)) 
    window.bind("<Shift-Up>", lambda e: move_window("Up",True))
    window.bind("<Shift-Down>", lambda e: move_window("Down",True))
    window.bind("<Control-a>", lambda e: move_window("Left"))
    window.bind("<Control-d>", lambda e: move_window("Right")) 
    window.bind("<Control-w>", lambda e: move_window("Up"))
    window.bind("<Control-s>", lambda e: move_window("Down"))
    window.bind("<Shift-a>", lambda e: move_window("Left",True))
    window.bind("<Shift-d>", lambda e: move_window("Right",True)) 
    window.bind("<Shift-w>", lambda e: move_window("Up",True))
    window.bind("<Shift-s>", lambda e: move_window("Down",True))
    window.bind("<Control-A>", lambda e: move_window("Left"))
    window.bind("<Control-D>", lambda e: move_window("Right")) 
    window.bind("<Control-W>", lambda e: move_window("Up"))
    window.bind("<Control-S>", lambda e: move_window("Down"))
    window.bind("<Shift-A>", lambda e: move_window("Left",True))
    window.bind("<Shift-D>", lambda e: move_window("Right",True)) 
    window.bind("<Shift-W>", lambda e: move_window("Up",True))
    window.bind("<Shift-S>", lambda e: move_window("Down",True))
    # 设置游戏画布
    canvas = tk.Canvas(
        window,
        width=400,
        height=400,
        bg='#050505',
    )
    canvas.pack(
        padx=4,              # 左右各留4像素边距
        pady=0,              
        expand=False,        # 不需要扩展
        fill=tk.NONE         # 不需要填充
    )
    # 修改背景图片加载径
    background_images = ['background.jpg', 'background2.jpg','background3.jpg','background4.jpg','background5.jpg']
    selected_bg = random.choice(background_images)
    bg_image_path = os.path.join(current_dir, "assets", "images", selected_bg)
    image = Image.open(bg_image_path)
    image = image.resize((400, 400), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(image)
    
    # 在 Canvas 上创建图像（背景）
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
    # 确保景图片对象不会被垃圾回收
    canvas.bg_image = bg_image

    border_left = tk.Canvas(
        window,
        width=5,           
        height=445,
        highlightthickness=0
    )
    border_left.place(x=0, y=0)
    
    border_right = tk.Canvas(
        window,
        width=5,           
        height=445,
        highlightthickness=0
    )
    border_right.place(x=402, y=0)
    
    border_bottom = tk.Canvas(
        window,
        width=405,
        height=6,          
        highlightthickness=0
    )
    border_bottom.place(x=0, y=439)
    
    window.bind("<Escape>", lambda event: window.quit())
    # 定义霓虹灯颜色
    def generate_gradient_colors(steps):
        colors = [
            # 梦幻极光
            [
                "#FF5F5F",  # 珊瑚红 - 与金色黄昏的珊瑚色呼应
                "#3ECDC4",  # 青绿色 - 与深海幻境的海蓝绿相近
                "#45B7E1",  # 天蓝色 - 与深海幻境的皇家蓝相近
                "#DDA0DD",  # 梅红色 - 与紫罗兰梦呼应
                "#FFB7C5",  # 樱花粉 - 与樱花飞舞呼应
                "#FF4F4F"   # 浅红色 - 与樱花飞舞的深粉红相近
            ],
            # 深海幻境
            [
                "#00008B",  # 深蓝色
                "#4169E1",  # 皇家蓝
                "#00CED1",  # 深青色
                "#20B2AA",  # 海蓝绿
                "#7FFFD4",  # 碧绿色
                "#98FB98"   # 嫩绿色
            ],
            # 樱花飞舞
            [
                "#FFB7C5",  # 樱花粉
                "#FFC0CB",  # 粉红色
                "#FFB6C1",  # 浅粉红
                "#FF69B4",  # 热粉红
                "#FF1493",  # 深粉红
                "#DB7093"   # 苍紫罗兰红
            ],
            # 紫罗兰梦
            [
                "#E6E6FA",  # 薰衣草色
                "#D8BFD8",  # 蓟色
                "#DDA0DD",  # 梅红色
                "#DA70D6",  # 兰花色
                "#BA55D3",  # 中兰花紫
                "#9370DB"   # 中紫色
            ],
            # 金色黄昏
            [
                "#FFD700",  # 金色
                "#FFA500",  # 橙色
                "#FF8C00",  # 深橙色
                "#FF7F50",  # 珊瑚色
                "#FF6347",  # 番茄色
                "#FF4500"   # 橙红色
            ],
            # 森林晨露
            [
                "#90EE90",  # 淡绿色
                "#98FB98",  # 嫩绿色
                "#3CB371",  # 中海绿色
                "#2E8B57",  # 海绿色
                "#228B22",  # 森林绿
                "#006400"   # 深绿色
            ],
            # 极光之夜
            [
                "#191970",  # 午夜蓝
                "#483D8B",  # 暗板岩蓝
                "#6A5ACD",  # 板岩蓝
                "#7B68EE",  # 中板岩蓝
                "#9370DB",  # 中紫色
                "#8A2BE2"   # 紫罗兰色
            ]
        ][random.randint(0, 6)]  # 随机选择一种配色方案
        
        # 预先计算所有颜色的RGB值
        rgb_colors = []
        for color in colors:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            rgb_colors.append((r, g, b))
        
        gradient = []
        colors_len = len(colors) - 1
        step_size = colors_len / steps
        
        for i in range(steps):
            index = i * step_size
            idx1 = int(index)
            idx2 = min(idx1 + 1, colors_len)
            
            t = index - idx1
            r1, g1, b1 = rgb_colors[idx1]
            r2, g2, b2 = rgb_colors[idx2]
            
            r = int(r1 * (1-t) + r2 * t)
            g = int(g1 * (1-t) + g2 * t)
            b = int(b1 * (1-t) + b2 * t)
            
            gradient.append(f'#{r:02x}{g:02x}{b:02x}')
        return gradient
    
    # 生成渐变色
    gradient_colors = generate_gradient_colors(30)  # 30个渐变色
    offset = [0]  # 用于颜色偏移
    
    def update_border_color():
        # 预先计算常用值
        segments_per_border = 30  # 每个边框30段
        height_per_segment = 445 / segments_per_border
        width_per_segment = 405 / segments_per_border
        gradient_len = len(gradient_colors)
        
        # 更新偏移量
        offset[0] = (offset[0] + 1) % gradient_len
        
        # 预先计算所有需要的颜色索引和颜色
        color_indices = [(i + offset[0]) % gradient_len for i in range(segments_per_border * 3)]
        colors = [gradient_colors[i] for i in color_indices]
        
        # 分配颜色给各个边框
        left_colors = colors[:segments_per_border]
        right_colors = colors[segments_per_border:segments_per_border*2]
        bottom_colors = colors[segments_per_border*2:]
        
        # 清除旧的内容
        for canvas in [border_left, border_right, border_bottom]:
            canvas.delete("all")
            
        # 批量创建图形数据
        def create_border_rects(colors, is_vertical):
            rects = []
            for i, color in enumerate(colors):
                if is_vertical:
                    y1 = i * height_per_segment
                    y2 = y1 + height_per_segment
                    rects.extend([
                        (-2, y1-2, 7, y2+2, color, "gray50"),
                        (0, y1, 5, y2, color, "")
                    ])
                else:
                    x1 = i * width_per_segment
                    x2 = x1 + width_per_segment
                    rects.extend([
                        (x1-2, -2, x2+2, 8, color, "gray50"),
                        (x1, 0, x2, 6, color, "")
                    ])
            return rects
            
        # 生成并绘制所有边框
        for canvas, colors, is_vertical in [
            (border_left, left_colors, True),
            (border_right, right_colors, True), 
            (border_bottom, bottom_colors, False)
        ]:
            rects = create_border_rects(colors, is_vertical)
            for x1, y1, x2, y2, color, stipple in rects:
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", stipple=stipple)
        
        # 绘制圆角连接处
        left_corner_color = left_colors[-1]
        right_corner_color = right_colors[-1]
        
        # 左下角
        border_left.create_arc(-2, 438, 12, 452, start=180, extent=90, fill=left_corner_color, stipple="gray50")
        border_left.create_arc(0, 440, 10, 450, start=180, extent=90, fill=left_corner_color)
        
        # 右下角
        border_right.create_arc(-7, 438, 7, 452, start=270, extent=90, fill=right_corner_color, stipple="gray50")
        border_right.create_arc(-5, 440, 5, 450, start=270, extent=90, fill=right_corner_color)
        
        window.after(16, update_border_color)
    
    # 启动颜色更新
    window.after(100, update_border_color)
    
    # 定义蛇的初始状态
    snake = [(20, 20), (20, 40), (20, 60)]
    snake_direction = "Down"
    
    # 修改物相关的变量声明
    food = None  # 始化为None
    
    # 定义游戏态
    game_running = True
    
    # 将这些变量声明为全局变量
    game_paused = False
    current_score = 0
    snake_speed = 100
    
    # 粒子类定义
    class Particle:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.color = color
            self.size = random.randint(3, 6)
            
            # 360度喷射
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(4.0, 7.0)
            
            # 添加向上的初始速度
            self.speed_x = math.cos(angle) * speed
            self.speed_y = math.sin(angle) * speed - 2  # -2给一个向上的初始速度
            
            self.alpha = 1.0
            self.id = None
            self.gravity = 0.2     # 重力效果
            self.drag = 0.97      # 空气阻力
            
            # 闪烁效果
            self.flicker_rate = random.uniform(0.05, 0.15)
            self.base_alpha = 1.0
            self.flicker_offset = random.uniform(0, math.pi * 2)
            
            # 尾迹效果
            self.trail = []
            self.trail_length = 5
    
    particles = []
    
    # 在定义 particles 列表后添加
    ripple_particles = []  # 初始化涟漪粒子列表
    
    # 加载水波声效
    ripple_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets", "music", "water_ripple.wav"))
    ripple_sound.set_volume(0.2)  # 设置音量为20%
    
    # 在 Particle 类后添加
    class RippleParticle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.size = 0
            self.max_size = random.uniform(80, 100)  # 增加最大尺寸
            self.speed = random.uniform(1.2, 1.5)    # 降低速度使动画更柔和
            self.alpha = 1.0
            # 增加更多的环来制造层次感
            self.rings = [
                {"size": 0, "alpha": 1.0, "width": 2.0},
                {"size": -10, "alpha": 0.9, "width": 1.8},
                {"size": -20, "alpha": 0.8, "width": 1.6},
                {"size": -30, "alpha": 0.7, "width": 1.4},
                {"size": -40, "alpha": 0.6, "width": 1.2},
                {"size": -50, "alpha": 0.5, "width": 1.0}
            ]
            self.wave_offset = random.uniform(0, math.pi * 2)
            self.wave_speed = random.uniform(0.08, 0.12)  # 降低波动速度
            self.fade_speed = random.uniform(0.02, 0.03)  # 添加淡出速度
            
            # 播放水波声效
            if len(ripple_particles) < 3:  # 限制同时播放的声音数量
                ripple_sound.play()
                
    class MilestoneParticle:
        def __init__(self, x, y, color, angle, speed):
            self.x = x
            self.y = y
            self.color = color
            self.speed_x = math.cos(angle) * speed
            self.speed_y = math.sin(angle) * speed
            self.life = 1.0
            self.fade_speed = random.uniform(0.02, 0.04)
            self.size = random.uniform(3, 5)
            self.gravity = 0.2
            self.flicker_offset = random.uniform(0, math.pi * 2)
            self.base_alpha = 1.0
    
    milestone_particles = []  # 存储里程碑特效的粒子
    
    def create_milestone_effect(score):
        """创建现代霓虹风格的里程碑特效"""
        # 预定义配色方案,避免每次重新创建字典
        color_schemes = {
            'cyber_pink': {
                'primary': ["#FF1493", "#FF0090", "#FF0070", "#FF0050", "#FF0030"],  # 更鲜艳的粉红色
                'glow': "#FF1493",
                'accent': ["#FFFFFF", "#FF1493", "#FF0090"]
            },
            'quantum_blue': {
                'primary': ["#00FFFF", "#00B7FF", "#0090FF", "#0066FF", "#003CFF"],  # 更明亮的蓝色
                'glow': "#00FFFF", 
                'accent': ["#FFFFFF", "#00FFFF", "#00B7FF"]
            },
            'neon_purple': {
                'primary': ["#9932CC", "#8B00FF", "#7B00FF", "#6A00FF", "#5900FF"],  # 更深邃的紫色
                'glow': "#9932CC",
                'accent': ["#FFFFFF", "#9932CC", "#8B00FF"]
            },
            'toxic_green': {
                'primary': ["#00FF00", "#00DD00", "#00BB00", "#009900", "#007700"],
                'glow': "#00FF00",
                'accent': ["#FFFFFF", "#00FF00", "#00DD00"]
            },
            'plasma_gold': {
                'primary': ["#FFD700", "#FFC125", "#FFB90F", "#FFA500", "#FF8C00"],  # 更温暖的金色
                'glow': "#FFD700",
                'accent': ["#FFFFFF", "#FFD700", "#FFC125"]
            },
            'inferno_red': {
                'primary': ["#FF3030", "#FF0000", "#CD0000", "#8B0000", "#800000"],  # 更热烈的红色
                'glow': "#FF3030",
                'accent': ["#FFFFFF", "#FF3030", "#FF0000"]
            },
            'ocean_blue': {
                'primary': ["#00FFFF", "#00C0FF", "#0090FF", "#0060FF", "#0030FF"],
                'glow': "#00FFFF",
                'accent': ["#FFFFFF", "#00FFFF", "#00C0FF"]
            },
            'electric_blue': {
                'primary': ["#87CEFA", "#1E90FF", "#0000FF", "#0000CD", "#00008B"],  # 更明亮的电光蓝
                'glow': "#87CEFA",
                'accent': ["#FFFFFF", "#87CEFA", "#1E90FF"]
            },
            'void_violet': {
                'primary': ["#9400D3", "#8A2BE2", "#9370DB", "#7B68EE", "#6A5ACD"],  # 更神秘的紫罗兰
                'glow': "#9400D3",
                'accent': ["#FFFFFF", "#9400D3", "#8A2BE2"]
            },
            'solar_orange': {
                'primary': ["#FFA500", "#FF8C00", "#FF7F00", "#FF6347", "#FF4500"],  # 更温暖的橙色
                'glow': "#FFA500",
                'accent': ["#FFFFFF", "#FFA500", "#FF8C00"]
            },
            'aqua_teal': {
                'primary': ["#40E0D0", "#48D1CC", "#00CED1", "#20B2AA", "#008B8B"],  # 更清新的青色
                'glow': "#40E0D0",
                'accent': ["#FFFFFF", "#40E0D0", "#48D1CC"]
            },
            'acid_lime': {
                'primary': ["#32CD32", "#98FB98", "#90EE90", "#7CCD7C", "#66CD00"],  # 更活力的青柠色
                'glow': "#32CD32",
                'accent': ["#FFFFFF", "#32CD32", "#98FB98"]
            },
            'rainbow_burst': {
                'primary': ["#FF69B4", "#FF1493", "#FF00FF", "#9400D3", "#4B0082"],  # 更绚丽的彩虹色
                'glow': "#FF69B4",
                'accent': ["#FFFFFF", "#FF69B4", "#FF1493"]
            },
            'prismatic_flow': {
                'primary': ["#FF00FF", "#EE00EE", "#CD00CD", "#8B008B", "#800080"],  # 更梦幻的棱镜色
                'glow': "#FF00FF",
                'accent': ["#FFFFFF", "#FF00FF", "#EE00EE"]
            }
        }
        
        scheme_name = random.choice(list(color_schemes.keys()))
        colors = color_schemes[scheme_name]
        sound_manager.play('milestone')
        center_x, center_y = 200, 200
        start_time = time.time()
        
        # 预计算所有常量
        TWO_PI = 2 * math.pi
        PARTICLE_COUNT = 32
        ANGLE_STEP = TWO_PI / PARTICLE_COUNT
        base_size = 42
        
        # 预计算所有三角函数值和装饰点位置
        cos_angles = [math.cos(i * ANGLE_STEP) for i in range(PARTICLE_COUNT)]
        sin_angles = [math.sin(i * ANGLE_STEP) for i in range(PARTICLE_COUNT)]
        dot_positions = [(math.cos(math.radians(angle)), math.sin(math.radians(angle))) 
                        for angle in range(0, 360, 45)]
        
        # 预计算粒子颜色
        primary_colors = colors['primary']
        color_indices = [min(int((i / PARTICLE_COUNT) * len(primary_colors)), len(primary_colors)-1) 
                        for i in range(PARTICLE_COUNT)]
        
        # 初始化particles列表
        particles = []
        
        # 创建粒子
        for i in range(PARTICLE_COUNT):
            particles.append((
                center_x,  # x
                center_y,  # y
                cos_angles[i],  # cos_angle
                sin_angles[i],  # sin_angle
                random.uniform(3.0, 4.0),  # speed
                random.uniform(1.5, 2.5),  # size
                primary_colors[color_indices[i]],  # color
                random.uniform(0, TWO_PI)  # phase
            ))
        
        # 缓存常用值
        accent_colors = colors['accent']
        text_offsets = [(-1,0), (1,0), (0,-1), (0,1)]  # 标准化文本偏移
        
        def animate_milestone():
            nonlocal particles
            
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed >= 6.0:
                return
            
            # 使用列表存储绘图命令
            BUFFER_SIZE = PARTICLE_COUNT * 3 + 20 + 1
            draw_buffer = [None] * BUFFER_SIZE
            buffer_index = 0
            
            # 预计算常用值
            fade_factor = max(0, 1.0 - elapsed / 6.0)
            elapsed_3 = elapsed * 3
            elapsed_2_5 = elapsed * 2.5
            sin_elapsed_2_5 = math.sin(elapsed_2_5)
            text_fade = min(1.0, elapsed / 0.5) * (1.0 - max(0, (elapsed - 2.5) / 0.5))
            scale = (1 + sin_elapsed_2_5 * 0.03) * text_fade
            base_scaled = int(base_size * scale)
            
            # 轨迹参数
            trail_length = 12 * fade_factor
            trail_factors = [0.7, 0.4, 0.1]
            
            # 创建局部变量引用以减少查找
            create_line = canvas.create_line
            create_text = canvas.create_text
            create_oval = canvas.create_oval
            sin = math.sin
            
            def process_particle_batch(start_idx, end_idx):
                nonlocal buffer_index
                new_particles = []
                
                for i in range(start_idx, end_idx):
                    if i >= len(particles):
                        break
                        
                    x, y, cos_angle, sin_angle, speed, size, color, phase = particles[i]
                    
                    # 波动和移动计算
                    wave = sin(elapsed_3 + phase) * 0.2
                    move_factor = fade_factor * (1 + wave)
                    speed_factor = speed * move_factor
                    
                    # 计算新位置
                    new_x = x + cos_angle * speed_factor
                    new_y = y + sin_angle * speed_factor
                    
                    # 保存新的粒子状态
                    new_particles.append((new_x, new_y, cos_angle, sin_angle, speed, size, color, phase))
                    
                    # 生成轨迹
                    trail_size = size * fade_factor
                    trail_cos = cos_angle * trail_length
                    trail_sin = sin_angle * trail_length
                    current_trail_size = trail_size
                    
                    for factor in trail_factors:
                        if buffer_index < BUFFER_SIZE:
                            trail_x = new_x - trail_cos * factor
                            trail_y = new_y - trail_sin * factor
                            draw_buffer[buffer_index] = ('line', (
                                new_x, new_y, trail_x, trail_y,
                                color, current_trail_size
                            ))
                            buffer_index += 1
                            current_trail_size -= trail_size * 0.3
                
                return new_particles
            
            # 使用线程池处理粒子更新
            particle_count = len(particles)
            batch_size = max(50, particle_count // 4)
            new_particles = []
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for start_idx in range(0, particle_count, batch_size):
                    end_idx = min(start_idx + batch_size, particle_count)
                    futures.append(executor.submit(process_particle_batch, start_idx, end_idx))
                
                # 收集所有批次的结果
                for future in futures:
                    new_particles.extend(future.result())
            
            # 更新粒子列表
            particles = new_particles
            
            # 显示数字效果
            if elapsed < 3.0:
                text_str = str(score)
                
                # 预计算文本参数
                text_params = [(i * 2 * scale,
                               ("Arial Black", base_scaled + int(i * 2), "bold"),
                               accent_colors[min(i, len(accent_colors)-1)])
                              for i in range(3)]
                
                # 绘制文本效果
                for offset, font, color in text_params:
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        if buffer_index < BUFFER_SIZE:
                            draw_buffer[buffer_index] = ('text', (
                                center_x + offset * dx,
                                center_y + offset * dy,
                                text_str, font, color
                            ))
                            buffer_index += 1
                
                # 中心文本
                if buffer_index < BUFFER_SIZE:
                    draw_buffer[buffer_index] = ('text', (
                        center_x, center_y, text_str,
                        ("Arial Black", base_scaled, "bold"),
                        accent_colors[0]
                    ))
                    buffer_index += 1
                
                # 装饰点
                dot_radius = scale * 2
                dist = base_size * 1.5
                for angle in range(0, 360, 45):
                    if buffer_index < BUFFER_SIZE:
                        rad = math.radians(angle)
                        x = center_x + math.cos(rad) * dist
                        y = center_y + math.sin(rad) * dist
                        draw_buffer[buffer_index] = ('oval', (
                            x - dot_radius,
                            y - dot_radius,
                            x + dot_radius,
                            y + dot_radius,
                            accent_colors[1]
                        ))
                        buffer_index += 1
            
            # 清除旧内容
            canvas.delete("milestone")
            
            # 批量执行绘图命令
            for i in range(buffer_index):
                cmd_type, args = draw_buffer[i]
                if cmd_type == 'line':
                    create_line(*args[:4], 
                               fill=args[4], 
                               width=args[5],
                               capstyle=tk.ROUND, 
                               tags="milestone")
                elif cmd_type == 'text':
                    create_text(*args[:2], 
                               text=args[2], 
                               font=args[3],
                               fill=args[4], 
                               tags="milestone")
                else:  # oval
                    create_oval(*args[:4], 
                               fill=args[4],
                               outline="", 
                               tags="milestone")
            
            # 继续动画
            canvas.after(16, animate_milestone)
        
        animate_milestone()
    
    def create_ripple(event):
        """创建蓝色涟漪效果"""
        if 0 <= event.x <= 400 and 0 <= event.y <= 400:
            ripple_particles.append(RippleParticle(event.x, event.y))
            update_ripples()
    
    def update_ripples():
        """更新并绘制所有涟漪粒子"""
        canvas.delete("ripple")
        current_time = time.time()

        for particle in ripple_particles[:]:
            remove_particle = True
            
            for ring in particle.rings:
                # 更新环的大小
                ring["size"] += particle.speed
                
                # 更复杂的波动效果
                time_factor = current_time * 4
                distance_factor = ring["size"] * 0.015
                
                # 组合多个正弦波创造更自然的波动
                wave = (math.sin(time_factor + particle.wave_offset + distance_factor) * 0.3 +
                    math.sin(time_factor * 0.7 + particle.wave_offset * 1.2 + distance_factor * 0.8) * 0.2)
                
                actual_size = ring["size"] * (1 + wave * 0.08)
                
                # 改进的透明度计算
                base_alpha = max(0, 1 - (abs(actual_size) / particle.max_size))
                ring["alpha"] = base_alpha * (1 + wave * 0.1)
                
                if ring["alpha"] > 0:
                    remove_particle = False
                    wave_stretch = 1 + wave * 0.03
                    
                    # 改进的颜色计算
                    alpha = ring["alpha"]
                    # 提高基础亮度
                    base_brightness = 180  # 提高基础亮度值
                    
                    # 动态颜色计算
                    r_component = int(min(255, base_brightness + wave * 20))
                    g_component = int(min(255, base_brightness + wave * 25))
                    b_component = int(min(255, base_brightness + wave * 30))
                    
                    # 确保外圈也保持明亮
                    min_brightness = 140  # 设置最小亮度
                    r_component = max(min_brightness, r_component)
                    g_component = max(min_brightness, g_component)
                    b_component = max(min_brightness, b_component)
                    
                    # 转换alpha值为16进制
                    alpha_hex = int(min(255, max(0, alpha * 255)))
                    
                    # 生成颜色代码
                    color = f'#{r_component:02x}{g_component:02x}{b_component:02x}'
                    
                    # 主要水波
                    canvas.create_oval(
                        particle.x - actual_size,
                        particle.y - actual_size * wave_stretch,
                        particle.x + actual_size,
                        particle.y + actual_size * wave_stretch,
                        outline=color,
                        width=ring["width"],
                        tags="ripple"
                    )
                    
                    # 改进的内部光晕效果
                    if ring["alpha"] > 0.2:  # 降低光晕显示阈值
                        glow_size = actual_size * 0.97
                        # 使用更明亮的光晕颜色
                        glow_color = "#7FD3F7"  # 更亮的蓝色
                        canvas.create_oval(
                            particle.x - glow_size,
                            particle.y - glow_size * wave_stretch,
                            particle.x + glow_size,
                            particle.y + glow_size * wave_stretch,
                            outline=glow_color,
                            width=1.0,  # 增加光晕宽度
                            tags="ripple",
                            stipple='gray25'
                        )
                        
                        # 添加额外的内部光晕
                        if ring["alpha"] > 0.4:
                            inner_glow_size = actual_size * 0.94
                            canvas.create_oval(
                                particle.x - inner_glow_size,
                                particle.y - inner_glow_size * wave_stretch,
                                particle.x + inner_glow_size,
                                particle.y + inner_glow_size * wave_stretch,
                                outline="#A5E1FF",  # 更亮的内部光晕
                                width=0.8,
                                tags="ripple",
                                stipple='gray25'
                            )
            
            if remove_particle:
                ripple_particles.remove(particle)

        if ripple_particles:
            window.after(16, update_ripples)
    
    # 创建食物爆炸效果
    def create_food_effect(x, y, food_type):
        # 使用渐变色方案
        color_schemes = {
            'normal': [
                "#FF0000", "#FF3333", "#FF4444", "#FF6666",  # 红色渐变系
                "#FF1111", "#FF2222", "#FF5555"
            ],
            'golden': [
                "#FFD700", "#FFC125", "#FFB90F", "#FFA500",  # 金色渐变系
                "#FFD800", "#FFB800", "#FFA200"
            ],
            'special': [
                "#9400D3", "#8A2BE2", "#9370DB", "#8B00FF",  # 紫罗兰渐变系
                "#9932CC", "#BA55D3", "#9B30FF"
            ],
            'rainbow': ['#FF1493',  # 亮粉红 - 甜蜜的草莓味
                        '#FF69B4',  # 粉红色 - 柔和的樱桃味
                        '#00FFFF',  # 青色 - 清爽的薄荷味
                        '#1E90FF',  # 道奇蓝 - 清凉的蓝莓味
                        '#9370DB',  # 中紫色 - 浪漫的葡萄味
                        '#FF6EB4',  # 热粉红 - 可爱的树莓味
                        '#40E0D0'   # 绿松石色 - 清新的薄荷味
                        ]  # 添加彩虹颜色
            ,
            'star_candy': [
                '#FF3366',  # 珊瑚玫瑰 - 充满活力不刺眼
                '#00B8D4',  # 海洋蓝 - 清新深邃
                '#7E57C2',  # 暮光紫 - 优雅神秘
                '#26A69A',  # 青玉石 - 温和沉静
                '#FF6B9C',  # 樱花粉 - 柔美甜蜜
                '#5C6BC0',  # 星空蓝 - 深邃梦幻
                '#2ECC71',  # 翡翠绿 - 生机盎然
                '#9B59B6',  # 紫水晶 - 高贵典雅
                '#16A085',  # 孔雀绿 - 沉稳优雅
                '#F39C12'   # 琥珀金 - 温暖明亮
            ]
        }
        
        # 不食物类型的粒子数量
        particle_counts = {
            'normal': 15,   # 红色食物
            'golden': 25,   # 金色食物
            'special': 40 ,  # 紫色食物
            'rainbow': 50 , # 设置为50个粒子
            'star_candy': 40
        }
        
        colors = color_schemes[food_type]
        particle_count = particle_counts[food_type]
        
        # 创建粒子
        for _ in range(particle_count):
            particles.append(Particle(x + 10, y + 10, random.choice(colors)))
        
        # 在这里添加里程碑检查
        score_ = current_score + food.properties[food_type]['score']  
        if score_ // 20 > current_score // 20:  # 检查是否跨越了20的倍数
            create_milestone_effect(score_)
            #print(score_)
    
    # 更新粒子效果
    def update_particles():
        # 1. 缓存更多频繁使用的方法和属性
        canvas_ref = canvas
        create_oval = canvas_ref.create_oval
        delete = canvas_ref.delete
        sin = math.sin
        max_min = lambda x, min_val, max_val: max(min_val, min(max_val, x))
        
        # 2. 预计算常量值并使用局部变量
        current_time = time.time() * 10
        STIPPLE_GRAY50 = 'gray50'
        EMPTY_STR = ''
        TRAIL_BATCH_SIZE = 4
        
        # 3. 使用数组替代列表来存储坐标
        coords_array = array.array('f', [0] * 4)
        
        # 4. 预分配固定大小的缓冲区并重用
        TRAIL_BUFFER_SIZE = 50
        trail_buffer = [[0] * 4 for _ in range(TRAIL_BUFFER_SIZE)]
        
        # 5. 批量处理前预先计算总数
        particle_count = len(particles)
        active_particles = []
        active_particles_append = active_particles.append  # 局部化方法调用
        
        # 6. 使用更高效的批处理逻辑
        for i in range(0, particle_count, TRAIL_BATCH_SIZE):
            batch_end = min(i + TRAIL_BATCH_SIZE, particle_count)
            
            for j in range(i, batch_end):
                particle = particles[j]
                
                # 7. 快速路径检查
                if particle.alpha <= 0:
                    if particle.id:
                        delete(particle.id)
                        if particle.trail:
                            delete(*particle.trail)
                    continue
                
                # 8. 物理更新优化 - 减少乘法运算
                drag = particle.drag
                particle.speed_y = particle.speed_y * drag + particle.gravity * drag
                particle.speed_x *= drag
                
                # 9. 位置更新 - 直接修改
                old_x, old_y = particle.x, particle.y
                particle.x += particle.speed_x
                particle.y += particle.speed_y
                
                # 10. Alpha值更新优化
                base_alpha = particle.base_alpha - 0.02
                particle.base_alpha = base_alpha
                flicker = sin(current_time + particle.flicker_offset) * 0.3 + 0.7
                particle.alpha = max_min(base_alpha * flicker, 0, 1)
                
                # 11. 清理旧图形 - 批量操作
                if particle.id:
                    delete(particle.id)
                    if particle.trail:
                        delete(*particle.trail)
                        particle.trail = []
                
                # 12. 尾迹绘制优化
                if base_alpha > 0.3:
                    trail_alpha = particle.alpha
                    dx = (particle.x - old_x) / particle.trail_length
                    dy = (particle.y - old_y) / particle.trail_length
                    trail_ids = []
                    trail_ids_append = trail_ids.append
                    base_size = particle.size * particle.alpha
                    
                    # 13. 尾迹批处理优化
                    for k in range(0, particle.trail_length, TRAIL_BATCH_SIZE):
                        batch = min(TRAIL_BATCH_SIZE, particle.trail_length - k)
                        
                        for m in range(batch):
                            idx = k + m
                            trail_x = old_x + dx * idx
                            trail_y = old_y + dy * idx
                            trail_size = base_size * (0.5 + idx / particle.trail_length)
                            half_size = trail_size * 0.5
                            
                            coords = trail_buffer[idx]
                            coords[0] = trail_x - half_size
                            coords[1] = trail_y - half_size
                            coords[2] = trail_x + half_size
                            coords[3] = trail_y + half_size
                            
                            trail_ids_append(create_oval(
                                *coords,
                                fill=particle.color,
                                stipple=STIPPLE_GRAY50 if trail_alpha < 0.5 else EMPTY_STR,
                                width=0
                            ))
                            trail_alpha *= 0.6
                    
                    particle.trail = trail_ids
                
                # 14. 主粒子绘制优化
                current_size = particle.size * particle.alpha
                half_size = current_size * 0.5
                coords_array[0] = particle.x - half_size
                coords_array[1] = particle.y - half_size
                coords_array[2] = particle.x + half_size
                coords_array[3] = particle.y + half_size
                
                particle.id = create_oval(
                    *coords_array,
                    fill=particle.color,
                    stipple=STIPPLE_GRAY50 if particle.alpha < 0.5 else EMPTY_STR,
                    width=0
                )
                
                active_particles_append(particle)
        
        # 15. 原地更新粒子列表
        particles[:] = active_particles
    
    def toggle_pause():
        nonlocal game_paused
        game_paused = not game_paused
        
        # 无论是暂停还是继续，都重新绘制整个画面
        canvas.delete("all")  # 清除所有内容
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
        draw_snake()
        draw_food() 
        draw_score()
        
        if not game_paused:
            # 继续游戏时，直接调用 move_snake
            move_snake()
            pause_button.config(bg="#4CAF50")
        else:
            pause_button.config(bg="#9C27B0")
    
    def reset_game(event=None):
        nonlocal snake, snake_direction, food, game_running, current_score, game_paused, snake_speed
        nonlocal color_chose,gradient_colors
        gradient_colors = generate_gradient_colors(30)  # 30个渐变色

        for after_id in window.tk.eval('after info').split():
            try:
                window.after_cancel(int(after_id))
            except ValueError:
                continue
        color_chose = random.randint(0, 5)
        # 重置游戏状态
        snake = [(20, 20), (20, 40), (20, 60)]
        snake_direction = "Down"
        current_score = 0
        snake_speed = 100
        game_running = True
        game_paused = False
        pause_button.config(bg="#4CAF50")
        clear_trails()  # 清除所有尾痕
        # 根据不同的音乐模式处理音乐
        if music_mode == "conditional":
            # 随机选择新的背景音乐
            bgm_name = random.choice(["background", "background2","background3","background4","background5"])  # 随机选择文件名
            bgm_path = os.path.join(current_dir, "assets", "music", f"{bgm_name}.mp3")
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.play(-1)
        
        # 清除画布并重绘所有内容
        def stop_animations():
            # 保存当前的边框动画after ID
            border_animation_ids = []
            for after_id in window.tk.eval('after info').split():
                # 检查这个after是否是边框动画的
                if "update_border_color" in window.tk.eval(f'after info {after_id}'):
                    border_animation_ids.append(after_id)
                    continue
                window.after_cancel(after_id)
            for widget in window.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            canvas.delete("all")  # 清除所有画布元素
            canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)  # 重新创建背景
        
        # 清理动画和画布
        stop_animations()
        
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
        window.unbind("<Left>")
        window.unbind("<Right>") 
        window.unbind("<Up>")
        window.unbind("<Down>")
        window.bind("<Left>", lambda event: change_direction("Left"))
        window.bind("<Right>", lambda event: change_direction("Right"))
        window.bind("<Up>", lambda event: change_direction("Up"))
        window.bind("<Down>", lambda event: change_direction("Down"))
        # 添加更优雅的圆环特效
        def create_elegant_ripple(step=0, max_steps=30):
            if step < max_steps:
                center_x, center_y = 200, 200
                base_radius = step * 12
                alpha = 1 - (step / max_steps)
                
                # 创建多层次圆环
                for i in range(8):  # 增加圆环层数
                    radius = base_radius - (i * 2)
                    if radius > 0:
                        # 使用更飘逸的渐变色彩
                        colors = [
                            f"#{int(alpha * 255):02x}e8ff",  # 梦幻蓝
                            f"#{int(alpha * 255):02x}f2ff",  # 淡紫
                            f"#{int(alpha * 255):02x}fffa",  # 浅金
                            f"#{int(alpha * 255):02x}ffd6",  # 玫瑰金
                            f"#{int(alpha * 255):02x}f5ff",  # 幻彩紫
                            f"#{int(alpha * 255):02x}e8ff",  # 梦幻紫
                            f"#{int(alpha * 255):02x}d9ff",  # 星空蓝
                            f"#{int(alpha * 255):02x}ecff"   # 极光色
                        ]
                        
                        # 主圆环 - 添加双层效果
                        for offset in [-1, 1]:  # 创建内外两层
                            circle = canvas.create_oval(
                                center_x - (radius + offset),
                                center_y - (radius + offset),
                                center_x + (radius + offset),
                                center_y + (radius + offset),
                                outline=colors[i],
                                width=1.5 if i == 0 else 0.8,
                                fill=""
                            )
                            
                            # 使用更柔和的淡出效果
                            fade_time = int(42 * (1 + (i/8)**2.8))
                            window.after(fade_time, lambda c=circle: canvas.delete(c))
                
                # 添加动态光点和星芒效果
                if step % 2 == 0:
                    for i in range(6):  # 增加光点数量
                        angle = (step / max_steps) * math.pi * 2 + (i * math.pi / 3)
                        for j in range(3):  # 每个方向三个光点
                            dot_radius = base_radius * (0.6 + j * 0.15)
                            dot_x = center_x + math.cos(angle) * dot_radius
                            dot_y = center_y + math.sin(angle) * dot_radius
                            
                            # 创建星芒效果
                            star_points = []
                            for k in range(5):  # 五角星芒
                                star_angle = angle + (k * math.pi / 2.5)
                                star_points.extend([
                                    dot_x + math.cos(star_angle) * (5 - j),
                                    dot_y + math.sin(star_angle) * (5 - j)
                                ])
                            
                            # 绘制星芒
                            star = canvas.create_polygon(
                                star_points,
                                fill=f"#{int(alpha * 255):02x}f0fb",
                                outline="",
                                smooth=True
                            )
                            
                            # 快速淡出效果
                            window.after(25, lambda s=star: canvas.delete(s))
                
                # 更平滑的动画过渡
                window.after(16, lambda: create_elegant_ripple(step + 1))
        
        create_elegant_ripple()
        
        # 生成新食物
        generate_food()
        
        # 绘制游戏元素
        draw_snake()
        draw_food()
        draw_score()
        
        # 直接调用 move_snake
        move_snake()
    
    # 然后创建按框架按钮
    button_frame = tk.Frame(window)
    button_frame.pack(pady=0)
    
    pause_button = tk.Button(
        button_frame,
        text="Pause/Continue",
        command=toggle_pause,
        width=12,
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 10, "bold"),
        relief="flat",
        borderwidth=0
    )
    pause_button.configure(highlightthickness=0)
    pause_button.bind('<Map>', lambda e: e.widget.configure(relief="flat"))
    pause_button.configure(cursor="hand2")
    pause_button.configure(bd=0, highlightthickness=0)
    pause_button.configure(compound="center")
    pause_button.configure(padx=10)
    pause_button.configure(pady=7.499999999)
    pause_button.configure(relief="ridge")
    pause_button.pack(side=tk.LEFT, padx=5)
    
    restart_button = tk.Button(
        button_frame,
        text="Restart",
        command=reset_game,
        width=10,
        bg="#2196F3",
        fg="white",
        font=("Helvetica", 10, "bold"),
        relief="flat", 
        borderwidth=0
    )
    restart_button.configure(highlightthickness=0)
    restart_button.bind('<Map>', lambda e: e.widget.configure(relief="flat"))
    restart_button.configure(cursor="hand2")
    restart_button.configure(bd=0, highlightthickness=0)
    restart_button.configure(compound="center")
    restart_button.configure(padx=10)
    restart_button.configure(pady=7.499999999)
    restart_button.configure(relief="ridge")
    restart_button.pack(side=tk.LEFT, padx=5)
    
    # 添加返按钮
    def back_to_start():
        """返回开始页面,带平滑淡出效果(0.8秒)"""
        global game_running, game_paused
        
        # 防止重复调用
        if not hasattr(back_to_start, 'is_running'):
            back_to_start.is_running = False
        if back_to_start.is_running:
            return
        back_to_start.is_running = True
            
        # 立即暂停游戏状态和清除画布
        game_running = False
        game_paused = True
        #canvas.delete("all")  # 清除所有画布内容
        
        # 取消所有pending的动画
        try:
            for after_id in window.tk.call('after', 'info'):
                try:
                    window.after_cancel(int(after_id))
                except ValueError:
                    continue
        except Exception as e:
            print(f" failed: {e}")
        
        # 40步 × 20ms = 800ms (0.8秒)
        alphas = [i/40 for i in range(40, -1, -1)]  # 从1.0到0.0,共41步
        current_step = 0
        
        def fade_step():
            nonlocal current_step
            try:
                if not window.winfo_exists():
                    cleanup_and_restart()
                    return
                    
                if current_step < len(alphas):
                    # 保持平滑的淡出动画效果
                    alpha = max(0.05, alphas[current_step])
                    if window.winfo_exists():
                        window.attributes('-alpha', alpha)
                        # 每次更新时重绘窗口内容,避免残影
                        window.update_idletasks()
                    current_step += 1
                    # 使用固定的20ms间隔保证动画流畅度
                    if window.winfo_exists():
                        window.after(20, fade_step)
                else:
                    cleanup_and_restart()
            except Exception as e:
                print(f"淡出动画出错: {str(e)}")
                cleanup_and_restart()
        
        def cleanup_and_restart():
            try:
                # 停止所有音频,使用淡出效果
                try:
                    if 'sound_manager' in globals():
                        sound_manager.cleanup()
                except Exception as e:
                    print(f" failed: {e}")
                    
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.fadeout(200)  # 音乐淡出时间增加到200ms
                        pygame.mixer.stop()
                except Exception as e:
                    print(f" failed: {e}")
                
                # 取消所有pending的after调用
                try:
                    if window.winfo_exists():
                        for after_id in window.tk.call('after', 'info'):
                            try:
                                window.after_cancel(int(after_id))
                            except (ValueError, tk.TclError):
                                continue
                except Exception as e:
                    print(f" failed: {e}")
                    
                # 清理画布和窗口内容
                try:
                    if window.winfo_exists():
                        canvas.delete("all")
                        # 强制更新画布避免残影
                        canvas.update_idletasks()
                        for widget in window.winfo_children():
                            widget.destroy()
                except Exception as e:
                    print(f" failed: {e}")
                    
                # 优雅地销毁当前窗口
                try:
                    if window.winfo_exists():
                        window.withdraw()  # 先隐藏窗口
                        window.update()
                        window.destroy()
                except Exception as e:
                    print(f"failed: {e}")
                    
                # 重置运行状态标记    
                back_to_start.is_running = False
                    
                # 创建新的开始页面,确保完全不透明且无残影
                start_page = StartPage()
                start_page.window.lift()
                start_page.window.focus_force()
                start_page.window.update_idletasks()  # 强制重绘
                start_page.window.mainloop()
                
            except Exception as e:
                print(f"返回主菜单时发生错误: {str(e)}")
                # 确保窗口被销毁
                try:
                    if window.winfo_exists():
                        window.destroy()
                except Exception as e:
                    print(f"failed: {e}")
                # 重置运行状态标记    
                back_to_start.is_running = False
                # 重新创建开始页面    
                start_page = StartPage()
                start_page.window.mainloop()
        
        # 开始淡出动画
        try:
            if window.winfo_exists():
                fade_step()  # 直接调用fade_step开始动画
            else:
                cleanup_and_restart()
        except Exception as e:
            print(f"启动淡出动画失败: {str(e)}")
            cleanup_and_restart()
    
    back_button = tk.Button(
        button_frame,
        text="Back",
        command=back_to_start,
        width=8,
        bg="#FF5722",
        fg="white",
        font=("Helvetica", 10, "bold"),
        relief="flat",
        borderwidth=0
    )
    # 创建圆角效果
    back_button.configure(highlightthickness=0)
    back_button.bind('<Map>', lambda e: e.widget.configure(relief="flat"))
    # 使用自定义样式类实现圆角
    back_button.configure(cursor="hand2")
    back_button.configure(bd=0, highlightthickness=0)
    back_button.configure(compound="center")
    # 应用圆角样式
    back_button.configure(padx=10)
    back_button.configure(pady=7.499999999)
    back_button.configure(borderwidth=0)
    back_button.configure(relief="ridge")
    back_button.pack(side=tk.LEFT, padx=5)
    back_button.bind("<Enter>", lambda e: back_button.config(bg="#FF8A65"))  # 浅橙色
    back_button.bind("<Leave>", lambda e: back_button.config(bg="#FF5722"))
    
    restart_button.bind("<Enter>", lambda e: restart_button.config(bg="#64B5F6"))  # 浅蓝色
    restart_button.bind("<Leave>", lambda e: restart_button.config(bg="#2196F3"))
    
    pause_button.bind("<Enter>", lambda e: pause_button.config(bg="#81C784"))  # 浅绿色
    pause_button.bind("<Leave>", lambda e: pause_button.config(bg="#4CAF50"))
    
    def draw_snake():
        # 使用渐变效果，从到尾颜色逐渐变化
        INTP = random.randint(0, 2)
        
        color_schemes = [
            [   # 第一组：梦幻晨曦组
                [   # 晨曦粉紫
                    "#FF80ED",  # 梦幻起始粉
                    "#FF50B8",  # 晨曦过渡粉
                    "#FF2087",  # 玫瑰魅色
                    "#FF00AA"   # 魅影终点色
                ],
                [   # 晨曦青蓝
                    "#80FFFF",  # 晶莹起始青
                    "#40E5FF",  # 碧海过渡色
                    "#00CCFF",  # 深海梦境色
                    "#00A8FF"   # 深邃终点色
                ],
                [   # 晨曦金色
                    "#FFE566",  # 晨光起始金
                    "#FFD700",  # 璀璨过渡金                
                    "#FFAD1F",  # 琥珀过渡色
                    "#FF9912"   # 落日终点色
                ]
            ],
            [   # 第二组：梦幻极光组（重新优化）
                [   # 梦幻紫罗
                    "#E680FF",  # 梦幻起始紫
                    "#D355FF",  # 极光过渡紫
                    "#B82AFF",  # 魅影紫霞
                    "#9900FF"   # 深邃紫梦
                ],
                [   # 梦幻青碧
                    "#80FFE6",  # 梦幻起始青
                    "#40FFD4",  # 极光碧波
                    "#00FFB8",  # 深海之梦
                    "#00E5A0"   # 碧波尽头
                ],
                [   # 梦幻翠绿
                    "#80FF9E",  # 梦幻嫩绿
                    "#40FF8A",  # 极光翠绿
                    "#00FF76",  # 翡翠之梦
                    "#00E562"   # 碧绿深邃
                ]
            ],
            [   # 第三组：赛博霓虹组（强对比版）
                [   # 等离子脉冲
                    "#FF5555",  # 等离子起始（明亮赛博红）
                    "#FF2222",  # 脉冲过渡
                    "#FF0000",  # 能量聚焦
                    "#CC0066"   # 核心迸发（深邃玫红）
                ],
                [   # 量子极光
                    "#DD66FF",  # 量子起始（通透量子紫）
                    "#BB33FF",  # 极光弧光
                    "#9900FF",  # 量子跃迁
                    "#7700CC"   # 虚空之境
                ],
                [   # 全息青焰
                    "#66FFFF",  # 全息起始（明亮赛博青）
                    "#33FFFF",  # 离子之光
                    "#00FFFF",  # 数据流束
                    "#00CCFF"   # 矩阵深邃
                ]
            ],
            [   # 第一组：梦幻星空
                [   # 星云幻彩
                    "#FF99FF",  # 星云粉紫
                    "#FF66FF",  # 星尘闪烁
                    "#FF33FF",  # 星际光芒
                    "#CC00FF"   # 深空魔力
                ],
                [   # 银河之流
                    "#99FFFF",  # 银河起点
                    "#66FFFF",  # 星河波动
                    "#33FFFF",  # 星际之流
                    "#00CCFF"   # 深空之渊
                ],
                [   # 恒星之光
                    "#FFFF99",  # 恒星光辉
                    "#FFFF66",  # 星光闪耀
                    "#FFFF33",  # 光芒万丈
                    "#FFCC00"   # 永恒之星
                ]
            ],
            [   # 第二组：霓虹都市
                [   # 霓虹之夜
                    "#FF6699",  # 霓虹玫瑰
                    "#FF3366",  # 城市脉动
                    "#FF0033",  # 都市之心
                    "#CC0033"   # 暗夜之魂
                ],
                [   # 电子光辉
                    "#66FF99",  # 电子光芒
                    "#33FF66",  # 数据流光
                    "#00FF33",  # 矩阵能量
                    "#00CC33"   # 科技深邃
                ],
                [   # 赛博之焰
                    "#FF9966",  # 赛博烈焰
                    "#FF6633",  # 数码燃烧
                    "#FF3300",  # 信息之火
                    "#CC3300"   # 核心之炎
                ]
            ],
            [   # 第三组：量子领域
                [   # 量子之舞
                    "#9999FF",  # 量子起点
                    "#6666FF",  # 虚拟律动
                    "#3333FF",  # 数据洪流
                    "#0000CC"   # 信息之海
                ],
                [   # 矩阵绿光
                    "#99FF99",  # 矩阵光束
                    "#66FF66",  # 程序之光
                    "#33FF33",  # 代码闪耀
                    "#00CC00"   # 系统之芯
                ],
                [   # 超维空间
                    "#FF9999",  # 维度之门
                    "#FF6666",  # 空间涟漪
                    "#FF3333",  # 现实折射
                    "#CC0000"   # 终极真理
                ]
            ]
        ]
        
        colors = color_schemes[color_chose][INTP]  # 随机选择一种颜色方案
        
        # 先制蛇身
        # 假设蛇身部分是由列表坐标组成，colors 是颜色列表
        block_size = 20  # 每个蛇身块的大小
        shadow_offset = 5  # 阴影偏移量

        def draw_segment(canvas, segment, color):
            """
            绘制蛇身方块,终极优化版本
            """
            # 直接使用列表索引,避免任何变量赋值和计算
            canvas.create_rectangle(
                segment[0], segment[1],
                segment[0] + 20, segment[1] + 20,
                fill=color,
                outline=""
            )

        def draw_snake(canvas, snake, colors):
            """
            批量绘制整条蛇,终极优化版本
            """
            # 预计算颜色列表长度,避免重复计算
            color_len = len(colors)
            
            # 使用列表推导式一次性生成所有绘图命令
            commands = [(
                segment[0], segment[1],
                segment[0] + 20, segment[1] + 20,
                colors[i % color_len]
            ) for i, segment in enumerate(snake[:-1])]
            
            # 批量执行所有绘图命令
            for x1, y1, x2, y2, color in commands:
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # 直接调用优化后的绘制函数
        draw_snake(canvas, snake, colors)


        
        # 单独处理蛇头
        head = snake[-1]
        head_color = colors[0]  # 使用第一个颜色作为基础头部颜色
        
        # 正常绘制蛇头
        canvas.create_rectangle(
            head[0], head[1],
            head[0] + 20, head[1] + 20,
            fill=head_color,
            outline=""
        )
        
        # 在蛇头上添加眼睛
        head = snake[-1]  # 蛇头是列表的最后一个元素
        # 根据蛇的方向调整眼睛位置
        if snake_direction == "Right":
            # 右眼
            canvas.create_oval(head[0] + 12, head[1] + 5, head[0] + 16, head[1] + 8, fill="#F8F8F8")
            canvas.create_oval(head[0] + 13, head[1] + 6, head[0] + 15, head[1] + 7, fill="#2196F3")
            # 左眼
            canvas.create_oval(head[0] + 12, head[1] + 12, head[0] + 16, head[1] + 15, fill="#F8F8F8")
            canvas.create_oval(head[0] + 13, head[1] + 13, head[0] + 15, head[1] + 14, fill="#2196F3")
            
        elif snake_direction == "Left":
            # 右眼
            canvas.create_oval(head[0] + 4, head[1] + 5, head[0] + 8, head[1] + 8, fill="#F8F8F8")
            canvas.create_oval(head[0] + 5, head[1] + 6, head[0] + 7, head[1] + 7, fill="#2196F3")
            # 左眼
            canvas.create_oval(head[0] + 4, head[1] + 12, head[0] + 8, head[1] + 15, fill="#F8F8F8")
            canvas.create_oval(head[0] + 5, head[1] + 13, head[0] + 7, head[1] + 14, fill="#2196F3")
            
        elif snake_direction == "Up":
            # 右眼
            canvas.create_oval(head[0] + 5, head[1] + 4, head[0] + 8, head[1] + 8, fill="#F8F8F8")
            canvas.create_oval(head[0] + 6, head[1] + 5, head[0] + 7, head[1] + 7, fill="#2196F3")
            # 左眼
            canvas.create_oval(head[0] + 12, head[1] + 4, head[0] + 15, head[1] + 8, fill="#F8F8F8")
            canvas.create_oval(head[0] + 13, head[1] + 5, head[0] + 14, head[1] + 7, fill="#2196F3")
            
        else:  # Down
            # 右眼
            canvas.create_oval(head[0] + 5, head[1] + 12, head[0] + 8, head[1] + 16, fill="#F8F8F8")
            canvas.create_oval(head[0] + 6, head[1] + 13, head[0] + 7, head[1] + 15, fill="#2196F3")
            # 左眼
            canvas.create_oval(head[0] + 12, head[1] + 12, head[0] + 15, head[1] + 16, fill="#F8F8F8")
            canvas.create_oval(head[0] + 13, head[1] + 13, head[0] + 14, head[1] + 15, fill="#2196F3")
    
    class Food:
        def __init__(self, position, food_type):
            self.position = position
            self.food_type = food_type
            # 不同食物的属性，调整了颜色使其更鲜明
            self.properties = {
                'normal': {
                    'color': '#FF0033',  # 更鲜艳的红色
                    'score': 1,
                    'effect': None,
                    'probability': 0.60
                },
                'golden': {
                    'color': '#FFD700',  # 更明亮的金色
                    'score': 3,
                    'effect': 'speed_up',
                    'probability': 0.235
                },
                'special': {
                    'color': '#9400D3',  # 更深邃的紫色
                    'score': 5,
                    'effect': 'slow_down',
                    'probability': 0.10
                },
                'rainbow': {
                    'color': '#FF1493',
                    'score': 10,
                    'effect': 'rainbow',
                    'probability': 0.055
                },
                'star_candy': {
                    'color': '#FFD700',
                    'score': 6,
                    'effect': 'star_candy',
                    'probability': 0.015
                }
            }
            
            # 彩色糖果的颜色列表
            self.rainbow_colors = [
                '#FF1493',  # 亮粉红 - 甜蜜的草莓味
                '#FF69B4',  # 粉红色 - 柔和的樱桃味
                '#00FFFF',  # 青色 - 清爽的薄荷味
                '#1E90FF',  # 道奇蓝 - 清凉的蓝莓味
                '#9370DB',  # 中紫色 - 浪漫的葡萄味
                '#FF6EB4',  # 热粉红 - 可爱的树莓味
                '#40E0D0'   # 绿松石色 - 清新的薄荷味
            ]
            self.color_index = 0
    
    def generate_food():
        nonlocal food  
        new_position = (random.randint(0, 19) * 20, random.randint(0, 19) * 20)
        while new_position in snake:
            new_position = (random.randint(0, 19) * 20, random.randint(0, 19) * 20)
        
        # 使用权重随机选择食物类型
        food_types = ['normal', 'golden', 'special', 'rainbow', 'star_candy']
        weights = [0.59, 0.240, 0.10, 0.055, 0.015]  # 概率权重
        
        # 使用random.choices进行加权随机选择
        food_type = random.choices(
            food_types,
            weights=weights,
            k=1
        )[0]
        
        food = Food(new_position, food_type)
    
    def draw_food():
        if not food:
            return
        
        x, y = food.position
        base_color = food.properties[food.food_type]['color']
        
        # 使用更温和的明暗变化参数：
        # - 使用较慢的变化速度(2)
        # - 使用适中的振幅(0.2)
        # - 使用较高的基础亮度(0.8)
        glow = abs(math.sin(time.time() * 2)) * 0.2 + 0.8
        
        # 调整颜色亮度
        def adjust_color(hex_color, factor):
            # 将颜色转换RGB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # 调整亮度
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            return f'#{r:02x}{g:02x}{b:02x}'
        
        # 获取当前颜色
        current_color = adjust_color(base_color, glow)
        
        # 据食物类型绘制不同形状
        if food.food_type == 'normal':
            # 普通食物：方块
            canvas.create_rectangle(
                x, y, x + 20, y + 20,
                fill=current_color,
                outline=""
            )
        elif food.food_type == 'golden':
            # 金色食物：圆
            canvas.create_oval(
                x, y, x + 20, y + 20,
                fill=current_color,
                outline=""
            )
        elif food.food_type == 'special':  # special
            # 特殊食物：菱形
            canvas.create_polygon(
                x + 10, y,      # 上
                x + 20, y + 10, # 右
                x + 10, y + 20, # 下
                x, y + 10,      # 左
                fill=current_color,
                outline=""
            )
        elif food.food_type == 'rainbow':
                # 绘制糖果形状
                # 糖果主体(两个圆形)
            # 主体圆形部分(稍微调整位置和大小)
            canvas.create_oval(
                x + 5, y + 3,  
                x + 15, y + 13,  
                fill=food.rainbow_colors[food.color_index],
                outline=""
            )
            canvas.create_oval(
                x + 5, y + 7,
                x + 15, y + 17,
                fill=food.rainbow_colors[(food.color_index + 1) % len(food.rainbow_colors)],
                outline=""
            )

            # 包装纸褶皱效果增强
            # 左侧包装纸 - 多层次设计
            canvas.create_polygon(
                x + 2, y + 5,    # 外尖
                x + 4, y + 7,    # 内上
                x + 5, y + 10,   # 内中
                x + 4, y + 13,   # 内下
                x + 2, y + 15,   # 外尖
                fill=food.rainbow_colors[(food.color_index + 2) % len(food.rainbow_colors)],
                outline=""
            )

            # 左侧内层褶皱
            canvas.create_polygon(
                x + 3, y + 7,    # 内尖上
                x + 4.5, y + 8,  # 褶皱上
                x + 5, y + 10,   # 中点
                x + 4.5, y + 12, # 褶皱下
                x + 3, y + 13,   # 内尖下
                fill=food.rainbow_colors[(food.color_index + 3) % len(food.rainbow_colors)],
                stipple='gray50',
                outline=""
            )

            # 右侧包装纸 - 对称的多层次设计
            canvas.create_polygon(
                x + 18, y + 5,   # 外尖
                x + 16, y + 7,   # 内上
                x + 15, y + 10,  # 内中
                x + 16, y + 13,  # 内下
                x + 18, y + 15,  # 外尖
                fill=food.rainbow_colors[(food.color_index + 2) % len(food.rainbow_colors)],
                outline=""
            )

            # 右侧内层褶皱
            canvas.create_polygon(
                x + 17, y + 7,   # 内尖上
                x + 15.5, y + 8, # 褶皱上
                x + 15, y + 10,  # 中点
                x + 15.5, y + 12,# 褶皱下
                x + 17, y + 13,  # 内尖下
                fill=food.rainbow_colors[(food.color_index + 3) % len(food.rainbow_colors)],
                stipple='gray50',
                outline=""
            )

            # 包装纸光泽效果
            # 左侧高光
            canvas.create_line(
                x + 3, y + 7,
                x + 4, y + 10,
                x + 3, y + 13,
                fill="white",
                width=1,
                stipple='gray25'
            )

            # 右侧高光
            canvas.create_line(
                x + 17, y + 7,
                x + 16, y + 10,
                x + 17, y + 13,
                fill="white",
                width=1,
                stipple='gray25'
            )

            # 糖果表面点缀
            # 上部光点
            canvas.create_oval(
                x + 9, y + 5,
                x + 11, y + 7,
                fill="white",
                stipple='gray50',
                outline=""
            )

            # 下部光点
            canvas.create_oval(
                x + 9, y + 13,
                x + 11, y + 15,
                fill="white",
                stipple='gray50',
                outline=""
            )
                            
            # 更新颜色索引使糖果变色
            food.color_index = (food.color_index + 1) % len(food.rainbow_colors)
        elif food.food_type == 'star_candy':
            center_x, center_y = x + 10, y + 10
            size = 30
            
            # 计算五角星的点
            points = []
            num_points = 180  # 增加点的数量使曲线更平滑
            for i in range(num_points):
                # 使用参数方程计算花瓣曲线
                angle = (2 * math.pi * i / num_points) - math.pi / 2
                # r = a + b*sin(nθ) 其中:
                # - a 是基础半径
                # - b 是振幅
                # - n 是花瓣数(这里是5)
                r = (size/4) * (1 + math.sin(5 * angle))  # 调整size/4来控制整体大小
                
                points.extend([
                    center_x + r * math.cos(angle),
                    center_y + r * math.sin(angle)
                ])
            
            t = time.time()
            r = int(128 + 127 * math.sin(t * 2.0))
            g = int(128 + 127 * math.sin(t * 2.0 + 2.0))
            b = int(128 + 127 * math.sin(t * 2.0 + 4.0))
            dynamic_color = f'#{r:02x}{g:02x}{b:02x}'
            
            # 绘制五角星
            canvas.create_polygon(
                points,
                fill=dynamic_color,  # 使用动态颜色
                outline=''
            )
    class StarParticle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.size = random.randint(10, 15)
            self.angle = random.uniform(0, math.pi * 2)
            self.speed = random.uniform(2, 4)
            self.rotation = random.uniform(0, math.pi * 2)
            self.rotation_speed = random.uniform(-0.1, 0.1)
            self.alpha = 1.0
            # 使用预定义的颜色列表以提高性能
            self._colors = (
                "#FFD700", "#FFC125", "#FFE4B5", 
                "#FFDF00", "#FFB90F"
            )
            self.color = random.choice(self._colors)
            # 使用deque优化轨迹存储
            self.trail = deque(maxlen=5)

        def move(self):
            # 使用append而不是列表操作
            self.trail.append((self.x, self.y))
            
            # 使用预计算的三角函数值
            cos_angle = math.cos(self.angle)
            sin_angle = math.sin(self.angle)
            self.x += cos_angle * self.speed
            self.y += sin_angle * self.speed
            
            # 更新状态
            self.rotation += self.rotation_speed
            self.speed *= 0.98
            self.alpha -= 0.02
            return self.alpha > 0

        def draw(self, canvas):
            if self.alpha <= 0:
                return
                
            # 优化轨迹绘制
            trail_length = len(self.trail)
            if trail_length > 0:
                for i, (trail_x, trail_y) in enumerate(self.trail):
                    trail_alpha = (i / trail_length) * self.alpha
                    if trail_alpha > 0.1:
                        trail_size = self.size * 0.5 * trail_alpha
                        canvas.create_oval(
                            trail_x - trail_size, trail_y - trail_size,
                            trail_x + trail_size, trail_y + trail_size,
                            fill=self.color,
                            stipple='gray50',
                            outline=""
                        )
            
            # 预计算五角星点
            points = []
            for i in range(5):
                angle = self.rotation + (2 * math.pi * i / 5)
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
                
                # 外部点
                points.extend([
                    self.x + cos_angle * self.size,
                    self.y + sin_angle * self.size
                ])
                
                # 内部点
                angle += math.pi / 5
                inner_size = self.size * 0.4
                points.extend([
                    self.x + math.cos(angle) * inner_size,
                    self.y + math.sin(angle) * inner_size
                ])
            
            # 优化星星绘制
            canvas.create_polygon(
                points,
                fill=self.color,
                outline="white" if self.alpha > 0.7 else "",
                width=1,
                stipple='gray50' if self.alpha < 0.5 else ''
            )
    
    # 在 move_snake 函数之前添加
    class CelebrationFirework:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.particles = []
            # 使用更丰富的渐变色彩
            self.colors = [
                "#FFD700", "#FFA500", "#FF69B4", "#FF1493",  # 金色到粉色渐变
                "#4169E1", "#1E90FF", "#00BFFF", "#87CEEB",  # 蓝色系渐变
                "#32CD32", "#98FB98", "#00FF7F", "#3CB371",  # 绿色系渐变
                "#FF4500", "#FF6347", "#FF7F50", "#FFA07A",  # 橙红系渐变
                "#9370DB", "#8A2BE2", "#9400D3", "#BA55D3"   # 紫色系渐变
            ]
            self.create_particles()
            
        def create_particles(self):
            # 预计算一些常用值
            TWO_PI = 2 * math.pi
            base_x, base_y = self.x, self.y
            
            # 创建基础粒子参数
            base_particle = {
                'x': base_x,
                'y': base_y,
                'alpha': 1.0
            }
            
            # 预计算角度和速度范围
            main_angles = [random.uniform(0, TWO_PI) for _ in range(100)]
            main_speeds = [random.uniform(4, 10) for _ in range(100)]
            trail_angles = [random.uniform(0, TWO_PI) for _ in range(20)]
            trail_speeds = [random.uniform(2, 5) for _ in range(20)]
            
            # 批量创建主要爆炸效果粒子
            for angle, speed in zip(main_angles, main_speeds):
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
                dx = cos_angle * speed
                dy = sin_angle * speed
                
                particle = base_particle.copy()
                particle.update({
                    'dx': dx,
                    'dy': dy,
                    'color': random.choice(self.colors),
                    'size': random.uniform(2, 6),
                    'type': 'main',
                    'sparkle_timer': random.uniform(0, math.pi)
                })
                self.particles.append(particle)
            
            # 批量创建星光轨迹粒子
            for angle, speed in zip(trail_angles, trail_speeds):
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
                dx = cos_angle * speed
                dy = sin_angle * speed
                
                particle = base_particle.copy()
                particle.update({
                    'dx': dx,
                    'dy': dy,
                    'color': random.choice(self.colors),
                    'size': random.uniform(3, 8),
                    'type': 'trail',
                    'trail': []
                })
                self.particles.append(particle)

        def update_and_draw(self, canvas):
            canvas.delete("celebration_firework")
            alive_particles = []
            
            # 预计算重力和透明度衰减
            MAIN_GRAVITY = 0.15
            TRAIL_GRAVITY = 0.08
            MAIN_ALPHA_DECAY = 0.013
            TRAIL_ALPHA_DECAY = 0.01
            
            for p in self.particles:
                # 更新位置
                p['x'] += p['dx']
                p['y'] += p['dy']
                
                if p['type'] == 'main':
                    p['dy'] += MAIN_GRAVITY
                    p['alpha'] -= MAIN_ALPHA_DECAY
                    p['sparkle_timer'] += 0.2
                    
                    if p['alpha'] > 0.1:
                        alive_particles.append(p)
                        # 一次性计算所有需要的值
                        sparkle = math.sin(p['sparkle_timer']) * 0.3 + 0.7
                        size = p['size'] * p['alpha'] * sparkle
                        x, y = p['x'], p['y']
                        size_1_5 = size * 1.5
                        color = p['color']
                        
                        # 批量绘制
                        canvas.create_oval(
                            x - size_1_5, y - size_1_5,
                            x + size_1_5, y + size_1_5,
                            fill=color,
                            outline='',
                            tags="celebration_firework",
                            stipple='gray25'
                        )
                        canvas.create_oval(
                            x - size, y - size,
                            x + size, y + size,
                            fill=color,
                            outline='white' if p['alpha'] > 0.8 else '',
                            tags="celebration_firework"
                        )
                
                elif p['type'] == 'trail':
                    p['dy'] += TRAIL_GRAVITY
                    p['alpha'] -= TRAIL_ALPHA_DECAY
                    
                    # 使用列表推导式更新轨迹
                    p['trail'].append((p['x'], p['y']))
                    if len(p['trail']) > 10:
                        p['trail'] = p['trail'][-10:]
                    
                    if p['alpha'] > 0.1:
                        alive_particles.append(p)
                        trail_len = len(p['trail'])
                        base_width = p['size'] * p['alpha']
                        color = p['color']
                        
                        # 使用zip优化轨迹绘制
                        for i, (p1, p2) in enumerate(zip(p['trail'][:-1], p['trail'][1:])):
                            ratio = i / trail_len
                            canvas.create_line(
                                p1[0], p1[1], p2[0], p2[1],
                                fill=color,
                                width=base_width * ratio,
                                tags="celebration_firework",
                                capstyle=tk.ROUND
                            )
            
            self.particles = alive_particles
            return bool(alive_particles)

    def show_celebration_firework():
        firework = CelebrationFirework(200, 150)
        
        def animate_firework():
            if game_running and firework.update_and_draw(canvas):
                window.after(16, animate_firework)
        
        # 播放烟花音效
        try:
            firework_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets", "music", "firework.wav"))
            firework_sound.play()
        except Exception as e:  # 添加了异常处理
            print(f"无法播放烟花音效: {e}")
        
        animate_firework()
    
    def move_snake():
        nonlocal snake, food, game_running, current_score, snake_speed
        if game_paused or not game_running:
            return
            
        head_x, head_y = snake[-1]
        if snake_direction == "Up":
            new_head = (head_x, head_y - 20)
        elif snake_direction == "Down":
            new_head = (head_x, head_y + 20)
        elif snake_direction == "Left":
            new_head = (head_x - 20, head_y)
        elif snake_direction == "Right":
            new_head = (head_x + 20, head_y)
            
        # 处理穿墙逻辑
        global Game_Mode
        if Game_Mode == "Pass":  # 可以穿墙
            # 如果超出边界,从对面出现
            new_head = (
                new_head[0] % 400,  # x坐标取余
                new_head[1] % 400   # y坐标取余
            )
        
        # 检查是否撞到墙壁或自己
        if new_head in snake or (
            Game_Mode == "Forbid" and (  # 不能穿墙时才检查边界
                new_head[0] < 0 or 
                new_head[0] >= 400 or 
                new_head[1] < 0 or 
                new_head[1] >= 400
            )
        ):
            game_running = False
            
            # 只在条件模式下停止音乐
            if music_mode == "conditional":
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            
            # 创建死亡动画
            stars = [StarParticle(head_x + 10, head_y + 10) for _ in range(5)]
            
            def animate_death():
                nonlocal stars
                canvas.delete("all")  # 删除所有元素
                canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
                sound_manager.play('death')
                
                # 继续绘制蛇的最后一帧
                draw_snake()  # 保持蛇的图像
                
                # 更新和绘制星星
                new_stars = []
                for star in stars:
                    if star.move():
                        star.draw(canvas)
                        new_stars.append(star)
                stars = new_stars
                
                # 只有在所有星星消失后才开始粒子特效
                if not stars:
                    # 创建死亡粒子效果
                    death_particles = []
                    colors = [
                        "#FF1493", "#FF69B4", "#FFB6C1",  # 梦幻糖果粉（甜美梦境）
                        "#FFD700", "#FFC125", "#FFE4B5",  # 皇室尊贵金（奢华璀璨）
                        "#00FFFF", "#40E0D0", "#7FFFD4",  # 海洋之心蓝（深邃神秘）
                        "#9932CC", "#BA55D3", "#DDA0DD",  # 魔法星空紫（浪漫迷离）
                        "#32CD32", "#98FB98", "#90EE90",  # 生命翡翠绿（自然灵动）
                        "#FF4500", "#FF6347", "#FFA07A",  # 熔岩之光橙（热情似火）
                        "#FF0033", "#FF3366", "#FF6699",  # 玫瑰之恋红（浪漫绽放）
                        "#00FA9A", "#00FF7F", "#7CCD7C",  # 春之精灵绿（生机盎然）
                        "#4169E1", "#1E90FF", "#87CEEB",  # 深海宝石蓝（深邃优雅）
                        "#9400D3", "#8A2BE2", "#9370DB",  # 暮光魔法紫（神秘梦幻）
                    ]
                    
                    for segment in snake:
                        for _ in range(12):  # 每个蛇段生成12个粒子
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(3, 6)
                            color = random.choice(colors)
                            death_particles.append({
                                'x': segment[0] + 10,
                                'y': segment[1] + 10,
                                'angle': angle,
                                'speed': speed,
                                'color': color,
                                'size': random.uniform(3, 6),
                                'alpha': 1.0,
                                'type': random.choice(['circle', 'star', 'spark'])
                            })
                    
                    def update_death_particles():
                        nonlocal death_particles
                        canvas.delete("all")  # 清除所有元素
                        canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
                        
                        # 重新绘制蛇
                        draw_snake()
                        
                        # 显示长度和分数
                        def create_glowing_text(x, y, text, main_color="#FFD700", glow_color="#FFA500"):
                            # 外发光效果
                            for offset in range(1, 3):
                                canvas.create_text(
                                    x, y,
                                    text=text,
                                    fill=glow_color,
                                    font=("Impact", 16),
                                    activefill="#FFFFFF"
                                )
                            # 主文本
                            canvas.create_text(
                                x, y,
                                text=text,
                                fill=main_color,
                                font=("Impact", 16)
                            )
                            
                        create_glowing_text(50, 20, f"Length: {len(snake)}")
                        create_glowing_text(180, 20, f"Score: {current_score}")
                        
                        new_particles = []
                        for p in death_particles:
                            p['x'] += math.cos(p['angle']) * p['speed']
                            p['y'] += math.sin(p['angle']) * p['speed']
                            p['speed'] *= 0.94
                            p['size'] *= 0.96
                            p['alpha'] -= 0.015
                            
                            if p['size'] > 0.5:
                                new_particles.append(p)
                                
                                if p['type'] == 'circle':
                                    # 发光效果
                                    glow_size = p['size'] * 1.8
                                    canvas.create_oval(
                                        p['x'] - glow_size, p['y'] - glow_size,
                                        p['x'] + glow_size, p['y'] + glow_size,
                                        fill="",
                                        outline=p['color'],
                                        width=1,
                                        stipple='gray50'
                                    )
                                    
                                    # 主粒子
                                    canvas.create_oval(
                                        p['x'] - p['size'], p['y'] - p['size'],
                                        p['x'] + p['size'], p['y'] + p['size'],
                                        fill=p['color'],
                                        outline=""
                                    )
                                
                                elif p['type'] == 'star':
                                    points = []
                                    for i in range(5):
                                        angle = math.radians(i * 72)
                                        points.extend([
                                            p['x'] + math.cos(angle) * p['size'],
                                            p['y'] + math.sin(angle) * p['size']
                                        ])
                                    canvas.create_polygon(
                                        points,
                                        fill=p['color'],
                                        outline=""
                                    )
                                
                                else:  # spark
                                    end_x = p['x'] + math.cos(p['angle']) * p['size'] * 2
                                    end_y = p['y'] + math.sin(p['angle']) * p['size'] * 2
                                    canvas.create_line(
                                        p['x'], p['y'],
                                        end_x, end_y,
                                        fill=p['color'],
                                        width=2
                                    )
                        
                        death_particles = new_particles
                        if death_particles:
                            window.after(16, update_death_particles)
                        else:
                            # 清除画布，重绘背景和蛇
                            canvas.delete("all")
                            canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
                            draw_snake()
                            
                            # 显示游戏结束文本（不显示长度和分数）
                            high_score = load_high_score()
                            if current_score > high_score:
                                save_high_score(current_score)
                                # 清除画布上的所有元素
                                canvas.delete("all")
                                canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
                                
                                def create_elegant_effect(frame=0, max_frames=180):
                                    if frame < max_frames:
                                        progress = frame / max_frames
                                        
                                        # 预计算常用值
                                        center_x, center_y = 200, 60
                                        
                                        # 闪烁光晕效果 - 使用预计算的sin值
                                        sin_val = math.sin(frame * 0.1)
                                        glow_radius = 50 + sin_val * 5
                                        glow_alpha = int(128 * (1 - progress))
                                        glow_color = f"#{glow_alpha:02x}FFD7"
                                        
                                        # 批量创建图形
                                        items = []
                                        
                                        # 光晕
                                        items.append(('oval', (
                                            center_x - glow_radius, center_y - glow_radius,
                                            center_x + glow_radius, center_y + glow_radius,
                                            glow_color, ""
                                        )))
                                        
                                        # NEW RECORD 标题
                                        if frame > 20:
                                            fade_in = min(1.0, (frame - 20) / 30)
                                            text_color = f"#{int(255*fade_in):02x}FFFF"
                                            items.append(('text', (
                                                center_x, center_y, "NEW RECORD",
                                                text_color, "#FFD700", ("Helvetica", 32, "bold")
                                            )))
                                        
                                        # 动态分割线
                                        if frame > 40:
                                            line_progress = min(1.0, (frame - 40) / 40)
                                            half_width = 80 * line_progress  # 直接计算半宽度,避免重复计算
                                            y_base = 85  # 基准y坐标
                                            
                                            # 一次性计算x坐标
                                            x1 = center_x - half_width
                                            x2 = center_x + half_width
                                            
                                            items.extend([
                                                ('line', (x1, y_base - 1, x2, y_base - 1, "#FFD700", 1)),
                                                ('line', (x1, y_base + 1, x2, y_base + 1, "#FFD700", 1))
                                            ])
                                        
                                        # 分数显示
                                        if frame > 60:
                                            # 预先计算常用值
                                            score_scale = min(1.0, (frame - 60) / 20)
                                            font_size = int(42 * score_scale)
                                            score_text = f"{current_score:,}"
                                            font = ("Arial Black", font_size, "bold")
                                            y_pos = 120
                                            
                                            # 阴影偏移量预先定义
                                            shadow_offsets = ((2,2), (1,1), (-1,-1), (-2,-2))
                                            
                                            # 批量添加阴影文本
                                            shadow_items = [('text', (
                                                center_x + offset_x, y_pos + offset_y,
                                                score_text, "#000000", None, font
                                            )) for offset_x, offset_y in shadow_offsets]
                                            items.extend(shadow_items)
                                            
                                            # 添加主体文本
                                            text_items = [
                                                ('text', (center_x, y_pos, score_text, color, None, font))
                                                for color in ("#FFFFFF", "#FFD700")
                                            ]
                                            items.extend(text_items)
                                            
                                            # 每4帧添加一次粒子
                                            if frame % 4 == 0:
                                                # 预定义x轴范围
                                                x_ranges = [(120,160), (240,280)]
                                                particle_x = random.randint(*random.choice(x_ranges))
                                                particle_y = y_pos + random.randint(-20, 20)
                                                particle_size = random.randint(2, 4)
                                                
                                                # 计算粒子坐标
                                                p_coords = (
                                                    particle_x - particle_size,
                                                    particle_y - particle_size,
                                                    particle_x + particle_size,
                                                    particle_y + particle_size
                                                )
                                                items.append(('oval', (*p_coords, "#FFFACD", "")))
                                        
                                        # 批量绘制所有图形
                                        for item_type, args in items:
                                            if item_type == 'oval':
                                                x1,y1,x2,y2,fill,outline = args
                                                canvas.create_oval(x1,y1,x2,y2,fill=fill,outline=outline)
                                            elif item_type == 'text':
                                                x,y,text,fill,activefill,font = args
                                                canvas.create_text(x,y,text=text,fill=fill,activefill=activefill,font=font)
                                            elif item_type == 'line':
                                                x1,y1,x2,y2,fill,width = args
                                                canvas.create_line(x1,y1,x2,y2,fill=fill,width=width,capstyle=tk.ROUND)
                                        
                                        window.after(20, lambda: create_elegant_effect(frame + 1))
                                
                                # 启动优雅特效
                                create_elegant_effect()
                                def show_celebration(count=0):
                                    if count >= 3:  # 只循环三次
                                        return
                                    
                                    firework = CelebrationFirework(200, 150)
                                    def animate_firework():
                                        if firework.update_and_draw(canvas):
                                            window.after(16, animate_firework)
                                    animate_firework()
                                    
                                    # 播放烟花音效
                                    try:
                                        firework_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets", "music", "firework.wav"))
                                        firework_sound.play()
                                    except Exception as e:
                                        print(f"Sound play failed: {e}")
                                    
                                    # 第一次和第二次间隔1.8s,第二次和第三次间隔3s
                                    if count == 0:
                                        window.after(1800, lambda: show_celebration(count + 1))
                                    elif count == 1:
                                        window.after(3100, lambda: show_celebration(count + 1))
                                
                                # 开始第一次烟花
                                show_celebration()
                            def blink_game_over_text():
                                # 使用正弦函数创造梦幻效果
                                t = time.time()
                                # 第一行文字波动范围 0.87-1.0
                                wave1 = math.sin(t * 3.0) * 0.065 + 0.935  # (0.87 到 1.0)
                                # 第二行文字波动范围 0.95-1.0
                                wave2 = math.sin(t * 3.0) * 0.025 + 0.975  # (0.95 到 1.0)
                                
                                # 删除旧文字
                                canvas.delete("game_over_text")
                                
                                # 第一行文字使用原始粉色,但保持高亮度
                                base_r, base_g, base_b = 255, 64, 129  # #FF4081的RGB值
                                r = max(0, min(255, int(base_r * wave1)))
                                g = max(0, min(255, int(base_g * wave1)))
                                b = max(0, min(255, int(base_b * wave1)))
                                
                                color = f"#{r:02x}{g:02x}{b:02x}"
                                
                                canvas.create_text(
                                    200, 200,
                                    text="Yanami Anna かわい!",
                                    fill=color,
                                    font=("Impact", 24),
                                    tags="game_over_text"
                                )
                                
                                # 第二行文字使用明亮的白色
                                white_value = int(255 * wave2)
                                restart_color = f"#{white_value:02x}{white_value:02x}{white_value:02x}"
                                
                                canvas.create_text(
                                    200, 250,
                                    text="Press R to restart",
                                    fill=restart_color,
                                    font=("Impact", 18),
                                    tags="game_over_text"
                                )
                                
                                # 降低刷新率到10fps以进一步减少资源占用
                                window.after(100, blink_game_over_text)  # 约10fps
                            window.unbind("<Left>")
                            window.unbind("<Right>")
                            window.unbind("<Up>")
                            window.unbind("<Down>")
                            window.bind("<Left>", lambda e: move_window("Left"))
                            window.bind("<Right>", lambda e: move_window("Right")) 
                            window.bind("<Up>", lambda e: move_window("Up"))
                            window.bind("<Down>", lambda e: move_window("Down"))
                            # 开始闪烁动画
                            blink_game_over_text()
                    
                    update_death_particles()
                else:
                    # 在星星动画过程中显示长度和分数
                    canvas.create_text(
                        50, 20,
                        text=f"Length: {len(snake)}",
                        fill="#FFD700",
                        font=("Impact", 16)
                    )
                    canvas.create_text(
                        180, 20,
                        text=f"Score: {current_score}",
                        fill="#FFD700",
                        font=("Impact", 16)
                    )
                    window.after(20, animate_death)
            
            animate_death()
            return

        snake.append(new_head)
        
        # 检查是否吃到食物
        if food and new_head == food.position:
            # 播放吃食物音效
            sound_manager.play('eat')
            nonlocal color_chose
            # 创建食物效果
            create_food_effect(food.position[0], food.position[1], food.food_type)
            
            score_increase = food.properties[food.food_type]['score']
            current_score += score_increase
            
            effect = food.properties[food.food_type]['effect']
            if effect == 'speed_up':
                snake_speed = max(78, snake_speed - 10)
                #show_effect_message('speed_up')
            elif effect == 'slow_down':
                snake_speed = min(150, snake_speed + 10)
                #show_effect_message('slow_down')
            elif effect == 'rainbow':
                snake_speed = min(150, snake_speed + 5)
                nr = color_chose
                color_chose = random.randint(0, 5)  # 随机切换颜色方案
                #print("COLORRRRRRRR")
                while nr == color_chose:
                    color_chose = random.randint(0, 5)  # 随机切换颜色方案
            elif effect == 'star_candy':
                try:
                    snake_speed = min(150, snake_speed + 2)
                    nonlocal background_images, selected_bg, bg_image_path, bg_image, image, canvas
                    
                    # 保存当前背景以避免重复选择
                    current_bg = selected_bg
                    available_bgs = [bg for bg in background_images if bg != current_bg]
                    
                    # 从剩余背景中随机选择
                    selected_bg = random.choice(available_bgs)
                    bg_image_path = os.path.join(current_dir, "assets", "images", selected_bg)
                    
                    # 使用 with 语句确保文件正确关闭
                    with Image.open(bg_image_path) as img:
                        # 使用 LANCZOS 重采样进行高质量缩放
                        image = img.resize((400, 400), Image.LANCZOS)
                        bg_image = ImageTk.PhotoImage(image)
                    
                    # 清除画布并设置新背景
                    canvas.delete("all")
                    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
                    
                    # 保持对背景图片的引用以防止垃圾回收
                    canvas.bg_image = bg_image
                    
                    # 播放背景切换音效（如果有）
                    try:
                        sound_manager.play('background_change')
                    except Exception as e:
                        print(f"Sound play failed: {e}")

                        
                except Exception as e:
                    print(f"背景切换失败: {str(e)}")
                    # 如果切换失败，保持原有背景
                    canvas.create_image(0, 0, anchor=tk.NW, image=canvas.bg_image)
            generate_food()
        else:
            snake.pop(0)
            
        # 重绘所有内容
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
        draw_snake()
        draw_food()
        draw_score()
        
        # 更新粒子效果
        update_particles()
        
        #使用单一计时器和帧计数实现平滑移动
        if game_running:
            step = snake_speed // 20  # 从16份改为20份，追求极致平滑
            window.after(step, lambda: 
                window.after(step, lambda: 
                    window.after(step, lambda: 
                        window.after(step, lambda:
                            window.after(step, lambda:
                                window.after(step, lambda:
                                    window.after(step, lambda:
                                        window.after(step, lambda:
                                            window.after(step, lambda:
                                                window.after(step, lambda:
                                                    window.after(step, lambda:
                                                        window.after(step, lambda:
                                                            window.after(step, lambda:
                                                                window.after(step, lambda:
                                                                    window.after(step, lambda:
                                                                        window.after(step, lambda:
                                                                            window.after(step, lambda:
                                                                                window.after(step, lambda:
                                                                                    window.after(step, move_snake)))))))))))))))))))

    
    def change_direction(new_direction):
        global last_direction_change_time
        current_time = time.time()
        print(current_time - last_direction_change_time)
        # 检查时间间隔
        if current_time - last_direction_change_time < direction_change_interval:
            nonlocal snake
                # 获取蛇头位置和方向    
            head_x, head_y = snake[-1]
            if new_direction == "Up":
                new_head_ = (head_x, head_y - 20)
            elif new_direction == "Down":
                new_head_ = (head_x, head_y + 20)
            elif new_direction == "Left":
                new_head_ = (head_x - 20, head_y)
            elif new_direction == "Right":
                new_head_ = (head_x + 20, head_y)
                
            # 处理穿墙逻辑
            global Game_Mode
            if Game_Mode == "Pass":  # 可以穿墙
                # 如果超出边界,从对面出现
                new_head_ = (
                    new_head_[0] % 400,  # x坐标取余
                    new_head_[1] % 400   # y坐标取余
                )
            if new_head_ in snake:
                return
        nonlocal snake_direction
        if new_direction == snake_direction:
            return
        if new_direction == "Up" and snake_direction != "Down":
            snake_direction = "Up"
            last_direction_change_time = current_time
        elif new_direction == "Down" and snake_direction != "Up":
            snake_direction = "Down"
            last_direction_change_time = current_time
        elif new_direction == "Left" and snake_direction != "Right":
            snake_direction = "Left"
            last_direction_change_time = current_time
        elif new_direction == "Right" and snake_direction != "Left":
            snake_direction = "Right"
            last_direction_change_time = current_time
    
    def draw_score():
        snake_length = len(snake)
        
        # 使用时间创建微妙的颜色渐变
        t = time.time()
        # 预计算一些常用值
        sin_value = math.sin(t * 2)
        color_value = int(243 + 12 * sin_value)  # 减小渐变范围到235-255
        color_value_80 = int(color_value * 0.8)
        dynamic_gold = f"#{color_value:02x}{color_value_80:02x}00"
        
        # 复用文本内容
        length_text = f"Length: {snake_length}"
        score_text = f"Score: {current_score}"
        
        # 使用常量减少重复创建
        FONT = ("Impact", 16)
        BLACK = "black"
        
        # 显示Length和Score,添加柔和阴影
        for text, x in ((length_text, 50), (score_text, 180)):
            # 阴影
            canvas.create_text(
                x+1, 21,
                text=text,
                fill=BLACK,
                font=FONT,
                state="disabled"
            )
            # 主文本
            canvas.create_text(
                x, 20,
                text=text,
                fill=dynamic_gold,
                font=FONT
            )
        
        # 如果戏暂停，显示停文本
        if game_paused:
            def blink_text():
                if game_paused:  # 只在暂停状态下继续闪烁
                    # 使用正弦函数创造梦幻效果
                    t = time.time() 
                    wave = math.sin(t * 3.0) * 0.5 + 0.5  # 0.0 到 1.0
                    
                    # 扩大红色范围的变化
                    r = int(200 + wave * 55)  # 200-255
                    g = int(20 + wave * 70)   # 20-90
                    b = int(80 + wave * 70)   # 80-150
                    
                    # 确保颜色值在有效范围内
                    r = min(255, max(0, r))
                    g = min(255, max(0, g))
                    b = min(255, max(0, b))
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    # 删除旧文字
                    canvas.delete("pause_text")
                    
                    # 创建新文字
                    canvas.create_text(
                        200, 200,
                        text="PAUSED",
                        fill=color,
                        font=("Impact", 24),
                        tags="pause_text"
                    )
                    
                    # 提高刷新率获得更平滑效果
                    canvas.after(16, blink_text)  # 约60fps
            
            # 开始闪烁动画
            blink_text()
    def handle_click(event):
        """处理鼠标点击改变方向"""
        nonlocal snake_direction
        
        if game_paused:
            return
            
        head_x, head_y = snake[-1]  # 修正:使用snake[-1]获取蛇头
        # 每个蛇身块是20x20,所以中心点要加10
        head_center_x = head_x + 10  # 20/2 = 10
        head_center_y = head_y + 10  # 20/2 = 10
        
        # 计算鼠标点击位置相对于蛇头中心点的位置
        dx = event.x - head_center_x
        dy = event.y - head_center_y
        
        # 根据当前方向判断蛇头两侧
        if snake_direction in ["Left", "Right"]:
            # 当前水平移动时,只考虑上下
            # 使用相对于蛇头中心的位置判断
            new_direction = "Up" if dy < 0 else "Down"
        else:
            # 当前垂直移动时,只考虑左右
            # 使用相对于蛇头中心的位置判断
            new_direction = "Left" if dx < 0 else "Right"
        
        # 防止反向移动
        opposite_directions = {
            "Left": "Right",
            "Right": "Left", 
            "Up": "Down",
            "Down": "Up"
        }
        
        if new_direction != opposite_directions.get(snake_direction):
            snake_direction = new_direction
            
    window.bind('<Button-1>', handle_click)
    window.bind('<Button-2>', handle_click)
    window.bind('<Button-3>', handle_click)

    # 添加新的按键绑定
    window.bind("<Up>", lambda event: change_direction("Up"))
    window.bind("<w>", lambda event: change_direction("Up"))
    window.bind("<W>", lambda event: change_direction("Up"))
    window.bind("<Down>", lambda event: change_direction("Down"))
    window.bind("<s>", lambda event: change_direction("Down"))
    window.bind("<S>", lambda event: change_direction("Down"))
    window.bind("<Left>", lambda event: change_direction("Left"))
    window.bind("<a>", lambda event: change_direction("Left"))
    window.bind("<A>", lambda event: change_direction("Left"))
    window.bind("<Right>", lambda event: change_direction("Right"))
    window.bind("<d>", lambda event: change_direction("Right"))
    window.bind("<D>", lambda event: change_direction("Right"))
    window.bind("<p>", lambda event: toggle_pause())     # P 键暂停/继续
    window.bind("<P>", lambda event: toggle_pause())     # P 键暂停/继续
    window.bind("<space>", lambda event: toggle_pause()) # 空格键暂停/继续
    window.bind("<r>", lambda event: reset_game())       # R 键重新开始
    window.bind("<R>", lambda event: reset_game())       # R 键重新开始
    window.bind("<b>", lambda event: back_to_start())    # B 键返回主菜单
    window.bind("<B>", lambda event: back_to_start())    # B 键返回主菜单
    window.bind("<BackSpace>", lambda event: back_to_start())    # BackSpace 键返回主菜单

    # 在绑定其他事件的地方添加
    canvas.bind("<Button-1>", create_ripple)
    canvas.bind("<Button-2>", create_ripple)
    canvas.bind("<Button-3>", create_ripple)
    def on_game_closing():
        """处理游戏窗口关闭事件"""
        try:
            # 停止游戏循环
            global game_running
            game_running = False
            
            # 停止所有音乐和音效
            pygame.mixer.music.stop()
            
            # 销毁游戏窗口
            window.destroy()
            
            # 显示开始页面
            start_page.window.deiconify()
            start_page.window.focus_force()
            
        except Exception as e:
            print(f"关闭游戏窗口时出错: {e}")
            # 确保程序不会卡死
            if 'window' in locals() and window.winfo_exists():
                window.destroy()
    
    # 设置窗口关闭处理
    window.protocol("WM_DELETE_WINDOW", on_game_closing)
    
    # 在游戏初始化分添加
    snake_speed = 100  # 初始速度
    generate_food()    # 生成第一个食物
    draw_snake()      # 画蛇
    draw_food()       # 画食物
    draw_score()      # 显示分数
    
    # 立即开始移动蛇
    move_snake()      # 直接调用move_snake而不是使用after
    
    
    window.mainloop()
# 修改程序入口点
if __name__ == "__main__":
    initialize_high_score_file()  # 确保文件存在
    start_page = StartPage()
    start_page.window.mainloop()
'''
class FrameController:
    def __init__(self, target_fps=60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.last_time = time.time()
        
    def begin_frame(self):
        """开始新一帧，返回距离上一帧的时间差"""
        current_time = time.time()
        dt = current_time - self.last_time   
        self.last_time = current_time
        return dt
    
    def end_frame(self):
        """确保帧率不超过目标值"""
        elapsed = time.time() - self.last_time
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)

# 在主循环中使用
frame_controller = FrameController(60)
'''