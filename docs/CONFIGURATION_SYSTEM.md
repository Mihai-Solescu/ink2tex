# Configuration System Design

## Overview

Ink2TeX uses a sophisticated configuration system that supports both **portable** and **installed** deployment modes while maintaining cross-platform compatibility.

## Configuration Strategy

### 1. **Auto-Detection of Deployment Mode**

The application automatically detects whether it's running in:
- **Portable Mode**: Config files next to the executable
- **Installed Mode**: Config files in platform-specific user directories

### 2. **Configuration File Discovery (Priority Order)**

1. **Portable Directory**: Next to executable (highest priority)
2. **User Config Directory**: Platform-specific locations
3. **Fallback**: Current working directory

### 3. **Platform-Specific Config Locations**

| Platform | User Config Directory |
|----------|----------------------|
| **Windows** | `%APPDATA%\Ink2TeX\` |
| **macOS** | `~/Library/Application Support/Ink2TeX/` |
| **Linux** | `~/.config/ink2tex/` |

## Configuration Files

### Core Configuration Files

1. **`.api`** - Google Gemini API key
2. **`.config`** - Application settings
3. **`prompt.txt`** - AI prompt customization

### File Format

Simple key-value format:
```
# Comments start with #
KEY=value
ANOTHER_KEY=another_value
```

## Implementation Architecture

### ConfigManager Class

**Responsibilities:**
- Auto-detect portable vs installed mode
- Discover configuration paths by priority
- Handle cross-platform path differences
- Create default config files when needed

### ConfigReader Class

**Responsibilities:**
- Read configuration values with fallbacks
- Update configuration settings
- Validate API keys
- Handle missing files gracefully

## Deployment Modes

### Portable Version

**Structure:**
```
Ink2TeX-Portable/
├── Ink2TeX.exe          # Main executable
├── .api                 # API key template
├── .config              # Settings template
├── prompt.txt           # AI prompt template
├── setup.bat           # Easy setup script
└── README.md           # Documentation
```

**Benefits:**
- No installation required
- Self-contained
- Easy to move between computers
- Config files travel with the app

### Installed Version

**Structure:**
```
Installation:
  C:\Program Files\Ink2TeX\
  └── Ink2TeX.exe

User Config:
  %APPDATA%\Ink2TeX\
  ├── .api
  ├── .config
  └── prompt.txt
```

**Benefits:**
- Follows OS conventions
- Multiple users can have separate configs
- Configs persist through app updates
- Standard uninstall process

## Cross-Platform Extensibility

### Adding New Platforms

To support a new platform:

1. **Update `_get_user_config_directory()`:**
   ```python
   elif sys.platform == "new_platform":
       return Path.home() / ".new_platform_config_dir" / "ink2tex"
   ```

2. **Test configuration discovery:**
   - Verify path creation
   - Test file permissions
   - Validate read/write access

### Configuration Schema Extension

To add new configuration options:

1. **Update default templates** in `create_default_config_files()`
2. **Add validation logic** in `ConfigReader`
3. **Update documentation** and examples

## Usage Examples

### Reading Configuration

```python
from ink2tex.core.config import ConfigReader

# Read API key (automatically finds the file)
api_key = ConfigReader.read_api_key_from_config()

# Read app setting with default
auto_start = ConfigReader.read_config_value('AUTO_START', default='false')

# Read custom prompt
prompt = ConfigReader.read_prompt_from_file()
```

### Writing Configuration

```python
# Update a setting (writes to appropriate location)
ConfigReader.update_config_setting('AUTO_START', 'true')
```

### Getting Configuration Info

```python
# Get detailed config status
config_info = ConfigReader.get_config_info()
print(f"Mode: {'Portable' if config_info['is_portable'] else 'Installed'}")
print(f"Config directory: {config_info['writable_config_dir']}")
```

## Setup Tools

### Automated Setup Script

`scripts/setup_config.py` provides:
- Configuration status overview
- Missing file detection
- Default file creation
- API key validation
- Platform-specific guidance

### Portable Setup Script

`setup.bat` (included with portable version):
- User-friendly configuration wizard
- Direct access to config file editing
- Clear setup instructions

## Error Handling

### Graceful Degradation

1. **Missing API key**: Clear error message with setup instructions
2. **Missing config files**: Auto-creation with templates
3. **Invalid values**: Fallback to sensible defaults
4. **Permission issues**: Clear error messages and alternative paths

### User Feedback

- **Descriptive error messages** with actionable solutions
- **Auto-detection** of common configuration issues
- **Setup guidance** for first-time users

## Security Considerations

1. **API key protection**: Files are created with appropriate permissions
2. **No sensitive defaults**: Templates contain placeholder values
3. **Path validation**: Prevents directory traversal attacks
4. **Safe file operations**: Atomic writes and backup handling

## Testing Strategy

### Automated Tests

- **Cross-platform path generation**
- **File discovery priority**
- **Default file creation**
- **Mode detection accuracy**

### Manual Testing

- **Portable deployment** on clean systems
- **Installed deployment** with multiple users
- **Cross-platform behavior** on different OSes
- **Upgrade scenarios** with existing configs

## Future Enhancements

### Planned Features

1. **GUI configuration editor** for non-technical users
2. **Configuration backup/restore** functionality
3. **Cloud sync integration** for settings
4. **Configuration validation** with schema checking
5. **Migration tools** for upgrading config formats

This design provides a robust, extensible foundation for configuration management that scales from simple portable apps to complex multi-user installations across different platforms.
