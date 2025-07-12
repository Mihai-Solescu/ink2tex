"""
Configuration management for Ink2TeX.
Handles reading API keys and configuration values from files with cross-platform support.
Supports both portable and installed deployment modes.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List


class ConfigManager:
    """Enhanced configuration manager with cross-platform support and portable mode detection"""
    
    def __init__(self):
        self._config_paths = self._discover_config_paths()
        self._is_portable = self._detect_portable_mode()
    
    def _detect_portable_mode(self) -> bool:
        """Detect if running in portable mode (config files next to executable)"""
        executable_dir = self._get_executable_directory()
        
        # Check if any config files exist next to the executable
        portable_indicators = ['.api', '.config', 'prompt.txt']
        for indicator in portable_indicators:
            if (executable_dir / indicator).exists():
                return True
        return False
    
    def _get_executable_directory(self) -> Path:
        """Get the directory containing the executable or script"""
        if getattr(sys, 'frozen', False):
            # PyInstaller executable
            return Path(sys.executable).parent
        else:
            # Development mode - use project root
            return self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for pyproject.toml"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        # Fallback to current script directory
        return Path(__file__).resolve().parent.parent.parent
    
    def _get_user_config_directory(self) -> Path:
        """Get the platform-specific user configuration directory"""
        if sys.platform == "win32":
            # Windows: Use APPDATA for roaming configs
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata) / "Ink2TeX"
            else:
                return Path.home() / "AppData" / "Roaming" / "Ink2TeX"
        elif sys.platform == "darwin":
            # macOS: Use Application Support
            return Path.home() / "Library" / "Application Support" / "Ink2TeX"
        else:
            # Linux/Unix: Use XDG config directory
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                return Path(xdg_config) / "ink2tex"
            else:
                return Path.home() / ".config" / "ink2tex"
    
    def _discover_config_paths(self) -> List[Path]:
        """Discover all possible configuration directories in priority order"""
        paths = []
        
        # 1. Portable mode: next to executable (highest priority)
        executable_dir = self._get_executable_directory()
        paths.append(executable_dir)
        
        # 2. User config directory (platform-specific)
        user_config_dir = self._get_user_config_directory()
        paths.append(user_config_dir)
        
        # 3. Fallback: current working directory
        paths.append(Path.cwd())
        
        return paths
    
    def find_config_file(self, filename: str) -> Optional[Path]:
        """Find a configuration file by checking all config paths in priority order"""
        for config_path in self._config_paths:
            file_path = config_path / filename
            if file_path.exists() and file_path.is_file():
                return file_path
        return None
    
    def get_writable_config_directory(self) -> Path:
        """Get the preferred directory for writing config files"""
        if self._is_portable:
            # Portable mode: write next to executable
            return self._get_executable_directory()
        else:
            # Installed mode: use user config directory
            user_config_dir = self._get_user_config_directory()
            user_config_dir.mkdir(parents=True, exist_ok=True)
            return user_config_dir
    
    def create_default_config_files(self) -> dict:
        """Create default configuration files if they don't exist"""
        config_dir = self.get_writable_config_directory()
        created_files = {}
        
        # Create .api file with template
        api_file = config_dir / '.api'
        if not api_file.exists():
            api_content = """# Google Gemini API Key Configuration
# Get your free API key from: https://makersuite.google.com/app/apikey
# Replace 'your_api_key_here' with your actual API key
GOOGLE_API_KEY=your_api_key_here
"""
            api_file.write_text(api_content, encoding='utf-8')
            created_files['.api'] = str(api_file)
        
        # Create .config file with defaults
        config_file = config_dir / '.config'
        if not config_file.exists():
            config_content = """# Ink2TeX Configuration File
# Application settings and preferences

# Auto-start with Windows (true/false)
AUTO_START=false

# Global hotkey for overlay (default: ctrl+shift+i)
HOTKEY=ctrl+shift+i

# AI prompt file location (relative to config directory)
PROMPT_FILE=prompt.txt

# Application behavior settings
STARTUP_NOTIFICATION=true
TRAY_ICON_TOOLTIP=Ink2TeX - Math to LaTeX Converter
"""
            config_file.write_text(config_content, encoding='utf-8')
            created_files['.config'] = str(config_file)
        
        # Create prompt.txt file
        prompt_file = config_dir / 'prompt.txt'
        if not prompt_file.exists():
            prompt_content = """From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1. Each line of handwritten text must be on its own new line in the output.
2. Enclose each separate line of LaTeX within single dollar signs ($).
3. Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex."""
            prompt_file.write_text(prompt_content, encoding='utf-8')
            created_files['prompt.txt'] = str(prompt_file)
        
        return created_files
    
    @property
    def is_portable(self) -> bool:
        """Check if running in portable mode"""
        return self._is_portable
    
    @property
    def config_paths(self) -> List[Path]:
        """Get all configuration search paths"""
        return self._config_paths.copy()


