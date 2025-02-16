"""
窗口管理模块
处理游戏窗口的创建和管理
"""

import tkinter as tk
import time
from config import COLORS, GAME_CONFIG

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
                    lambda e, l=item_label: l.configure(fg='#FF2D55'))
                item_label.bind('<Leave>', 
                    lambda e, l=item_label: l.configure(fg='#FFD700'))
        
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