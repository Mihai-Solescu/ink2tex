# Ink2TeX Deployment Guide

This guide explains how to create a distributable version of Ink2TeX that users can install with a single click.

## 🚀 Quick Start for Developers

### 1. Build the Executable
```bash
# Run the build script
build_exe.bat
```
This creates `dist/Ink2TeX.exe` - a standalone executable with all dependencies bundled.

### 2. Create the Installer (Optional but Recommended)
```bash
# First install Inno Setup from: https://jrsoftware.org/isinfo.php
# Then run:
build_installer.bat
```
This creates `installer/Ink2TeX_Setup_v1.0.0.exe` - a professional Windows installer.

## 📦 What Users Get

### Option A: Standalone Executable
- **File**: `Ink2TeX.exe` (~150-200MB)
- **Installation**: Just download and run
- **Configuration**: Users need to edit `.api` file with their Google API key

### Option B: Professional Installer (Recommended)
- **File**: `Ink2TeX_Setup_v1.0.0.exe` (~80-120MB compressed)
- **Installation**: Double-click to install with wizard
- **Features**:
  - ✅ Start menu shortcuts
  - ✅ Optional desktop icon  
  - ✅ Optional auto-start with Windows
  - ✅ Professional uninstaller
  - ✅ Installation notes and license
  - ✅ Automatic file associations

## 🛠 Technical Details

### Build Process
1. **PyInstaller** bundles Python + dependencies into a single .exe
2. **Inno Setup** creates a Windows installer around the executable
3. All configuration files are included and properly deployed

### File Structure After Installation
```
C:\Program Files\Ink2TeX\
├── Ink2TeX.exe          # Main application
├── .api                 # Google API key (user must configure)
├── .config             # Application settings
├── prompt.txt          # AI prompt for conversion
├── README.md           # Documentation
├── LICENSE.txt         # Software license
└── INSTALL_NOTES.txt   # Setup instructions
```

### Dependencies Bundled
- PyQt6 (GUI framework)
- Google Generative AI (Gemini API)
- Pillow (Image processing)
- Matplotlib (LaTeX rendering)
- pynput (Global hotkeys)
- All Python standard library modules

## 🎯 User Experience

### First-Time Setup
1. **Download** installer from your distribution site
2. **Run** `Ink2TeX_Setup_v1.0.0.exe`
3. **Follow** installation wizard
4. **Get** Google API key from https://makersuite.google.com/app/apikey
5. **Edit** `.api` file in installation folder
6. **Launch** Ink2TeX from Start menu

### Daily Usage
1. **Press** `Ctrl+Shift+I` anywhere to open overlay
2. **Draw** math equations
3. **Press** `Enter` to convert to LaTeX
4. **Copy** result to clipboard or view preview

## 🔧 Advanced Configuration

### Customizing the Build

#### Add Application Icon
1. Create `assets/icon.ico` (256x256 recommended)
2. The build script will automatically include it

#### Modify Version Info
Edit `version_info.txt` to change:
- Version numbers
- Company name
- Copyright information
- Product description

#### Customize Installer
Edit `installer.iss` to modify:
- Installation options
- File associations
- Registry entries
- Custom actions

### Build Requirements
- **Python 3.8+** with pip
- **PyInstaller 6.0+** for executable creation
- **Inno Setup 6.0+** for installer creation (optional)
- **Windows 10+** for building and testing

## 📋 Distribution Checklist

Before releasing to users:

- [ ] Test executable on clean Windows machine
- [ ] Verify all configuration files are included
- [ ] Test installer and uninstaller
- [ ] Create user documentation
- [ ] Set up download/hosting location
- [ ] Test with different API keys
- [ ] Verify hotkeys work system-wide
- [ ] Check antivirus compatibility

## 🚨 Known Issues & Solutions

### Antivirus False Positives
- **Issue**: Some antivirus software flags PyInstaller executables
- **Solution**: Submit to antivirus vendors for whitelisting, or sign the executable

### Large File Size
- **Issue**: Executable is ~150-200MB due to bundled dependencies
- **Solution**: This is normal for PyQt6 applications. Installer compresses to ~80-120MB

### API Key Security
- **Issue**: API key is stored in plain text
- **Solution**: Users should keep `.api` file secure and not share it

## 📈 Future Improvements

Potential enhancements for distribution:
- Code signing certificate for trusted installation
- Auto-updater functionality
- Multiple language support in installer
- Cloud-based configuration sync
- Portable mode (no installation required)
