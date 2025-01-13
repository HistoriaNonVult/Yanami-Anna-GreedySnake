import pygame
import sys
import random
import math
from pygame import gfxdraw
from collections import deque
import os

class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # 初始化音频系统
        
        # 基础设置
        self.WIDTH = 800
        self.HEIGHT = 600
        self.GRID_SIZE = 20
        self.FPS = 60
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.running = True
        self.paused = False
        self.score = 0
        self.snake_speed = 10  # 基础速度
        
        # 初始化蛇
        self.snake = [(20, 20), (20, 40), (20, 60)]  # 蛇身坐标列表
        self.direction = (0, 1)  # 初始向下移动
        
        # 初始化食物
        self.food = self.generate_food()
        
        # 初始化音效（在load_resources之前设置默认值）
        self.death_sound = pygame.mixer.Sound(buffer=b'')  # 创建空的音效
        self.eat_sound = pygame.mixer.Sound(buffer=b'')
        
        try:
            self.load_resources()
        except Exception as e:
            print(f"资源加载失败: {e}")
            print("使用默认设置继续运行")
        
        # 粒子系统
        self.particles = []
        
    def load_resources(self):
        """加载图片、音效等资源"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 加载背景图片
            self.bg_image = pygame.image.load(os.path.join(current_dir, "assets/images/background.jpg")).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (self.WIDTH, self.HEIGHT))
            
            # 加载音效
            self.eat_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets/music/eat.wav"))
            self.death_sound = pygame.mixer.Sound(os.path.join(current_dir, "assets/music/death.wav"))
            
            # 加载背景音乐
            pygame.mixer.music.load(os.path.join(current_dir, "assets/music/background.mp3"))
            pygame.mixer.music.play(-1)  # 循环播放
            
        except Exception as e:
            print(f"资源加载错误: {e}")
            # 即使加载失败也继续使用默认值
    
    def generate_food(self):
        """生成新的食物"""
        while True:
            x = random.randrange(0, self.WIDTH, self.GRID_SIZE)
            y = random.randrange(0, self.HEIGHT, self.GRID_SIZE)
            if (x, y) not in self.snake:
                return (x, y)
    
    def add_particles(self, x, y, color):
        """添加粒子效果"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color
            })
    
    def update_particles(self):
        """更新粒子状态"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 0.02
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """绘制粒子"""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            pos = (int(particle['x']), int(particle['y']))
            
            surf = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (1, 1), 1)
            self.screen.blit(surf, pos)
    
    def handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_game()
                    
                # 方向控制
                if not self.paused:
                    if event.key in (pygame.K_w, pygame.K_UP) and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN) and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key in (pygame.K_a, pygame.K_LEFT) and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT) and self.direction != (-1, 0):
                        self.direction = (1, 0)
    
    def update(self):
        """更新游戏状态"""
        if self.paused:
            return
            
        # 移动蛇
        head_x = self.snake[-1][0] + self.direction[0] * self.GRID_SIZE
        head_y = self.snake[-1][1] + self.direction[1] * self.GRID_SIZE
        
        # 检查碰撞
        if (head_x < 0 or head_x >= self.WIDTH or 
            head_y < 0 or head_y >= self.HEIGHT or 
            (head_x, head_y) in self.snake):
            self.game_over()
            return
        
        # 添加新头部
        self.snake.append((head_x, head_y))
        
        # 检查是否吃到食物
        if (head_x, head_y) == self.food:
            self.eat_sound.play()
            self.score += 1
            self.food = self.generate_food()
            self.add_particles(head_x, head_y, (255, 215, 0))
        else:
            self.snake.pop(0)  # 移除尾部
        
        # 更新粒子
        self.update_particles()
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制背景
        self.screen.blit(self.bg_image, (0, 0))
        
        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            color = self.get_snake_segment_color(i)
            pygame.draw.rect(self.screen, color, (x, y, self.GRID_SIZE-1, self.GRID_SIZE-1))
        
        # 绘制食物
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (*self.food, self.GRID_SIZE-1, self.GRID_SIZE-1))
        
        # 绘制粒子
        self.draw_particles()
        
        # 绘制分数
        self.draw_score()
        
        # 如果暂停，绘制暂停文本
        if self.paused:
            self.draw_pause_text()
        
        pygame.display.flip()
    
    def get_snake_segment_color(self, index):
        """获取蛇身段的颜色(可以实现渐变效果)"""
        progress = index / len(self.snake)
        return (
            int(100 + 155 * progress),
            int(200 + 55 * progress),
            int(100 + 155 * (1 - progress))
        )
    
    def draw_score(self):
        """绘制分数"""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
    
    def draw_pause_text(self):
        """绘制暂停文本"""
        font = pygame.font.Font(None, 48)
        text = font.render('PAUSED', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        self.screen.blit(text, text_rect)
    
    def game_over(self):
        """游戏结束处理"""
        self.death_sound.play()
        # 可以添加死亡动画等效果
        
    def reset_game(self):
        """重置游戏"""
        self.snake = [(20, 20), (20, 40), (20, 60)]
        self.direction = (0, 1)
        self.score = 0
        self.food = self.generate_food()
        self.particles.clear()
        self.paused = False
    
    def run(self):
        """游戏主循环"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()