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