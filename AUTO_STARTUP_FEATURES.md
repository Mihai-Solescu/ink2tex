# Auto-Startup Feature for Ink2TeX

## Overview
Ink2TeX now includes auto-startup functionality that allows the application to start automatically when Windows boots. This feature can be configured both during installation and through the application settings.

## Features Added

### 1. Application Settings Window
- **Access**: Right-click system tray icon → "⚙️ Settings"
- **Auto-Start Toggle**: One-click enable/disable auto-startup
- **Real-time Status**: Shows current Windows registry status
- **Configuration Sync**: Automatically syncs settings with config file

### 2. Installation Options
- **Installer Checkbox**: "Start Ink2TeX automatically when Windows starts"
- **Registry Management**: Automatically adds/removes Windows startup entry
- **Config File Update**: Updates `.config` file to match installer selection

### 3. Configuration Management
- **New Setting**: `AUTO_START_WITH_WINDOWS=true/false` in `.config`
- **Registry Sync**: Application syncs config with Windows registry on startup
- **Authoritative Source**: Windows registry is the authoritative source for startup status

## Technical Implementation

### Windows Registry Integration
- **Registry Key**: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- **Value Name**: `Ink2TeX`
- **Value Data**: Full path to executable
- **Auto-cleanup**: Uninstaller automatically removes registry entry

### Settings Window Components
- **Startup Settings Group**: Toggle button for auto-start
- **Visual Feedback**: Button text changes to reflect current state
- **Error Handling**: Graceful failure with user-friendly messages
- **Admin Requirements**: Shows error if registry access fails

### Configuration File Updates
- **Automatic Sync**: App syncs config file with registry status on startup
- **Installer Integration**: Installer updates config file based on user selection
- **Backward Compatibility**: Works with existing config files

## User Experience

### Installation Flow
1. User runs installer
2. Installer shows auto-startup checkbox (unchecked by default)
3. If selected, registry entry is created and config file updated
4. Application starts with correct auto-startup status

### Settings Management
1. Right-click system tray icon → "Settings"
2. Click auto-start toggle button
3. Registry is immediately updated
4. Config file is synchronized
5. Visual feedback confirms change

### Startup Behavior
- If enabled, app starts silently in system tray on Windows boot
- No console window or visible UI
- Global hotkey (Ctrl+Shift+I) immediately available
- Tray icon appears with tooltip indicating ready status

## Error Handling

### Registry Access Issues
- Graceful fallback if registry access denied
- User-friendly error messages
- Suggestion to run as administrator if needed

### Configuration Conflicts
- Registry status is authoritative
- Config file automatically synced on startup
- No user intervention required for minor inconsistencies

## Security Considerations

### Registry Permissions
- Uses `HKEY_CURRENT_USER` (no admin rights required for normal operation)
- Only modifies user-specific startup entries
- Clean uninstallation removes all traces

### Executable Path Security
- Full path stored in registry for security
- Quoted paths prevent injection attacks
- Validates executable exists before enabling

## Testing

### Automated Tests
- `startup_manager.py`: Standalone test module
- Tests enable/disable functionality
- Validates registry operations
- Restores original state after testing

### Manual Testing
1. Install with auto-startup enabled
2. Restart Windows - verify app starts in tray
3. Open Settings → disable auto-startup
4. Restart Windows - verify app doesn't start
5. Re-enable through Settings
6. Uninstall - verify registry entry removed

## Troubleshooting

### Auto-startup Not Working
1. Check if app shows in Task Manager on startup
2. Verify registry entry exists: `WIN+R` → `regedit` → navigate to startup key
3. Try running as administrator
4. Check Windows Startup settings in Task Manager

### Settings Window Issues
1. Ensure app has registry access permissions
2. Check if antivirus is blocking registry modifications
3. Try running app as administrator
4. Verify config file is writable

### Registry Conflicts
1. Manually remove registry entry if needed
2. Delete and recreate through Settings window
3. Check for multiple registry entries with different paths

This feature provides users with a seamless experience while maintaining full control over startup behavior.
