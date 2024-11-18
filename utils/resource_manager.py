import os
import sys
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import pygame
import logging
from builtins import open

class ResourceManager:
    """Singleton class to manage game resources"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._init_logging()
        self._init_pygame()
        self._init_attributes()
        self._initialized = True

    def _init_logging(self):
        """Initialize logging system"""
        if getattr(sys, 'frozen', False):
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        self.logger = logging.getLogger(__name__)

    def _init_pygame(self):
        """Initialize pygame and font"""
        pygame.init()
        pygame.font.init()
        self.logger.info("Initialized pygame and font")

    def _init_attributes(self):
        """Initialize basic attributes"""
        self._cache = {}
        self.config = self.load_config()
        self.setup_paths()

    # === Path Management ===
    def setup_paths(self):
        """Setup paths for resources"""
        self.base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else Path(__file__).parent.parent
        self.assets_path = os.path.join(self.base_path, 'assets')
        self.models_path = os.path.join(self.assets_path, 'models')
        self.chessboard_path = os.path.join(self.assets_path, 'chessboard')
        self.background_path = os.path.join(self.assets_path, 'background')
        self.bgmusic_path = os.path.join(self.assets_path, 'bgmusic')
        self.fonts_path = os.path.join(self.assets_path, 'fonts')
        self.icon_path = os.path.join(self.assets_path, 'icon')

    def get_resource_path(self, relative_path):
        """Get full path for resource"""
        return os.path.join(self.base_path, relative_path)

    def get_save_path(self, filename):
        """Get save file path"""
        return os.path.join(self.config['game_dir'], 'saves', filename)

    # === Config Management ===
    def load_config(self):
        """Load or create config file"""
        config_path = 'config.json'
        default_config = {
            'game_dir': os.path.dirname(os.path.abspath(__file__)),
            'last_save_dir': None,
            'cache_enabled': True,
            'debug_mode': False
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    self.logger.info("Loaded existing config")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
        
        return default_config

    def save_config(self):
        """Save config"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def select_game_directory(self):
        """Allow user to select game directory"""
        root = tk.Tk()
        root.withdraw()
        
        directory = filedialog.askdirectory(
            title='Select game directory',
            initialdir=self.config['game_dir']
        )
        
        if directory:
            self.config['game_dir'] = directory
            self.save_config()
            return True
        return False

    # === Resource Loading ===
    def load_image(self, filename):
        """Load and cache image"""
        if isinstance(filename, pygame.Surface):
            return filename
        
        possible_paths = [
            os.path.join(path, filename) for path in 
            [self.models_path, self.chessboard_path, self.background_path, self.icon_path]
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

    def load_sound(self, filename):
        """Load and cache sound"""
        path = os.path.join(self.bgmusic_path, filename)
        if path not in self._cache:
            try:
                if os.path.exists(path):
                    pygame.mixer.music.load(path)
                    self._cache[path] = True
                    self.logger.info(f"Loaded sound: {path}")
                else:
                    self.logger.warning(f"Sound file not found: {path}")
                    return False
            except Exception as e:
                self.logger.error(f"Failed to load sound {path}: {e}")
                return False
        return True

    # === Save/Load Game State ===
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

    # === Cache Management ===
    def clear_cache(self, keep_cache_info=False):
        """Clear both memory and disk cache"""
        try:
            if not keep_cache_info:
                cache_size = len(self._cache)
                self._cache.clear()
                self.logger.info(f"Cleared {cache_size} items from memory cache")
                
                if os.path.exists(self.config['game_dir']):
                    cache_info_path = os.path.join(self.config['game_dir'], 'cache_info.json')
                    for file in os.listdir(self.config['game_dir']):
                        file_path = os.path.join(self.config['game_dir'], file)
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
                self._cache.clear()
                self.logger.info("Cleared memory cache, kept cache info")
                
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    def cleanup_unused_cache(self, max_size_mb=100):
        """Clean up cache if it exceeds max size"""
        try:
            cache_size = sum(
                w * h * 4 for item in self._cache.values() 
                if isinstance(item, pygame.Surface) 
                for w, h in [item.get_size()]
            )
            
            cache_size_mb = cache_size / (1024 * 1024)
            if cache_size_mb > max_size_mb:
                self.logger.warning(f"Cache size ({cache_size_mb:.1f}MB) exceeds limit")
                self.clear_cache()
            
        except Exception as e:
            self.logger.error(f"Error cleaning cache: {e}")

    def save_cache_info(self):
        """Save cache info to file"""
        try:
            cache_info = {
                path: {
                    'type': 'surface' if isinstance(resource, pygame.Surface) else 'font',
                    'size': resource.get_size() if isinstance(resource, pygame.Surface) else resource.get_height(),
                    'path': path
                }
                for path, resource in self._cache.items()
                if isinstance(resource, (pygame.Surface, pygame.font.Font))
            }
            
            cache_info_path = os.path.join(self.config['game_dir'], 'cache_info.json')
            with open(cache_info_path, 'w') as f:
                json.dump(cache_info, f, indent=4)
                self.logger.info("Saved cache info")
            
        except Exception as e:
            self.logger.error(f"Error saving cache info: {e}")

    def load_cache_info(self):
        """Load cache info from file"""
        try:
            cache_info_path = os.path.join(self.config['game_dir'], 'cache_info.json')
            if os.path.exists(cache_info_path):
                with open(cache_info_path, 'r') as f:
                    cache_info = json.load(f)
                    
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

    # === Resource Verification ===
    def verify_resources(self):
        """Verify all required resources exist"""
        required_dirs = [
            self.assets_path, self.models_path, self.chessboard_path,
            self.background_path, self.bgmusic_path, self.fonts_path,
            self.icon_path
        ]
        
        missing_dirs = [dir_path for dir_path in required_dirs if not os.path.exists(dir_path)]
        
        if missing_dirs:
            for dir_path in missing_dirs:
                self.logger.warning(f"Missing directory: {dir_path}")
            self.logger.error("Missing required directories")
            return False
        
        self.logger.info("All resource directories verified")
        return True

    def __del__(self):
        """Save cache before cleanup"""
        if self.config.get('cache_enabled', True):
            self.save_cache_info()
        else:
            self.clear_cache()