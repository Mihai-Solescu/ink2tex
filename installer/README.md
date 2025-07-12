# Ink2TeX Deployment System - Complete Guide

This directory contains all files related to building and deploying Ink2TeX. This README explains **exactly** how the two-stage deployment process works.

## 🎯 **The Big Picture: Why Two Tools?**

**Question**: "Does Inno Setup contain the executable produced by PyInstaller?"
**Answer**: **YES!** Inno Setup takes the PyInstaller executable and wraps it in a professional installer.

```text
Python Code → PyInstaller → Standalone EXE → Inno Setup → Professional Installer
    ↓              ↓              ↓              ↓              ↓
  app.py      100MB exe file    Ready to run   Installer EXE   End user runs this
```

## 🏗️ **Stage 1: PyInstaller (Python → Standalone Executable)**

### What PyInstaller Does

1. **Analyzes** your `app.py` and finds ALL dependencies
2. **Bundles** Python interpreter + your code + ALL libraries into ONE file
3. **Creates** `dist\Ink2TeX.exe` (~100MB) that runs WITHOUT Python installed

### How It Works

```python
# ink2tex.spec tells PyInstaller:
data_files = [
    ('../.api', '.'),           # Include .api file INSIDE the .exe
    ('../.config', '.'),        # Include .config file INSIDE the .exe  
    ('../prompt.txt', '.'),     # Include prompt.txt INSIDE the .exe
]
```

### Result After Stage 1

```text
dist/
└── standalone/
    └── Ink2TeX.exe    # 100MB file containing:
                       #   - Python interpreter
                       #   - Your app.py code
                       #   - PyQt6, Pillow, Google AI, etc.
                       #   - .api, .config, prompt.txt (embedded)
```

**At this point**: You could give someone `Ink2TeX.exe` and it would work, but it's just a raw executable file.

## 📦 **Stage 2: Inno Setup (Executable → Professional Installer)**

### What Inno Setup Does

1. **Takes** the `Ink2TeX.exe` file PyInstaller created
2. **Adds** additional files (separate config files users can edit)
3. **Creates** a setup wizard that installs everything properly
4. **Handles** shortcuts, registry entries, uninstaller, etc.

### How Inno Setup Works

```ini
; installer.iss tells Inno Setup:
[Files]
Source: "..\dist\Ink2TeX.exe"   ; Include the PyInstaller executable
Source: "..\.api"               ; Include SEPARATE .api file (user editable)
Source: "..\.config"            ; Include SEPARATE .config file (user editable)
Source: "..\prompt.txt"         ; Include SEPARATE prompt.txt (user editable)
```

### Result After Stage 2

```text
dist/
├── standalone/
│   └── Ink2TeX.exe              # The standalone executable
└── installer/
    └── Ink2TeX_Setup_v1.0.0.exe # 101MB installer containing:
                                 #   - Ink2TeX.exe (the PyInstaller result)
                                 #   - Separate config files
                                 #   - Installation logic
                                 #   - Uninstaller
                                 #   - Shortcut creation
```

## 🔄 **The Complete Flow**

```text
1. USER RUNS: installer\scripts\build_exe.bat
   ┌─────────────────────────────────────────────────┐
   │ PyInstaller reads ink2tex.spec                  │
   │ Analyzes app.py + dependencies                  │
   │ Bundles everything into dist\standalone\Ink2TeX.exe
   └─────────────────────────────────────────────────┘
   
2. USER RUNS: installer\scripts\build_installer.bat
   ┌─────────────────────────────────────────────────┐
   │ Inno Setup reads installer.iss                  │
   │ Takes dist\Ink2TeX.exe (from step 1)            │
   │ Adds separate config files                      │
   │ Creates dist\installer\Ink2TeX_Setup_v1.0.0.exe │
   └─────────────────────────────────────────────────┘
   
3. END USER RUNS: Ink2TeX_Setup_v1.0.0.exe
   ┌─────────────────────────────────────────────────┐
   │ Installation wizard appears                     │
   │ User chooses install location                   │
   │ Files copied to Program Files\Ink2TeX\          │
   │ Shortcuts created in Start Menu                 │
   │ Registry entries added (if auto-start chosen)   │
   │ Uninstaller registered                          │
   └─────────────────────────────────────────────────┘
```

