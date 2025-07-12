#!/usr/bin/env python3
"""
Configuration Setup Script for Ink2TeX
Helps set up configuration files for both portable and installed versions.
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ink2tex.core.config import ConfigReader, ConfigManager


def main():
    """Interactive configuration setup"""
    print("=" * 60)
    print("              Ink2TeX Configuration Setup")
    print("=" * 60)
    print()
    
    # Initialize config manager
    manager = ConfigManager()
    
    # Show current configuration status
    print("📋 Current Configuration Status:")
    print("-" * 40)
    
    config_info = ConfigReader.get_config_info()
    
    if config_info['is_portable']:
        print("🎒 Mode: PORTABLE (config files next to executable)")
    else:
        print("🏠 Mode: INSTALLED (config files in user directory)")
    
    print(f"📁 Writable config directory: {config_info['writable_config_dir']}")
    print()
    
    print("📄 Configuration Files:")
    for filename, path in config_info['found_files'].items():
        if path:
            print(f"  ✅ {filename}: {path}")
        else:
            print(f"  ❌ {filename}: Not found")
    
    print()
    print("🔍 Search paths (in priority order):")
    for i, path in enumerate(config_info['config_paths'], 1):
        print(f"  {i}. {path}")
    
    print()
    
    # Offer to create missing config files
    missing_files = [f for f, path in config_info['found_files'].items() if not path]
    
    if missing_files:
        print(f"⚠️  Missing config files: {', '.join(missing_files)}")
        response = input("📝 Create default configuration files? [Y/n]: ").strip().lower()
        
        if response in ('', 'y', 'yes'):
            print()
            print("Creating default configuration files...")
            created_files = manager.create_default_config_files()
            
            for filename, filepath in created_files.items():
                print(f"  ✅ Created: {filepath}")
            
            print()
            print("🔧 Next steps:")
            print("1. Edit the .api file and add your Google Gemini API key")
            print("   Get one free at: https://makersuite.google.com/app/apikey")
            print("2. Customize the .config file if needed")
            print("3. Modify prompt.txt to customize AI behavior")
            print()
            
            # Offer to open config directory
            config_dir = manager.get_writable_config_directory()
            if sys.platform == "win32":
                response = input(f"🗂️  Open config directory in Explorer? [Y/n]: ").strip().lower()
                if response in ('', 'y', 'yes'):
                    import subprocess
                    subprocess.run(['explorer', str(config_dir)])
        else:
            print("⏭️  Skipped creating config files.")
    else:
        print("✅ All configuration files found!")
    
    print()
    
    # API key validation
    print("🔑 API Key Validation:")
    print("-" * 30)
    try:
        api_key = ConfigReader.read_api_key_from_config()
        if api_key == 'your_api_key_here':
            print("⚠️  API key is still the default template value")
            print("   Please edit your .api file and add a real API key")
        else:
            print(f"✅ API key configured (ends with: ...{api_key[-8:]})")
    except Exception as e:
        print(f"❌ API key error: {e}")
    
    print()
    print("🚀 Configuration setup complete!")
    print("   You can run this script again anytime to check status.")


if __name__ == "__main__":
    main()
