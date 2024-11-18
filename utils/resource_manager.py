import os
import sys
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import pygame
import logging

class ResourceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Chỉ show logs khi chạy từ source code
        if getattr(sys, 'frozen', False):
            # Đang chạy từ exe
            logging.basicConfig(level=logging.ERROR)  # Chỉ log lỗi nghiêm trọng
        else:
            # Đang chạy từ source code
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            
        self.logger = logging.getLogger(__name__)
        
        pygame.init()
        pygame.font.init()
        self.logger.info("Initialized pygame and font")
        
        self._cache = {}
        self.config = self.load_config()
        
        # Tạo thư mục cache trong project folder
        self._cache_dir = os.path.join(self.config['game_dir'], 'cache')
        self._save_dir = os.path.join(self.config['game_dir'], 'saves')
        
        # Tạo các thư mục cần thiết
        os.makedirs(self._cache_dir, exist_ok=True)
        os.makedirs(self._save_dir, exist_ok=True)
        
        # Load cache từ lần chạy trước
        self.load_cache_info()
        
        self.setup_paths()
        self._initialized = True

    def setup_paths(self):
        """Setup các đường dẫn cho tài nguyên"""
        if getattr(sys, 'frozen', False):
            # Nếu đang chạy từ file exe (PyInstaller)
            self.base_path = sys._MEIPASS
        else:
            # Nếu đang chạy từ source code
            self.base_path = Path(__file__).parent.parent

        # Tạo các đường dẫn cố định
        self.assets_path = os.path.join(self.base_path, 'assets')
        self.models_path = os.path.join(self.assets_path, 'models')
        self.chessboard_path = os.path.join(self.assets_path, 'chessboard')
        self.background_path = os.path.join(self.assets_path, 'background')
        self.bgmusic_path = os.path.join(self.assets_path, 'bgmusic')
        self.fonts_path = os.path.join(self.assets_path, 'fonts')
        self.icon_path = os.path.join(self.assets_path, 'icon')

    def load_config(self):
        """Load hoặc tạo config file"""
        config_path = 'config.json'
        default_config = {
            'game_dir': os.path.dirname(os.path.abspath(__file__)),
            'last_save_dir': None,
            'cache_enabled': True,  # Thêm option để bật/tắt cache
            'debug_mode': False     # Thêm debug mode
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Update default config với giá trị đã load
                    default_config.update(loaded_config)
                    self.logger.info("Loaded existing config")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
        
        return default_config

    def save_config(self):
        """Lưu config"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def select_game_directory(self):
        """Cho phép người dùng chọn thư mục lưu game"""
        root = tk.Tk()
        root.withdraw()
        
        directory = filedialog.askdirectory(
            title='Chọn thư mục lưu game',
            initialdir=self.config['game_dir']
        )
        
        if directory:
            self.config['game_dir'] = directory
            self._cache_dir = os.path.join(directory, 'cache')
            self._save_dir = os.path.join(directory, 'saves')
            
            os.makedirs(self._cache_dir, exist_ok=True)
            os.makedirs(self._save_dir, exist_ok=True)
            
            self.save_config()
            return True
        return False

    def load_image(self, filename):
        """Load and cache image"""
        possible_paths = [
            os.path.join(self.models_path, filename),
            os.path.join(self.chessboard_path, filename),
            os.path.join(self.icon_path, filename),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                if path not in self._cache:
                    try:
                        self._cache[path] = pygame.image.load(path)
                        self.logger.info(f"Loaded image: {path}")
                    except pygame.error as e:
                        self.logger.error(f"Failed to load image {path}: {e}")
                        continue
                return self._cache[path]
        self.logger.warning(f"Image not found: {filename}")
        return None

    def load_font(self, filename, size):
        """Load and cache font"""
        if filename is None:
            key = f"default_font_{size}"
            if key not in self._cache:
                self._cache[key] = pygame.font.Font(None, size)
            return self._cache[key]
        
        path = os.path.join(self.fonts_path, filename)
        key = f"{path}_{size}"
        if key not in self._cache:
            try:
                self._cache[key] = pygame.font.Font(path, size)
            except:
                self._cache[key] = pygame.font.Font(None, size)
        return self._cache[key]

    def get_resource_path(self, relative_path):
        """Get full path for resource"""
        if getattr(sys, 'frozen', False):
            return os.path.join(self.base_path, relative_path)
        return os.path.join(self.base_path, relative_path)

    def get_save_path(self, filename):
        """Get save file path"""
        return os.path.join(self._save_dir, filename)

    def save_game(self, game_state, filename='save.json'):
        """Save game state"""
        save_path = self.get_save_path(filename)
        with open(save_path, 'w') as f:
            json.dump(game_state, f, indent=4)
        self.config['last_save_dir'] = save_path
        self.save_config()

    def load_game(self, filename='save.json'):
        """Load game state"""
        save_path = self.get_save_path(filename)
        try:
            with open(save_path, 'r') as f:
                return json.load(f)
        except:
            return None

    def clear_cache(self, keep_cache_info=False):
        """Clear both memory and disk cache"""
        try:
            if not keep_cache_info:
                # Clear memory cache
                cache_size = len(self._cache)
                self._cache.clear()
                self.logger.info(f"Cleared {cache_size} items from memory cache")
                
                # Clear disk cache
                if os.path.exists(self._cache_dir):
                    cache_info_path = os.path.join(self._cache_dir, 'cache_info.json')
                    for file in os.listdir(self._cache_dir):
                        file_path = os.path.join(self._cache_dir, file)
                        if file_path != cache_info_path or not keep_cache_info:
                            try:
                                if os.path.isfile(file_path):
                                    os.unlink(file_path)
                                elif os.path.isdir(file_path):
                                    import shutil
                                    shutil.rmtree(file_path)
                            except Exception as e:
                                self.logger.error(f"Error deleting {file_path}: {e}")
            else:
                # Chỉ clear memory cache, giữ lại cache info
                self._cache.clear()
                self.logger.info("Cleared memory cache, kept cache info")
                
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    def verify_resources(self):
        """Verify all required resources exist"""
        required_dirs = [
            self.assets_path,
            self.models_path,
            self.chessboard_path,
            self.background_path,
            self.bgmusic_path,
            self.fonts_path,
            self.icon_path
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                self.logger.warning(f"Missing directory: {dir_path}")
        
        if missing_dirs:
            self.logger.error("Missing required directories")
            return False
        
        self.logger.info("All resource directories verified")
        return True

    def cleanup_unused_cache(self, max_size_mb=100):
        """Clean up cache if it exceeds max size"""
        try:
            cache_size = 0
            for path in self._cache:
                if isinstance(self._cache[path], pygame.Surface):
                    w, h = self._cache[path].get_size()
                    cache_size += w * h * 4  # 4 bytes per pixel
            
            cache_size_mb = cache_size / (1024 * 1024)
            if cache_size_mb > max_size_mb:
                self.logger.warning(f"Cache size ({cache_size_mb:.1f}MB) exceeds limit")
                self.clear_cache()
            
        except Exception as e:
            self.logger.error(f"Error cleaning cache: {e}")

    def save_cache_info(self):
        """Lưu thông tin cache vào file"""
        try:
            cache_info = {}
            for path, resource in self._cache.items():
                if isinstance(resource, pygame.Surface):
                    # Lưu thông tin của Surface
                    cache_info[path] = {
                        'type': 'surface',
                        'size': resource.get_size(),
                        'path': path
                    }
                elif isinstance(resource, pygame.font.Font):
                    # Lưu thông tin của Font
                    cache_info[path] = {
                        'type': 'font',
                        'size': resource.get_height(),
                        'path': path
                    }
            
            cache_info_path = os.path.join(self._cache_dir, 'cache_info.json')
            with open(cache_info_path, 'w') as f:
                json.dump(cache_info, f, indent=4)
                self.logger.info("Saved cache info")
            
        except Exception as e:
            self.logger.error(f"Error saving cache info: {e}")

    def load_cache_info(self):
        """Load thông tin cache từ file"""
        try:
            cache_info_path = os.path.join(self._cache_dir, 'cache_info.json')
            if os.path.exists(cache_info_path):
                with open(cache_info_path, 'r') as f:
                    cache_info = json.load(f)
                    
                # Tải lại các resource từ thông tin cache
                for path, info in cache_info.items():
                    if info['type'] == 'surface' and os.path.exists(path):
                        try:
                            self._cache[path] = pygame.image.load(path)
                            self.logger.info(f"Restored cached image: {path}")
                        except:
                            self.logger.warning(f"Failed to restore cached image: {path}")
                    elif info['type'] == 'font':
                        if path.startswith('default_font_'):
                            size = int(path.split('_')[-1])
                            self._cache[path] = pygame.font.Font(None, size)
                        elif os.path.exists(path):
                            size = info['size']
                            self._cache[path] = pygame.font.Font(path, size)
                
                self.logger.info(f"Restored {len(cache_info)} cached items")
                
        except Exception as e:
            self.logger.error(f"Error loading cache info: {e}")

    def __del__(self):
        """Save cache before cleanup"""
        if self.config.get('cache_enabled', True):
            self.save_cache_info()
        else:
            self.clear_cache()