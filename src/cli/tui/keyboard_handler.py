import sys
import tty
import termios
from typing import Optional, Callable
from enum import Enum

class KeyCode(Enum):
    """Key codes for special keys"""
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    RIGHT = '\x1b[C'
    LEFT = '\x1b[D'
    ENTER = '\r'
    TAB = '\t'
    ESC = '\x1b'
    SPACE = ' '
    BACKSPACE = '\x7f'
    DELETE = '\x1b[3~'

class KeyboardHandler:
    """Handles keyboard input with arrow key support"""
    
    def __init__(self):
        self.old_settings = None
        self.raw_mode = False
        
    def enable_raw_mode(self):
        """Enable raw keyboard input mode"""
        if not self.raw_mode:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            self.raw_mode = True
    
    def disable_raw_mode(self):
        """Disable raw keyboard input mode"""
        if self.raw_mode and self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            self.raw_mode = False
    
    def get_key(self) -> str:
        """Get a single key press"""
        if not self.raw_mode:
            self.enable_raw_mode()
            
        key = sys.stdin.read(1)
        
        # Handle escape sequences (arrow keys, etc.)
        if key == '\x1b':
            try:
                key += sys.stdin.read(2)
            except:
                pass
        
        return key
    
    def get_key_async(self, timeout: float = 0.1) -> Optional[str]:
        """Get a key with timeout (non-blocking)"""
        import select
        
        if not self.raw_mode:
            self.enable_raw_mode()
            
        if select.select([sys.stdin], [], [], timeout):
            return self.get_key()
        return None
    
    def is_arrow_key(self, key: str) -> bool:
        """Check if key is an arrow key"""
        return key in [KeyCode.UP.value, KeyCode.DOWN.value, KeyCode.LEFT.value, KeyCode.RIGHT.value]
    
    def is_special_key(self, key: str) -> bool:
        """Check if key is a special key"""
        return key in [k.value for k in KeyCode]
    
    def __enter__(self):
        """Context manager entry"""
        self.enable_raw_mode()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disable_raw_mode()

class ContinuousInput:
    """Handles continuous input with real-time updates"""
    
    def __init__(self, prompt: str = "", default: str = "", on_change: Optional[Callable] = None):
        self.prompt = prompt
        self.value = default
        self.cursor_pos = len(default)
        self.on_change = on_change
        self.keyboard = KeyboardHandler()
    
    def run(self) -> str:
        """Run continuous input until Enter is pressed"""
        with self.keyboard:
            while True:
                # Display current state
                self._display()
                
                # Get key input
                key = self.keyboard.get_key()
                
                if key == KeyCode.ENTER.value:
                    break
                elif key == KeyCode.BACKSPACE.value:
                    self._handle_backspace()
                elif key == KeyCode.LEFT.value:
                    self._handle_left()
                elif key == KeyCode.RIGHT.value:
                    self._handle_right()
                elif key == KeyCode.ESC.value:
                    return ""
                elif len(key) == 1 and ord(key) >= 32:  # Printable characters
                    self._handle_char(key)
                
                # Call change callback
                if self.on_change:
                    self.on_change(self.value)
        
        return self.value
    
    def _display(self):
        """Display the current input state"""
        # Clear line and show prompt with value
        sys.stdout.write(f'\r{self.prompt}{self.value}')
        # Position cursor
        if self.cursor_pos < len(self.value):
            sys.stdout.write(f'\r{self.prompt}{self.value[:self.cursor_pos]}')
        sys.stdout.flush()
    
    def _handle_char(self, char: str):
        """Handle character input"""
        self.value = self.value[:self.cursor_pos] + char + self.value[self.cursor_pos:]
        self.cursor_pos += 1
    
    def _handle_backspace(self):
        """Handle backspace"""
        if self.cursor_pos > 0:
            self.value = self.value[:self.cursor_pos-1] + self.value[self.cursor_pos:]
            self.cursor_pos -= 1
    
    def _handle_left(self):
        """Handle left arrow"""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
    
    def _handle_right(self):
        """Handle right arrow"""
        if self.cursor_pos < len(self.value):
            self.cursor_pos += 1

class NavigationHandler:
    """Handles navigation between UI elements"""
    
    def __init__(self, items: list, selected_index: int = 0):
        self.items = items
        self.selected_index = selected_index
        self.max_index = len(items) - 1
    
    def move_up(self):
        """Move selection up"""
        if self.selected_index > 0:
            self.selected_index -= 1
        return self.selected_index
    
    def move_down(self):
        """Move selection down"""
        if self.selected_index < self.max_index:
            self.selected_index += 1
        return self.selected_index
    
    def get_selected_item(self):
        """Get currently selected item"""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def get_selected_index(self):
        """Get selected index"""
        return self.selected_index
    
    def set_selected_index(self, index: int):
        """Set selected index"""
        self.selected_index = max(0, min(index, self.max_index))
