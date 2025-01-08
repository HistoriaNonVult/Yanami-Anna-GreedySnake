import tkinter as tk
from tkinter import ttk
import time

class ModernButton(tk.Button):
    """现代风格按钮类"""
    def __init__(self, master, **kwargs):
        # 默认样式配置
        self.default_config = {
            'font': ('Microsoft YaHei UI', 11),  # 微软雅黑字体
            'width': 8,
            'cursor': 'hand2',
            'bd': 0,
            'relief': 'flat',
            'highlightthickness': 0,
            'compound': 'center',
            'padx': 15,
            'pady': 8,
        }
        
        # 合并自定义配置
        self.default_config.update(kwargs)
        
        # 颜色配置
        self.colors = {
            'normal': {
                'bg': '#FF5722',          # 普通状态背景色
                'fg': 'white',            # 普通状态文字色
                'shadow': '#D84315'       # 阴影色
            },
            'hover': {
                'bg': '#FF7043',          # 悬停状态背景色
                'fg': 'white',            # 悬停状态文字色
                'glow': '#FF8A65'         # 发光效果色
            },
            'active': {
                'bg': '#F4511E',          # 点击状态背景色
                'fg': 'white'             # 点击状态文字色
            }
        }
        
        # 更新颜色配置
        self.default_config['bg'] = self.colors['normal']['bg']
        self.default_config['fg'] = self.colors['normal']['fg']
        self.default_config['activebackground'] = self.colors['active']['bg']
        self.default_config['activeforeground'] = self.colors['active']['fg']
        
        # 初始化按钮
        super().__init__(master, **self.default_config)
        
        # 绑定事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        
        # 动画状态
        self._animation_running = False
        self._hover_animation = None
        self._click_animation = None
    
    def _on_enter(self, event):
        """鼠标进入事件处理"""
        if self._animation_running:
            self.after_cancel(self._hover_animation)
        self._animate_hover(0)
    
    def _on_leave(self, event):
        """鼠标离开事件处理"""
        if self._animation_running:
            self.after_cancel(self._hover_animation)
        self._animate_leave(0)
    
    def _on_click(self, event):
        """鼠标点击事件处理"""
        if self._click_animation:
            self.after_cancel(self._click_animation)
        
        # 点击效果
        self.configure(bg=self.colors['active']['bg'])
        
        # 创建波纹效果
        self._create_ripple(event.x, event.y)
        
        # 100ms后恢复悬停状态
        self._click_animation = self.after(100, 
            lambda: self.configure(bg=self.colors['hover']['bg']))
    
    def _animate_hover(self, step):
        """悬停动画"""
        if step < 5:
            # 计算渐变色
            r = int(int(self.colors['normal']['bg'][1:3], 16) + 
                   (step * 8), 16)
            g = int(int(self.colors['normal']['bg'][3:5], 16) + 
                   (step * 8), 16)
            b = int(int(self.colors['normal']['bg'][5:7], 16) + 
                   (step * 8), 16)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.configure(bg=color)
            
            self._animation_running = True
            self._hover_animation = self.after(20, 
                lambda: self._animate_hover(step + 1))
        else:
            self._animation_running = False
    
    def _animate_leave(self, step):
        """离开动画"""
        if step < 5:
            # 计算渐变色
            r = int(int(self.colors['hover']['bg'][1:3], 16) - 
                   (step * 8), 16)
            g = int(int(self.colors['hover']['bg'][3:5], 16) - 
                   (step * 8), 16)
            b = int(int(self.colors['hover']['bg'][5:7], 16) - 
                   (step * 8), 16)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.configure(bg=color)
            
            self._animation_running = True
            self._hover_animation = self.after(20, 
                lambda: self._animate_leave(step + 1))
        else:
            self._animation_running = False
    
    def _create_ripple(self, x, y):
        """创建点击波纹效果"""
        # 创建画布覆盖在按钮上
        canvas = tk.Canvas(self, width=self.winfo_width(), 
                         height=self.winfo_height(),
                         highlightthickness=0, bg='')
        canvas.place(x=0, y=0)
        
        # 波纹参数
        ripple_radius = 0
        max_radius = max(self.winfo_width(), self.winfo_height()) * 1.5
        step = max_radius / 10
        alpha = 0.8
        
        def animate_ripple():
            nonlocal ripple_radius, alpha
            
            # 清除旧的波纹
            canvas.delete('ripple')
            
            if ripple_radius < max_radius:
                # 绘制新波纹
                canvas.create_oval(
                    x - ripple_radius, 
                    y - ripple_radius,
                    x + ripple_radius, 
                    y + ripple_radius,
                    fill='',
                    outline='white',
                    width=2,
                    stipple='gray50',
                    tags='ripple'
                )
                
                # 更新参数
                ripple_radius += step
                alpha -= 0.08
                
                # 继续动画
                self.after(20, animate_ripple)
            else:
                # 动画结束，销毁画布
                canvas.destroy()
        
        # 开始波纹动画
        animate_ripple()

class DemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("现代按钮演示")
        self.root.geometry("800x600")
        
        # 设置窗口样式
        self.root.configure(bg='#f0f0f0')
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        # 创建标题
        title_label = ttk.Label(
            self.main_frame, 
            text="现代按钮演示", 
            font=('Microsoft YaHei UI', 24, 'bold')
        )
        title_label.pack(pady=20)
        
        # 创建按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        # 创建不同样式的按钮
        self.create_buttons()
        
        # 创建计数器显示
        self.counter_label = ttk.Label(
            self.main_frame,
            text="点击次数: 0",
            font=('Microsoft YaHei UI', 12)
        )
        self.counter_label.pack(pady=20)
        
        self.click_count = 0
    
    def create_buttons(self):
        # 默认样式按钮
        self.btn1 = ModernButton(
            self.button_frame,
            text="点击我",
            command=self.increment_counter
        )
        self.btn1.pack(side='left', padx=10)
        
        # 自定义颜色按钮
        self.btn2 = ModernButton(
            self.button_frame,
            text="重置",
            command=self.reset_counter
        )
        self.btn2.colors['normal']['bg'] = '#2196F3'  # 蓝色主题
        self.btn2.colors['hover']['bg'] = '#42A5F5'
        self.btn2.colors['active']['bg'] = '#1976D2'
        self.btn2.configure(bg=self.btn2.colors['normal']['bg'])
        self.btn2.pack(side='left', padx=10)
    
    def increment_counter(self):
        self.click_count += 1
        self.counter_label.config(text=f"点击次数: {self.click_count}")
    
    def reset_counter(self):
        self.click_count = 0
        self.counter_label.config(text=f"点击次数: {self.click_count}")

if __name__ == '__main__':
    root = tk.Tk()
    app = DemoApp(root)
    root.mainloop()