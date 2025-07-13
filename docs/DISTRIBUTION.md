# 📦 Ink2TeX Distribution Package v1.0.0

*Professional Windows installer for handwritten math to LaTeX conversion*

## 🖥️ Platform Support

- ✅ **Windows 10/11 (x64)** - Full support with professional installer
- ❌ **Linux** - Not yet implemented  
- ❌ **macOS** - Not yet implemented

*Note: Cross-platform deployment is planned for future releases*

## 🎯 For End Users

### System Requirements
- Windows 10 or Windows 11 (64-bit)
- Internet connection for AI processing
- Google Gemini API key (free)

### Installation (Recommended Method)
1. **Download** `Ink2TeX_Setup_v1.0.0.exe` from releases
2. **Run installer** - No administrator rights required
3. **Enter API key** during installation or configure later
   - Get your free API key at: https://makersuite.google.com/app/apikey
4. **Launch** Ink2TeX from Start menu or desktop shortcut

### Installation Details
- **Installation location**: `%LOCALAPPDATA%\Ink2TeX\`
- **Config files**: `%LOCALAPPDATA%\Ink2TeX\` (.api, .config, prompt.txt)
- **No admin required**: User-level installation
- **Auto-start option**: Optional Windows startup integration

### Usage
- **Activate**: Press `Ctrl+Shift+I` anywhere to open drawing overlay
- **Draw**: Create math equations with mouse, stylus, or touch
- **Convert**: Press `Enter` to convert handwriting to LaTeX
- **Edit**: Modify LaTeX before copying to clipboard
- **Close**: Press `Esc` to close overlay
- **Settings**: Right-click system tray icon for configuration

### Configuration
- **API Key**: Required for AI conversion - configure via Settings menu
- **Hotkeys**: Customizable global shortcuts
- **Auto-start**: Optional Windows startup behavior
- **Drawing settings**: Brush size, colors, canvas preferences

### Uninstallation
- Use **"Add or Remove Programs"** in Windows Settings
- Or use the **uninstaller** in Start menu
- All user data and config files are cleanly removed

## 🛠️ For Developers

### Build Commands

```bash
# Create portable executable (development)
python build_wrapper.py --portable

# Create standalone executable with dependencies
python build_wrapper.py --exe

# Create Windows installer (requires Inno Setup)
python build_wrapper.py --installer

# Full build (exe + installer)
python build_wrapper.py --full
```

### Build Requirements

- **Python 3.12+** with virtual environment support
- **PyQt6** and all project dependencies
- **Inno Setup 6** (for Windows installer)
- **Windows 10/11** development environment

### Distribution Packages

#### Portable Version
- **Location**: `dist/portable/`
- **Contents**: Executable + config templates
- **Size**: ~150-200MB
- **Use case**: Development testing, portable usage

#### Professional Installer
- **Location**: `dist/installer/Ink2TeX_Setup_v1.0.0.exe`
- **Features**: API key wizard, user-level install, auto-start option
- **Size**: ~80-120MB  
- **Use case**: End-user distribution

### Security Features

- **API Key Protection**: Personal keys never included in builds
- **Template Configs**: Clean configuration files for distribution
- **User-Level Install**: No administrator privileges required
- **License Compliance**: Apache 2.0 license headers and files included

### Cross-Platform Status

- ✅ **Windows**: Full implementation with PyInstaller + Inno Setup
- ❌ **Linux**: Planned - will use PyInstaller + AppImage/DEB packages
- ❌ **macOS**: Planned - will use PyInstaller + DMG packages

*Note: The application code is cross-platform compatible. Only build/packaging scripts need platform-specific implementation.*
