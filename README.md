# Ink2TeX - Handwritten Math to LaTeX Converter

A system tray application that converts handwritten mathematical equations to LaTeX format using Google's Gemini AI.

## 📦 **Quick Start for Users**

### **Option 1: Use the Installer (Recommended)**

1. Download `Ink2TeX_Setup_v1.0.0.exe` from the releases
2. Run the installer and follow the setup wizard
3. Choose optional features:
   - ✅ Desktop shortcut
   - ✅ Auto-start with Windows
4. After installation, the app will be in your Start Menu and system tray

### **Option 2: Use Standalone Executable**

1. Download `Ink2TeX.exe` from the releases
2. Create a folder for the app (e.g., `C:\Ink2TeX\`)
3. Place the executable in the folder
4. Get a Google Gemini API key (see Configuration below)
5. Create configuration files (see Configuration below)
6. Double-click `Ink2TeX.exe` to run

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

**Quick Build (Creates both executable and installer):**

```batch
# From project root directory:
build.bat
```

**Build Outputs:**

- **Standalone executable**: `dist\standalone\Ink2TeX.exe` (~100MB)
- **Windows installer**: `dist\installer\Ink2TeX_Setup_v1.0.0.exe` (~101MB)

**Individual build steps:**

```batch
# Build just the executable:
installer\scripts\build_exe.bat

# Build just the installer (requires executable first):
installer\scripts\build_installer.bat

# Test deployment readiness:
test_deployment.bat
```

**Build Requirements:**

- Python 3.8+
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

## Development

### Project Structure

```text
ink2tex/
├── app.py                  # Main application
├── start_ink2tex.bat      # Windows launcher
├── build.bat              # Master build script
├── .config                # API key configuration
├── temp/                  # Temporary files directory
├── installer/             # Build and deployment files
│   ├── installer.iss      # Inno Setup script
│   ├── ink2tex.spec       # PyInstaller specification
│   └── scripts/           # Build scripts
│       ├── build.bat      # Master build script
│       ├── build_exe.bat  # Executable build script
│       ├── build_installer.bat # Installer build script
│       └── test_deployment.bat # Deployment test script
├── documentation/         # Project documentation
│   ├── AUTO_STARTUP_FEATURES.md
│   ├── DEPLOYMENT.md
│   └── DISTRIBUTION.md
└── README.md             # This file
```

### Building for Distribution

**Simple Build (Recommended):**

```batch
build.bat
```

This creates both a standalone executable and Windows installer with auto-startup functionality.

**Note**: All build commands should be executed from the project root directory. The build scripts are located in `installer\scripts\` but are designed to be called from the base folder.

**For detailed build instructions, see:** `installer/README.md`

### Key Classes

- `Ink2TeXSystemTrayApp`: System tray application manager
- `TransparentOverlay`: Full-screen drawing interface
- `ConversionThread`: Background AI processing
- `GlobalHotkeyManager`: Global keyboard shortcuts

## License

Created with GitHub Copilot assistance.

## Version History

### v1.0 (Current)

- System tray background application
- Global hotkey support (Ctrl+Shift+I)
- Smart cropping with handwriting detection
- Full-screen transparent overlay
- Live LaTeX preview
- Clipboard integration
