"""
Global hotkey management for Ink2TeX.
Handles system-wide keyboard shortcuts using pynput.
"""

from typing import Optional, Callable

# pynput import with fallback
try:
    import pynput.keyboard as keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class GlobalHotkeyManager:
    """Manages global keyboard shortcuts for system tray app"""
    
    def __init__(self, main_app):
        """Initialize the hotkey manager
        
        Args:
            main_app: Reference to the main application instance
        """
        self.main_app = main_app
        self.enabled = False
        self.hotkey: Optional[keyboard.GlobalHotKeys] = None
        
    def start_listening(self) -> bool:
        """Set up global shortcuts using pynput if available
        
        Returns:
            True if hotkeys were successfully set up, False otherwise
        """
        try:
            if not PYNPUT_AVAILABLE:
                print("pynput not available - global hotkeys disabled")
                return False
                
            def on_hotkey():
                """Handle global hotkey press"""
                self.main_app.open_overlay()
            
            # Set up global hotkey Ctrl+Shift+I
            self.hotkey = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+i': on_hotkey
            })
            self.hotkey.start()
            self.enabled = True
            return True
            
        except ImportError:
            print("pynput not available - global hotkeys disabled")
            return False
        except Exception as e:
            print(f"Failed to setup global hotkey: {e}")
            return False
    
    def stop_listening(self) -> None:
        """Stop listening for global hotkeys"""
        if hasattr(self, 'hotkey') and self.hotkey:
            try:
                self.hotkey.stop()
            except:
                pass
        self.enabled = False
