# Ink2TeX - Handwritten Math to LaTeX Converter

A system tray application that converts handwritten mathematical equations to LaTeX format using Google's Gemini AI.

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
   pip install PyQt6 google-generativeai matplotlib pillow
   ```

2. **Install optional global hotkey support:**
   ```bash
   python install_optional.py
   ```

3. **Configure API key:**
   Create a `.config` file in the project directory:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Starting the Application

**Option 1: Double-click the batch file**
```
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
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Global Hotkeys
- **Install pynput**: Run `python install_optional.py`
- **Default hotkey**: `Ctrl+Shift+I`
- **Fallback**: Double-click system tray icon

## Troubleshooting

### Common Issues

1. **System tray not available**
   - Check if your system supports system tray notifications
   - Some Linux distributions require additional configuration

2. **Global hotkey not working**
   - Install pynput: `pip install pynput`
   - Some systems may require additional permissions

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
```
ink2tex/
├── app.py                  # Main application
├── start_ink2tex.bat      # Windows launcher
├── install_optional.py    # Optional dependency installer
├── .config               # API key configuration
└── README.md            # This file
```

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
