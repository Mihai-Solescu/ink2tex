# 📦 Ink2TeX Distribution Package

## For End Users

### Installation (Recommended Method)
1. Download `Ink2TeX_Setup_v1.0.0.exe`
2. Run the installer and follow the setup wizard
3. Get your free Google API key at: https://makersuite.google.com/app/apikey
4. Open the installed folder and edit `.api` file with your key
5. Launch Ink2TeX from Start menu

### Usage
- Press `Ctrl+Shift+I` anywhere to open drawing overlay
- Draw math equations with mouse or stylus  
- Press `Enter` to convert to LaTeX
- Press `Esc` to close overlay
- Right-click system tray icon for options

### Uninstallation
- Use "Add or Remove Programs" in Windows Settings
- Or use the uninstaller in Start menu

## For Developers

### Build Commands
```bash
# Create standalone executable
build_exe.bat

# Create Windows installer (requires Inno Setup)
build_installer.bat
```

### What You Get
- `dist/Ink2TeX.exe` - Standalone executable (~150-200MB)
- `installer/Ink2TeX_Setup_v1.0.0.exe` - Professional installer (~80-120MB)

Both options provide a complete, dependency-free installation for end users.
