"""
声音管理模块
处理游戏中的所有音频相关功能
"""

import os
import pygame
from config import AUDIO_CONFIG, SOUND_EFFECTS

class SoundManager:
    """
    音效管理器类
    负责处理游戏中的所有音频效果，包括音效和背景音乐
    """
    
    def __init__(self):
        """初始化音效管理器"""
        self._sounds = {}
        self._sound_paths = SOUND_EFFECTS
        
        # 分离音效和音乐的控制
        self.sfx_enabled = True
        self.bgm_enabled = True
        
        # 初始化pygame音频系统
        pygame.mixer.pre_init(
            AUDIO_CONFIG['SAMPLE_RATE'],
            AUDIO_CONFIG['SAMPLE_SIZE'],
            AUDIO_CONFIG['CHANNELS'],
            AUDIO_CONFIG['BUFFER']
        )
        pygame.mixer.init()
        pygame.mixer.set_num_channels(AUDIO_CONFIG['MAX_CHANNELS'])
        
        # 创建音效通道池
        self._channels = [pygame.mixer.Channel(i) for i in range(8)]
        self._channel_index = 0
        
        # 预加载所有音效
        self._preload_sounds()
    
    def _preload_sounds(self):
        """预加载所有音效"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            for sound_name, (filename, volume) in self._sound_paths.items():
                path = os.path.join(current_dir, "assets", "music", filename)
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                # 转换音频格式以减少CPU使用
                sound = pygame.mixer.Sound(sound.get_raw())
                self._sounds[sound_name] = sound
        except Exception as e:
            print(f"预加载音效失败: {e}")
    
    def set_mode(self, mode: str):
        """
        根据模式设置音频状态
        
        Args:
            mode: 音频模式 ('off' 或 'on')
        """
        if mode == "off":
            self.bgm_enabled = False
            self.sfx_enabled = True
        else:
            self.bgm_enabled = True
            self.sfx_enabled = True
    
    def play(self, sound_name: str):
        """
        播放指定的音效
        
        Args:
            sound_name: 要播放的音效名称
        """
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
    
    def play_bgm(self, music_name: str):
        """
        播放背景音乐
        
        Args:
            music_name: 背景音乐文件名
        """
        if not self.bgm_enabled:
            return
            
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            music_path = os.path.join(current_dir, "assets", "music", music_name)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # -1表示循环播放
        except Exception as e:
            print(f"播放背景音乐失败: {e}")
    
    def stop_bgm(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
    
    def pause_bgm(self):
        """暂停背景音乐"""
        pygame.mixer.music.pause()
    
    def resume_bgm(self):
        """恢复背景音乐"""
        pygame.mixer.music.unpause()