class ConfigReader:
    """Utility class to read configuration values using the new ConfigManager"""
    
    _manager = None
    
    @classmethod
    def _get_manager(cls) -> ConfigManager:
        """Get or create the singleton ConfigManager instance"""
        if cls._manager is None:
            cls._manager = ConfigManager()
        return cls._manager
    
    @staticmethod
    def read_api_key_from_config(config_path: str = '.api') -> str:
        """Read Google API key from .api file
        
        Args:
            config_path: Filename of the API configuration file (not full path)
            
        Returns:
            The API key string
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If no API key is found in the file
        """
        manager = ConfigReader._get_manager()
        api_file = manager.find_config_file(config_path)
        
        if not api_file:
            # Try to create default config files
            created_files = manager.create_default_config_files()
            if config_path in created_files:
                raise ValueError(f"API configuration file '{config_path}' was created with template. Please edit {created_files[config_path]} and add your Google Gemini API key.")
            else:
                raise FileNotFoundError(f"API configuration file '{config_path}' not found in any config directory.")
        
        with open(api_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('/'):
                continue
                
            if '=' in line and line.upper().startswith('GOOGLE_API_KEY'):
                key_part = line.split('=', 1)[1].strip()
                if key_part and key_part != 'your_api_key_here':
                    return key_part
        
        raise ValueError(f"API key not found or not configured in {api_file}. Please edit the file and add your Google Gemini API key.")
    
    @staticmethod
    def read_config_value(key: str, config_path: str = '.config', default: Optional[str] = None) -> Optional[str]:
        """Read a configuration value from .config file
        
        Args:
            key: The configuration key to look for
            config_path: Filename of the configuration file (not full path)
            default: Default value to return if key not found
            
        Returns:
            The configuration value or default if not found
        """
        manager = ConfigReader._get_manager()
        config_file = manager.find_config_file(config_path)
        
        if not config_file:
            # Try to create default config files
            manager.create_default_config_files()
            config_file = manager.find_config_file(config_path)
            
        if not config_file:
            return default
        
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line and line.upper().startswith(key.upper()):
                value = line.split('=', 1)[1].strip()
                if value:
                    return value
        
        return default
    
    @staticmethod
    def read_prompt_from_file(prompt_file: Optional[str] = None) -> str:
        """Read the Gemini prompt from file
        
        Args:
            prompt_file: Filename of the prompt file. If None, reads from config.
            
        Returns:
            The prompt text
        """
        manager = ConfigReader._get_manager()
        
        if prompt_file is None:
            prompt_file = ConfigReader.read_config_value('PROMPT_FILE', default='prompt.txt')
        
        prompt_path = manager.find_config_file(prompt_file)
        
        if not prompt_path:
            # Try to create default config files
            created_files = manager.create_default_config_files()
            prompt_path = manager.find_config_file(prompt_file)
        
        if not prompt_path:
            # Fallback to default prompt if file not found
            return """From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1.  Each line of handwritten text must be on its own new line in the output.
2.  Enclose each separate line of LaTeX within single dollar signs ($).
3.  Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex."""
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    @staticmethod
    def update_config_setting(key: str, value: str, config_path: str = '.config') -> None:
        """Update a single setting in the config file
        
        Args:
            key: The configuration key to update
            value: The new value
            config_path: Filename of the configuration file (not full path)
        """
        manager = ConfigReader._get_manager()
        
        # Find existing config file or create new one
        existing_file = manager.find_config_file(config_path)
        if existing_file:
            config_file_path = existing_file
        else:
            # Create in writable config directory
            config_dir = manager.get_writable_config_directory()
            config_file_path = config_dir / config_path
        
        config_lines = []
        
        if config_file_path.exists():
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_lines = f.readlines()
        
        # Update or add setting
        updated = False
        for i, line in enumerate(config_lines):
            if line.strip().upper().startswith(key.upper()):
                config_lines[i] = f'{key}={value}\n'
                updated = True
                break
        
        if not updated:
            config_lines.append(f'{key}={value}\n')
        
        # Write back to file
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.writelines(config_lines)
    
    @staticmethod
    def get_config_info() -> dict:
        """Get information about the current configuration setup"""
        manager = ConfigReader._get_manager()
        
        info = {
            'is_portable': manager.is_portable,
            'config_paths': [str(path) for path in manager.config_paths],
            'writable_config_dir': str(manager.get_writable_config_directory()),
            'found_files': {}
        }
        
        # Check which config files are found where
        config_files = ['.api', '.config', 'prompt.txt']
        for filename in config_files:
            found_path = manager.find_config_file(filename)
            info['found_files'][filename] = str(found_path) if found_path else None
        
        return info
