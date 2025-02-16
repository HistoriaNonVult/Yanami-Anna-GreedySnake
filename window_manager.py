"""
窗口管理模块
处理游戏窗口的创建和管理
"""

import tkinter as tk
import time
from config import COLORS, GAME_CONFIG

class TransparentWindow:
    """
    透明窗口类
    用于创建和管理游戏的说明窗口
    """
    
    def __init__(self, parent):
        """
        初始化透明窗口
        
        Args:
            parent: 父窗口实例
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Instructions")
        
        # 设置窗口尺寸和位置
        self._setup_window_geometry(parent)
        
        # 设置窗口属性
        self._setup_window_attributes()
        
        # 创建窗口内容
        self._create_window_content()
        
        # 绑定快捷键
        self._bind_shortcuts()
        
        # 添加渐入效果
        self.window.attributes('-alpha', 0.0)
        self.advanced_fade_in()
        
        # 启动动画
        self.start_animations()
    
    def _setup_window_geometry(self, parent):
        """设置窗口几何属性"""
        window_width = GAME_CONFIG['WINDOW_WIDTH']
        window_height = GAME_CONFIG['WINDOW_HEIGHT']
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _setup_window_attributes(self):
        """设置窗口属性"""
        self.window.attributes('-alpha', 0.95)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
    
    def _create_window_content(self):
        """创建窗口内容"""
        # 创建主框架
        self.main_frame = tk.Frame(
            self.window,
            bg=COLORS['BACKGROUND']
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建边框效果
        self._create_borders()
        
        # 创建标题栏
        self._create_title_bar()
        
        # 创建内容区域
        self._create_content_area()
    
    def _create_borders(self):
        """创建边框效果"""
        self.outer_border = tk.Frame(
            self.main_frame,
            bg=COLORS['BACKGROUND'],
            highlightbackground=COLORS['BORDER_PRIMARY'],
            highlightthickness=2
        )
        self.outer_border.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        self.inner_border = tk.Frame(
            self.outer_border,
            bg=COLORS['BACKGROUND'],
            highlightbackground=COLORS['BORDER_SECONDARY'],
            highlightthickness=1
        )
        self.inner_border.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def _create_title_bar(self):
        """创建标题栏"""
        self.title_bar = tk.Frame(
            self.inner_border,
            bg=COLORS['TITLE_BAR'],
            height=40
        )
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # 添加装饰线
        self.create_tech_lines()
        
        # 绑定拖动事件
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        
        # 创建关闭按钮
        self._create_close_button()
        
        # 创建标题
        self._create_title()
    
    def _create_close_button(self):
        """创建关闭按钮"""
        close_frame = tk.Frame(self.title_bar, bg=COLORS['TITLE_BAR'])
        close_frame.pack(side=tk.RIGHT, padx=5)
        
        close_button = tk.Label(
            close_frame,
            text='⬡',
            bg=COLORS['TITLE_BAR'],
            fg=COLORS['BORDER_PRIMARY'],
            font=('Consolas', 20)
        )
        close_button.pack(side=tk.RIGHT)
        close_button.bind('<Button-1>', lambda e: self.window.destroy())
        close_button.bind('<Enter>', lambda e: self.pulse_effect(close_button))
    
    def _create_title(self):
        """创建标题"""
        self.title_label = tk.Label(
            self.title_bar,
            text='INSTRUCTIONS',
            bg=COLORS['TITLE_BAR'],
            fg=COLORS['BORDER_PRIMARY'],
            font=('Orbitron', 14, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, padx=15)
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<Left>', lambda e: self._move_window('left'))
        self.window.bind('<Right>', lambda e: self._move_window('right'))
        self.window.bind('<Up>', lambda e: self._move_window('up'))
        self.window.bind('<Down>', lambda e: self._move_window('down'))
    
    def create_tech_lines(self):
        """创建装饰线"""
        # 实现装饰线的创建逻辑
        pass
    
    def pulse_effect(self, widget):
        """创建脉冲发光效果"""
        # 实现脉冲效果的逻辑
        pass
    
    def advanced_fade_in(self, alpha=0.0):
        """实现渐入效果"""
        if alpha < 0.95:
            alpha += 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.advanced_fade_in(alpha))
    
    def start_animations(self):
        """启动动画效果"""
        self.animate_tech_lines()
    
    def animate_tech_lines(self):
        """动画效果：装饰线"""
        # 实现装饰线动画的逻辑
        pass
    
    def start_move(self, event):
        """开始移动窗口"""
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        """移动窗口"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def _move_window(self, direction):
        """
        移动窗口
        
        Args:
            direction: 移动方向 ('left', 'right', 'up', 'down')
        """
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        
        if direction == 'left':
            x -= 10
        elif direction == 'right':
            x += 10
        elif direction == 'up':
            y -= 10
        elif direction == 'down':
            y += 10
            
        self.window.geometry(f"+{x}+{y}")
