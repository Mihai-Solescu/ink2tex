"""
Configuration management for Ink2TeX.
Handles reading API keys and configuration values from files.
"""

import os
from typing import Optional


class ConfigReader:
    """Utility class to read configuration from .api and .config files"""
    
    @staticmethod
    def read_api_key_from_config(config_path: str = '.api') -> str:
        """Read Google API key from .api file
        
        Args:
            config_path: Path to the API configuration file
            
        Returns:
            The API key string
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If no API key is found in the file
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"API configuration file '{config_path}' not found.")
        
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('/'):
                continue
                
            if '=' in line and line.upper().startswith('GOOGLE_API_KEY'):
                key_part = line.split('=', 1)[1].strip()
                if key_part:
                    return key_part
        
        raise ValueError("API key not found in .api file")
    
    @staticmethod
    def read_config_value(key: str, config_path: str = '.config', default: Optional[str] = None) -> Optional[str]:
        """Read a configuration value from .config file
        
        Args:
            key: The configuration key to look for
            config_path: Path to the configuration file
            default: Default value to return if key not found
            
        Returns:
            The configuration value or default if not found
        """
        if not os.path.exists(config_path):
            return default
        
        with open(config_path, 'r') as f:
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
            prompt_file: Path to the prompt file. If None, reads from config.
            
        Returns:
            The prompt text
        """
        if prompt_file is None:
            prompt_file = ConfigReader.read_config_value('PROMPT_FILE', default='prompt.txt')
        
        if not os.path.exists(prompt_file):
            # Fallback to default prompt if file not found
            return """From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1.  Each line of handwritten text must be on its own new line in the output.
2.  Enclose each separate line of LaTeX within single dollar signs ($).
3.  Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex."""
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    @staticmethod
    def update_config_setting(key: str, value: str, config_path: str = '.config') -> None:
        """Update a single setting in the config file
        
        Args:
            key: The configuration key to update
            value: The new value
            config_path: Path to the configuration file
        """
        config_lines = []
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
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
        with open(config_path, 'w') as f:
            f.writelines(config_lines)