## 📁 **What Gets Installed Where**

When a user runs your installer, they get:

```text
C:\Program Files\Ink2TeX\
├── Ink2TeX.exe         # The PyInstaller executable (contains embedded defaults)
├── .api                # Separate file user can edit (overrides embedded)
├── .config             # Separate file user can edit (overrides embedded)
├── prompt.txt          # Separate file user can edit (overrides embedded)
├── README.md           # Documentation
├── LICENSE.txt         # Auto-generated license
├── INSTALL_NOTES.txt   # Auto-generated setup guide
└── unins000.exe        # Uninstaller
```

## 🧠 **The Smart Strategy**

Your app uses a **fallback system**:

1. **First**: Look for config files NEXT TO the executable (user can edit these)
2. **Fallback**: Use config files EMBEDDED IN the executable (defaults)

This means:

- ✅ App works immediately (embedded defaults)
- ✅ Users can customize settings (external files take priority)
- ✅ If user deletes external files, app still works (falls back to embedded)

## 📋 **Directory Structure**

```text
installer/
├── installer.iss          # Inno Setup script - defines what goes in installer
├── ink2tex.spec           # PyInstaller spec - defines what goes in executable
├── requirements-build.txt # Build dependencies
├── version_info.txt       # Version information for executable
└── scripts/               # Build and deployment scripts
    ├── build.bat          # Master build script (runs both stages)
    ├── build_exe.bat      # Stage 1: Python → Executable
    ├── build_installer.bat # Stage 2: Executable → Installer
    └── test_deployment.bat # Tests deployment readiness
```

## 🚀 **Building Ink2TeX**

**Important**: All build commands should be executed from the project root directory, not from the installer directory.

### Option 1: Complete Build (Recommended)

```batch
# From project root:
build.bat
```

- Runs Stage 1 (PyInstaller)
- Then runs Stage 2 (Inno Setup)
- Creates both executable AND installer

### Option 2: Individual Stages

```batch
# Stage 1 only - Create executable:
installer\scripts\build_exe.bat

# Stage 2 only - Create installer (requires Stage 1 first):
installer\scripts\build_installer.bat
```

### Option 3: Test First

```batch
# Check if everything is ready:
test_deployment.bat
```

## 📊 **Build Outputs**

- **Stage 1 Output**: `dist\standalone\Ink2TeX.exe` (~100MB standalone executable)
- **Stage 2 Output**: `dist\installer\Ink2TeX_Setup_v1.0.0.exe` (~101MB installer)

## 💡 **Why This Approach?**

### Without Inno Setup (PyInstaller only)

❌ Users get a raw .exe file  
❌ No shortcuts  
❌ No uninstaller  
❌ No auto-start option  
❌ Looks unprofessional  

### With Both Tools

✅ Professional installation experience  
✅ Start menu shortcuts  
✅ Proper uninstaller  
✅ Auto-start option  
✅ Registry integration  
✅ User can customize settings  
✅ Fallback to defaults if needed  

## 🛠️ **Requirements**

- Python 3.8+
- Inno Setup 6 (for Windows installer)
- All dependencies listed in `requirements-build.txt`

## 🔧 **Configuration**

The installer includes auto-startup functionality that can be configured:

- During installation via checkbox
- Through the application settings window
- Automatically syncs with Windows registry

## 🐛 **Troubleshooting**

If builds fail, run `test_deployment.bat` to check for missing dependencies or files.

## 📝 **Summary**

**PyInstaller**: Converts Python app → Standalone executable  
**Inno Setup**: Converts executable → Professional installer  
**Result**: End users get a proper Windows installation experience
