# Ink2TeX - Handwritten Math to LaTeX Converter

<div align="center">
  <img src="src/ink2tex/assets/icon.ico" alt="Ink2TeX Icon" width="64" height="64">
  
  *Version 1.0.0 - Professional Windows Release*
  
  🖊️ **Draw Math** • 🤖 **AI Converts** • 📋 **Copy LaTeX** • ✨ **Perfect Results**
  
  [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/Platform-Windows%2010/11-lightblue.svg)](#platform-support)
  [![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](#version-100-highlights)
</div>

---

A modern PyQt6 system tray application that converts handwritten mathematical equations to LaTeX format using Google's Gemini AI. Features a modular architecture with Python-based build system and professional Windows installer.

## � Key Features

- 🖊️ **Intuitive Drawing Interface** - Full-screen transparent overlay
- 🤖 **AI-Powered Conversion** - Google Gemini AI processes your handwriting
- 📋 **One-Click Copy** - LaTeX instantly copied to clipboard
- ⚙️ **Comprehensive Settings** - 6-tab configuration interface
- 🔥 **Global Hotkeys** - Ctrl+Shift+I from anywhere
- 🖥️ **System Tray Integration** - Runs quietly in background
- 🔒 **Secure API Management** - Protected key storage
- 📱 **Professional Installer** - User-level installation wizard

## �📋 Version 1.0.0 Highlights

- ✅ **Professional Windows Installer** with API key wizard
- ✅ **User-level Installation** (no admin rights required)
- ✅ **Apache License 2.0** with full compliance
- ✅ **Comprehensive Settings UI** with automatic API refresh
- ✅ **Security Features** (personal API key protection)
- ✅ **Build System** with Python-based automation
- ✅ **LaTeX Preview** with real-time rendering
- ✅ **Global Hotkeys** and system tray integration

## 🖥️ Platform Support

- ✅ **Windows 10/11 (x64)** ## ⚙️ **Configuration**

Ink2TeX features an intelligent configuration system with two deployment modes:

- **🎒 Portable Mode**: Config files next to executable (for portable usage)
- **🏠 Installed Mode**: Config files in user directories (Windows installer default)

### **Configuration Locations**

**Windows (Installed)**: `%LOCALAPPDATA%\Ink2TeX\`
**Windows (Portable)**: Next to executable
**Linux/macOS**: Not yet implemented

### **Configuration Files**

- `.api` - Your Google Gemini API key (required)
- `.config` - Application settings (auto-start, hotkeys, etc.)
- `prompt.txt` - AI conversion behavior customization

### **First-Time Setup**

1. **Get API Key**: Visit https://makersuite.google.com/app/apikey
2. **Configure via installer**: Enter key during installation, or
3. **Configure via Settings**: Right-click tray icon → Settings → General tab
4. **Test connection**: Settings window includes API test button

The system automatically creates template files with helpful comments for easy setup.support with professional installer
- ❌ **Linux** - Code compatible, deployment not implemented  
- ❌ **macOS** - Code compatible, deployment not implemented

*The application core is cross-platform compatible. Build scripts and packaging are currently Windows-specific. Linux and macOS deployment planned for future releases.*

## 🏗️ **Architecture Overview**

Ink2TeX uses a modern modular architecture with Python-based build automation:

```
ink2tex/
├── .api                    # Google Gemini API key configuration
├── .config                 # Application settings and configuration
├── .gitignore             # Git ignore rules
├── build_wrapper.py       # Python build system (replaces batch files)
├── test_startup.py        # Application startup testing
├── prompt.txt             # AI prompt template for handwriting conversion
├── pyproject.toml         # Modern Python project configuration
├── README.md              # This documentation file
├── dist/                  # Build output directory
│   └── portable/          # Portable executable builds
├── docs/                  # Documentation files
│   ├── AUTO_STARTUP_FEATURES.md
│   ├── DEPLOYMENT.md
│   └── DISTRIBUTION.md
├── installer/             # PyInstaller and installer configuration
│   ├── ink2tex.spec       # PyInstaller build specification
│   ├── installer.iss      # Inno Setup installer script
│   ├── requirements-build.txt # Build-time dependencies
│   ├── version_info.txt   # Windows executable version information
│   └── hooks/             # PyInstaller custom hooks
│       └── runtime_hook_numpy.py
├── scripts/               # Python build automation scripts
│   ├── build.py           # Complete build orchestration
│   ├── build_exe.py       # Executable-only build
│   ├── build_installer.py # Installer-only build
│   ├── test_deployment.py # Deployment testing script
│   ├── init_venv.py       # Virtual environment setup
│   └── clean.py           # Build artifact cleanup
├── src/                   # Source code directory
│   └── ink2tex/           # Main Python package
│       ├── __init__.py    # Package initialization
│       ├── main.py        # Application entry point (ONLY entry point)
│       ├── app.py         # Main application class
│       ├── assets/        # UI assets and resources
│       │   └── README_ICON.txt
│       ├── core/          # Core business logic modules
│       │   ├── __init__.py
│       │   ├── api.py     # Google Gemini API integration
│       │   ├── config.py  # Configuration file management
│       │   ├── hotkey.py  # Global hotkey handling
│       │   └── startup.py # Windows startup management
│       └── ui/            # User interface components
│           ├── __init__.py
│           ├── overlay.py # Transparent drawing overlay
│           ├── preview.py # LaTeX preview widget
│           └── settings.py # Settings window
├── temp/                  # Temporary files directory
│   └── temp_overlay_drawing.png
└── test/                  # Test modules and test files
    ├── test_canvas_features.py
    └── test_startup.py
```

### **Key Architectural Features:**

- **Python Build System**: Cross-platform build automation with robust path handling using `pathlib`
- **Separation of Concerns**: Core logic, UI components, and utilities are clearly separated
- **PyInstaller Compatible**: Prevents import-order errors and packaging issues
- **Lazy Loading**: Heavy dependencies (PyQt6, matplotlib, numpy) imported only when needed
- **Single Entry Point**: Only `main.py` contains the `if __name__ == "__main__"` block
- **Modern Python**: Uses `pyproject.toml` configuration and modular package structure
- **Professional CLI**: Build system uses `--` argument conventions with comprehensive help

## 📦 **Quick Start (Windows)**

### **Option 1: Use the Professional Installer (Recommended)**

1. Download `Ink2TeX_Setup_v1.0.0.exe` from the releases
2. Run the installer (no administrator rights required)
3. Enter your Google Gemini API key during installation or configure later
4. Choose optional features:
   - ✅ Desktop shortcut
   - ✅ Auto-start with Windows
5. Launch from Start Menu - the app runs in your system tray

### **Option 2: Use Portable Executable**

1. Download the portable version from releases
2. Extract to any folder (e.g., `C:\Ink2TeX\`)
3. Get a Google Gemini API key at https://makersuite.google.com/app/apikey
4. Edit the `.api` file in the folder and add your key
5. Double-click `Ink2TeX.exe` to run

### **Option 3: Run from Source (Developers)**

1. Clone the repository:
   ```bash
   git clone https://github.com/Mihai-Solescu/ink2tex.git
   cd ink2tex
   ```

2. Set up development environment:
   ```bash
   python build_wrapper.py --init
   ```

3. Run the application:
   ```bash
   python src/ink2tex/main.py
   ```

*Note: Source code is cross-platform compatible. Only packaging/deployment is Windows-specific currently.*

## 🎯 **How to Use Ink2TeX**

### **Getting Started**

1. **Launch the app**:

   - From Start Menu (if installed)
   - Or double-click `Ink2TeX.exe`
   - Look for the 📝 icon in your system tray

2. **Set up your API key** (first time only):
   - Right-click the tray icon → Status to check if key is configured
   - Edit the `.api` file in your installation folder
   - Add your Google Gemini API key (get one free at <https://makersuite.google.com/>)

### **Drawing Math Equations**

1. **Open the drawing overlay**:
   - Press `Ctrl+Shift+I` anywhere on your computer
   - OR double-click the 📝 tray icon
   - OR right-click tray icon → "Open Overlay"

2. **Draw your equation**:
   - Use your mouse, touchpad, or stylus to draw
   - The overlay covers your entire screen transparently
   - A preview panel appears on the left side

3. **Convert to LaTeX**:
   - Press `Enter` to send your drawing to AI for conversion
   - Wait for the LaTeX result to appear in the preview
   - Press `Esc` to close overlay (LaTeX is copied to clipboard)

### **Tips for Best Results**

- ✅ Write clearly with good spacing between symbols
- ✅ Draw larger rather than smaller (easier for AI to read)
- ✅ Use standard mathematical notation
- ✅ Wait for conversion to complete before drawing more

### **Keyboard Shortcuts**

- `Ctrl+Shift+I`: Open overlay from anywhere
- `Enter`: Convert drawing to LaTeX
- `Esc`: Close overlay (copies result to clipboard)
- `Ctrl+Z`: Undo last stroke

### **System Tray Menu**

Right-click the 📝 icon for options:

- 🖊️ **Open Overlay**: Start drawing
- ℹ️ **About**: Version information
- ⚙️ **Status**: Check API key and hotkey status
- ❌ **Exit**: Close the application

## ⚙️ **Configuration**

### **API Key Setup**

You need a free Google Gemini API key:

1. **Get API key**: Visit <https://makersuite.google.com/app/apikey>
2. **Configure the app**:
   - Find your installation folder (usually `C:\Program Files\Ink2TeX\`)
   - Edit the `.api` file with a text editor
   - Replace the placeholder with your actual API key:

   ```text
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. **Restart the app** to apply changes

### **Settings File (`.config`)**

Advanced users can edit the `.config` file to customize:

- Auto-start behavior
- Hotkey preferences  
- AI prompt customization

## 🔧 **Troubleshooting**

### **Common Issues**

**App won't start / No tray icon**

- Check if running: Look in Task Manager for "Ink2TeX.exe"
- Try running as administrator
- Check antivirus isn't blocking the app

**Hotkey Ctrl+Shift+I doesn't work**

- Make sure app is running (tray icon visible)
- Try clicking tray icon instead
- Some systems need admin privileges for global hotkeys

**"API Error" or conversion fails**

- Check your API key is correct in `.api` file
- Verify internet connection
- Ensure API key has Gemini access (not just other Google services)

**Overlay appears but is blank/black**

- Try pressing Alt+Tab to bring it to front
- Close overlay (Esc) and try again
- Check if other apps are interfering

**No LaTeX result after drawing**

- Make sure you pressed Enter to convert
- Wait longer - AI processing takes a few seconds
- Check Status menu for API configuration

### **Getting Help**

- Right-click tray icon → "Status" for diagnostic info
- Check the console/log for error messages
- Ensure all configuration files are present and valid

## 🏗️ **For Developers**

### **Building from Source**

**Interactive Build Menu (Recommended):**

```batch
# From project root directory - runs full build by default:
build_wrapper.bat

# Or use direct command options:
build_wrapper.bat full        # Full build (executable + installer) [DEFAULT]
build_wrapper.bat exe         # Executable only (faster)
build_wrapper.bat installer   # Installer only
build_wrapper.bat test        # Test deployment
build_wrapper.bat init        # Initialize virtual environment (.venv)
build_wrapper.bat help        # Show help and usage
```

## 🚀 **Build System (Windows)**

Ink2TeX uses a modern Python-based build system with robust path handling. Currently supports Windows with plans for Linux/macOS deployment.

### **Quick Build Commands**

```bash
# Default full build (3-second countdown for cancellation)
python build_wrapper.py

# Specific build commands
python build_wrapper.py --full       # Full build (executable + installer)
python build_wrapper.py --exe        # Executable only (faster)
python build_wrapper.py --installer  # Installer only
python build_wrapper.py --portable   # Portable version
python build_wrapper.py --test       # Test deployment readiness
python build_wrapper.py --init       # Initialize virtual environment
python build_wrapper.py --startup    # Test application startup
python build_wrapper.py --clean      # Clean build artifacts
python build_wrapper.py --help       # Show all available options
```

### **Build System Features**

- ✅ **Python-based automation** (cross-platform scripts)
- ✅ **Robust path handling** using `pathlib` and `PROJECT_ROOT` discovery
- ✅ **Virtual environment management** (`.venv` creation and setup)
- ✅ **Professional CLI** with `--` argument conventions
- ✅ **Windows packaging** (PyInstaller + Inno Setup)
- ❌ **Linux packaging** (planned - AppImage/DEB)
- ❌ **macOS packaging** (planned - DMG)

### **Build Requirements (Windows)**

- Python 3.12+ with pip
- Inno Setup 6 (for Windows installer)
- Virtual environment automatically managed (`.venv`)
- All dependencies automatically installed from `requirements.txt`

### **Platform Status**

- **Windows**: Full production build system
- **Linux/macOS**: Application code compatible, build scripts need implementation

**The build system automatically:**

- Creates and configures `.venv` virtual environment if needed
- Installs all build dependencies from `installer/requirements-build.txt`
- Handles PyInstaller configuration with modular architecture support
- Manages build artifacts and cleanup
- Tests deployment readiness and application startup

### **Build Outputs**

- **Portable executable**: `dist/portable/Ink2TeX.exe` (~100MB)
- **Windows installer**: `dist/installer/Ink2TeX_Setup_v1.0.0.exe` (~101MB)

### **Portable Package Structure**

The portable build creates a complete portable package:

```
dist/portable/
├── Ink2TeX.exe          # Main executable
├── .api                 # API key template (EDIT THIS!)
├── .config              # Application settings
├── prompt.txt           # AI prompt customization
├── setup.bat           # Easy configuration script
└── README.md           # Documentation
```

**For portable use:**
1. Copy the entire `dist/portable/` folder to any location
2. Run `setup.bat` for guided configuration
3. Edit `.api` file with your Google Gemini API key
4. Run `Ink2TeX.exe`

### **Configuration System**

Ink2TeX features an intelligent configuration system that automatically detects deployment mode:

- **🎒 Portable Mode**: Config files next to executable (perfect for USB drives)
- **🏠 Installed Mode**: Config files in platform-specific user directories

**Cross-platform config locations:**
- **Windows**: `%APPDATA%\Ink2TeX\`
- **macOS**: `~/Library/Application Support/Ink2TeX/`
- **Linux**: `~/.config/ink2tex/`

**Configuration files:**
- `.api` - Your Google Gemini API key
- `.config` - Application settings (auto-start, hotkeys, etc.)
- `prompt.txt` - AI behavior customization

The system automatically creates template files with helpful comments for easy setup.

### **Advanced Usage**

```bash
# Initialize environment only
python build_wrapper.py --init

# Test without building
python build_wrapper.py --test
python build_wrapper.py --startup

# Clean before fresh build
python build_wrapper.py --clean
python build_wrapper.py --full

# Manual steps (advanced users):
python scripts/init_venv.py
python scripts/build_exe.py
python scripts/build_installer.py
```
- Creates and configures `.venv` virtual environment if needed
- Installs all build dependencies
- Handles PyInstaller configuration
- No manual dependency management required
- Virtual environment (build_venv recommended)
- Inno Setup 6 (for Windows installer)
- All dependencies in `installer\requirements-build.txt`

**For detailed build instructions:** See `installer/README.md`

### **Development Setup**

1. **Install required packages:**

   ```bash
   pip install PyQt6 google-generativeai matplotlib pillow pynput
   ```

2. **Configure API key:**
   Create a `.api` file in the project directory:

   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Run from source:**

   ```bash
   python app.py
   ```

## Features

- 🖊️ **Transparent Overlay**: Full-screen transparent canvas for drawing math equations
- 🤖 **AI-Powered**: Uses Google Gemini 2.0 Flash Vision for accurate handwriting recognition
- 👁️ **Live Preview**: Real-time LaTeX rendering (loads on first use for faster startup)
- 📋 **Clipboard Integration**: Automatic copying to clipboard
- ⌨️ **Global Hotkeys**: Access from anywhere with Ctrl+Shift+I
- 🔄 **Smart Cropping**: Automatically crops to handwriting bounds
- 🎯 **System Tray**: Runs in background, always available
- ⚡ **Fast Startup**: Optimized initialization for quick overlay access

## Installation

1. **Install required packages:**

   ```bash
   pip install PyQt6 google-generativeai matplotlib pillow pynput
   ```

2. **Configure API key:**
   Create a `.config` file in the project directory:

   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Starting the Application

**Option 1: Double-click the batch file**

```bash
start_ink2tex.bat
```

**Option 2: Run from command line**

```bash
python app.py
```

### Using the Overlay

1. **Open overlay:**
   - Press `Ctrl+Shift+I` anywhere (global hotkey)
   - Double-click the system tray icon
   - Right-click tray icon → "Open Overlay"

2. **Draw your equation:**
   - Draw mathematical expressions on the transparent canvas
   - The left panel shows live preview and edit area

3. **Generate LaTeX:**
   - Press `Enter` to convert handwriting to LaTeX
   - Press `Esc` to close overlay (copies LaTeX to clipboard if available)
   - Press `Ctrl+Z` to undo last drawing stroke

### System Tray Controls

- **Left-click/Double-click**: Open overlay
- **Right-click**: Show context menu
  - 🖊️ Open Overlay
  - ℹ️ About
  - ⚙️ Status
  - ❌ Exit

## Application Architecture

### System Tray Design

The application runs as a background service with:

- **Ink2TeXSystemTrayApp**: Main system tray application class
- **GlobalHotkeyManager**: Handles global keyboard shortcuts (requires pynput)
- **TransparentOverlay**: Full-screen transparent drawing interface

### Key Components

- **Smart Cropping**: Automatically detects handwriting bounds with padding
- **Canvas Management**: Dynamic sizing covering full right side of screen
- **Thread-based Conversion**: Non-blocking AI processing
- **Error Handling**: Graceful fallbacks and user notifications

## Dependencies

### Required

- `PyQt6`: GUI framework and system tray functionality
- `google-generativeai`: Gemini AI API for handwriting recognition
- `matplotlib`: LaTeX rendering and preview
- `Pillow`: Image processing and manipulation

### Optional

- `pynput`: Global hotkey support (Ctrl+Shift+I from anywhere)
  - Without this: Use tray icon to open overlay
  - With this: Use global hotkey or tray icon

## Configuration

### API Setup

1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/)
2. Create `.config` file:

   ```text
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Global Hotkeys

- **Default hotkey**: `Ctrl+Shift+I` (global hotkey via pynput)
- **Fallback**: Double-click system tray icon

## Troubleshooting

### Common Issues

1. **System tray not available**
   - Check if your system supports system tray notifications
   - Some Linux distributions require additional configuration

2. **Global hotkey not working**
   - Ensure the application is running in the system tray
   - Try restarting the application
   - Some systems may require additional permissions for global hotkeys

3. **API errors**
   - Verify `.config` file exists with valid API key
   - Check internet connection
   - Ensure API key has Gemini access

4. **Overlay not appearing**
   - Check if overlay is behind other windows
   - Try Alt+Tab to bring to front
   - Close and reopen overlay

### Status Information

Right-click tray icon → "Status" to see:

- Global hotkey status
- API configuration status
- Available controls and shortcuts

## 🛠️ **Development**

### **Modular Architecture**

The application follows a clean modular architecture:

#### **Core Modules (`src/ink2tex/core/`)**
- `config.py` - Configuration file reading and management
- `startup.py` - Windows startup registry management
- `hotkey.py` - Global hotkey management using pynput
- `api.py` - Google Gemini API integration and threading

#### **UI Modules (`src/ink2tex/ui/`)**
- `overlay.py` - Full-screen transparent drawing overlay
- `preview.py` - LaTeX preview widget using matplotlib
- `settings.py` - Settings window for user preferences

#### **Main Application**
- `main.py` - **ONLY** entry point with multiprocessing setup
- `app.py` - Main application class coordinating all components

### **Development Setup**

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd ink2tex
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -e .
   ```

2. **Run from source**:
   ```bash
   python -m src.ink2tex.main
   # OR use the convenience script
   python run.py
   ```

3. **Test the modular structure**:
   ```bash
   python test_modular.py
   ```

### **Building**

1. **Setup build environment**:
   ```bash
   # First time setup - install build dependencies
   pip install -r installer\requirements-build.txt
   ```

2. **Build executable**:
   ```bash
   # Full build (executable + installer)
   build.bat
   
   # Executable only (faster)
   build_exe.bat
   ```

3. **Output location**:
   - Executable: `dist\portable\Ink2TeX.exe`
   - Installer: `dist\installer\Ink2TeX_Setup_v1.0.0.exe`
   - Build files: `build\`

### **Project Structure**

```text
ink2tex/
├── .api                    # Google Gemini API key configuration
├── .config                 # Application settings and configuration
├── .gitignore             # Git ignore rules
├── build_wrapper.bat      # Interactive build wrapper script
├── prompt.txt             # AI prompt template for handwriting conversion
├── pyproject.toml         # Modern Python project configuration
├── README.md              # This documentation file
├── dist/                  # Build output directory
│   └── portable/          # Portable executable builds
├── docs/                  # Documentation files
│   ├── AUTO_STARTUP_FEATURES.md
│   ├── DEPLOYMENT.md
│   ├── DISTRIBUTION.md
│   └── INSTALLER.md
├── installer/             # PyInstaller and installer configuration
│   ├── ink2tex.spec       # PyInstaller build specification
│   ├── installer.iss      # Inno Setup installer script
│   ├── requirements-build.txt # Build-time dependencies
│   ├── version_info.txt   # Windows executable version information
│   └── hooks/             # PyInstaller custom hooks
│       └── runtime_hook_numpy.py
├── scripts/               # Build automation scripts
│   ├── build.bat          # Complete build (executable + installer)
│   ├── build_exe.bat      # Executable-only build
│   ├── build_installer.bat # Installer-only build
│   └── test_deployment.bat # Deployment testing script
├── src/                   # Source code directory
│   └── ink2tex/           # Main Python package
│       ├── __init__.py    # Package initialization
│       ├── main.py        # Application entry point (ONLY entry point)
│       ├── app.py         # Main application class
│       ├── assets/        # UI assets and resources
│       │   └── README_ICON.txt
│       ├── core/          # Core business logic modules
│       │   ├── __init__.py
│       │   ├── api.py     # Google Gemini API integration
│       │   ├── config.py  # Configuration file management
│       │   ├── hotkey.py  # Global hotkey handling
│       │   └── startup.py # Windows startup management
│       └── ui/            # User interface components
│           ├── __init__.py
│           ├── overlay.py # Transparent drawing overlay
│           ├── preview.py # LaTeX preview widget
│           └── settings.py # Settings window
├── temp/                  # Temporary files directory
│   └── temp_overlay_drawing.png
└── test/                  # Test modules and test files
    ├── test_canvas_features.py
    └── test_startup.py
```

### **Key Design Principles**

1. **Single Entry Point**: Only `main.py` has `if __name__ == "__main__"`
2. **Lazy Imports**: Heavy libraries imported only when needed
3. **Separation of Concerns**: Core logic separate from UI
4. **PyInstaller Compatible**: Prevents multiprocessing and import errors
5. **Testable**: Each module can be tested independently

### **Adding New Features**

1. **Core functionality**: Add to appropriate `core/` module
2. **UI components**: Add to `ui/` module with lazy imports
3. **Configuration**: Use `ConfigReader` class methods
4. **API integration**: Extend `GeminiAPIManager` class
5. **Build system**: Update `installer/requirements-build.txt` if new dependencies added
    └── test_startup.py
```

### **Key Design Principles**

1. **Single Entry Point**: Only `main.py` has `if __name__ == "__main__"`
2. **Lazy Imports**: Heavy libraries imported only when needed
3. **Separation of Concerns**: Core logic separate from UI
4. **PyInstaller Compatible**: Prevents multiprocessing and import errors
5. **Testable**: Each module can be tested independently

### **Adding New Features**

1. **Core functionality**: Add to appropriate `core/` module
2. **UI components**: Add to `ui/` module with lazy imports
3. **Configuration**: Use `ConfigReader` class methods
4. **API integration**: Extend `GeminiAPIManager` class
5. **Build system**: Update `installer/requirements-build.txt` if new dependencies added

## 🎉 **Recent Modernization**

Ink2TeX has been completely modernized with:

### **✅ Python Build System**
- **Eliminated batch file dependencies** for cross-platform compatibility
- **Robust path handling** using `pathlib` and `PROJECT_ROOT` discovery
- **Professional CLI** with `--` argument conventions and comprehensive help
- **Non-blocking execution** (no hanging on user input)

### **✅ Enhanced Development Experience**
- **Automatic virtual environment management** (`.venv` setup and configuration)
- **Comprehensive testing** (deployment readiness, application startup validation)
- **Modern project structure** with `pyproject.toml` configuration
- **Clear separation of concerns** in modular architecture

### **✅ Build Commands**
```bash
python build_wrapper.py          # Default full build with countdown
python build_wrapper.py --exe    # Fast executable-only build
python build_wrapper.py --test   # Comprehensive deployment testing
python build_wrapper.py --startup # GUI application startup validation
python build_wrapper.py --clean  # Intelligent build artifact cleanup
python build_wrapper.py --help   # Complete usage documentation
```

### **✅ Improved Reliability**
- **PyInstaller compatibility** with modular architecture
- **Lazy loading** for faster startup and reduced memory usage
- **Error handling** with descriptive messages and recovery suggestions
- **Path independence** - works from any directory location

This modernization maintains full backward compatibility while providing a significantly improved development and deployment experience!

## License

MIT License - see LICENSE file for details.

## Version History

### v1.0 (Current)

- System tray background application
- Global hotkey support (Ctrl+Shift+I)
- Smart cropping with handwriting detection
- Full-screen transparent overlay
- Live LaTeX preview
- Clipboard integration
