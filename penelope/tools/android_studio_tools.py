"""
Android Studio control tools for Penelope
Allows Penelope to control Android Studio programmatically
"""
import time
import platform
from typing import Optional

def _ensure_android_studio_focused():
    """Ensure Android Studio window is focused"""
    if platform.system() != "Windows":
        return False
    
    try:
        import win32gui
        import win32con
        
        def find_window(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "android studio" in window_text.lower() or "studio" in window_text.lower():
                    ctx.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(find_window, windows)
        
        if windows:
            hwnd = windows[0]
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)
            return True
        return False
    except ImportError:
        # Fallback to pyautogui
        try:
            import pyautogui
            # Try Alt+Tab to switch to Android Studio
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            return True
        except:
            return False
    except Exception:
        return False

def _send_key_combination(*keys):
    """Send a key combination using pyautogui"""
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        time.sleep(0.3)
        return True
    except ImportError:
        return False
    except Exception as e:
        return False

def _type_text(text: str, delay: float = 0.1):
    """Type text using pyautogui"""
    try:
        import pyautogui
        pyautogui.write(text, interval=delay)
        time.sleep(0.3)
        return True
    except ImportError:
        return False
    except Exception as e:
        return False

def control_android_studio(action: str, **kwargs) -> str:
    """
    Control Android Studio programmatically.
    
    Available actions:
    - "new_project": Create a new Android project
    - "open_gemini": Open Gemini AI assistant
    - "open_project": Open an existing project (requires path parameter)
    - "build": Build the current project
    - "run": Run the current project
    - "sync_gradle": Sync Gradle files
    
    Args:
        action: The action to perform
        **kwargs: Additional parameters (e.g., path for open_project)
    
    Returns:
        Status message
    """
    if platform.system() != "Windows":
        return f"Error: Android Studio control only works on Windows. Current system: {platform.system()}"
    
    # Ensure Android Studio is focused
    if not _ensure_android_studio_focused():
        return "Error: Could not find or focus Android Studio window. Please make sure Android Studio is open."
    
    try:
        if action == "new_project":
            # File > New > New Project (Ctrl+Alt+N or File menu)
            # Alternative: Use Ctrl+Shift+A (Find Action) then type "New Project"
            _send_key_combination('ctrl', 'shift', 'a')
            time.sleep(0.5)
            _type_text("New Project")
            time.sleep(0.5)
            _send_key_combination('enter')
            time.sleep(1)
            return "Started new project wizard in Android Studio"
        
        elif action == "open_gemini":
            # Open Gemini AI assistant
            # Method 1: Alt+Shift+A (if assigned) or Ctrl+Shift+A then "Gemini"
            # Method 2: Click on Gemini icon in toolbar (if visible)
            # Method 3: Use Find Action (Ctrl+Shift+A) and search for "Gemini"
            _send_key_combination('ctrl', 'shift', 'a')
            time.sleep(0.5)
            _type_text("Gemini")
            time.sleep(0.5)
            _send_key_combination('enter')
            time.sleep(1)
            return "Opened Gemini AI assistant in Android Studio"
        
        elif action == "open_project":
            # File > Open (Ctrl+O)
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required for open_project action"
            
            _send_key_combination('ctrl', 'o')
            time.sleep(1)
            _type_text(path)
            time.sleep(0.5)
            _send_key_combination('enter')
            time.sleep(1)
            return f"Opened project at {path}"
        
        elif action == "build":
            # Build > Make Project (Ctrl+F9)
            _send_key_combination('ctrl', 'f9')
            time.sleep(0.5)
            return "Started build process"
        
        elif action == "run":
            # Run > Run 'app' (Shift+F10)
            _send_key_combination('shift', 'f10')
            time.sleep(0.5)
            return "Started running the app"
        
        elif action == "sync_gradle":
            # File > Sync Project with Gradle Files (or use notification bar)
            # Try Ctrl+Shift+O (Sync Project) or use Find Action
            _send_key_combination('ctrl', 'shift', 'a')
            time.sleep(0.5)
            _type_text("Sync Project with Gradle Files")
            time.sleep(0.5)
            _send_key_combination('enter')
            time.sleep(1)
            return "Synced project with Gradle files"
        
        elif action == "open_settings":
            # File > Settings (Ctrl+Alt+S)
            _send_key_combination('ctrl', 'alt', 's')
            time.sleep(0.5)
            return "Opened Android Studio settings"
        
        elif action == "open_terminal":
            # View > Tool Windows > Terminal (Alt+F12)
            _send_key_combination('alt', 'f12')
            time.sleep(0.5)
            return "Opened terminal in Android Studio"
        
        else:
            return f"Error: Unknown action '{action}'. Available actions: new_project, open_gemini, open_project, build, run, sync_gradle, open_settings, open_terminal"
    
    except Exception as e:
        return f"Error executing action '{action}': {str(e)}"

def new_android_project(project_name: str = None, template: str = "Empty Activity") -> str:
    """
    Create a new Android project with a wizard.
    This is a simplified version - full automation would require more complex UI interaction.
    """
    if not _ensure_android_studio_focused():
        return "Error: Android Studio is not open or not focused"
    
    try:
        # Start new project wizard
        _send_key_combination('ctrl', 'shift', 'a')
        time.sleep(0.5)
        _type_text("New Project")
        time.sleep(0.5)
        _send_key_combination('enter')
        time.sleep(2)  # Wait for wizard to open
        
        # If project_name provided, type it in the project name field
        if project_name:
            # Tab to project name field (may need adjustment)
            _send_key_combination('tab')
            time.sleep(0.3)
            _type_text(project_name)
            time.sleep(0.5)
        
        return f"Started new Android project wizard (template: {template})"
    except Exception as e:
        return f"Error creating new project: {str(e)}"

def open_gemini_agent() -> str:
    """Open Gemini AI agent in Android Studio"""
    return control_android_studio("open_gemini")

def send_message_to_gemini(message: str) -> str:
    """
    Type a message in Gemini's chat window and send it.
    
    Args:
        message: The message to send to Gemini
    
    Returns:
        Status message
    """
    if platform.system() != "Windows":
        return f"Error: Gemini chat control only works on Windows. Current system: {platform.system()}"
    
    # Ensure Android Studio is focused
    if not _ensure_android_studio_focused():
        return "Error: Could not find or focus Android Studio window. Please make sure Android Studio is open."
    
    try:
        import pyautogui
        
        # Wait a bit for Gemini window to be ready
        time.sleep(1)
        
        # Type the message in the chat input field
        # The chat input should be focused when Gemini is open
        _type_text(message, delay=0.05)
        time.sleep(0.5)
        
        # Send the message (usually Enter key)
        _send_key_combination('enter')
        time.sleep(0.5)
        
        return f"Sent message to Gemini: {message[:50]}..."
    except Exception as e:
        return f"Error sending message to Gemini: {str(e)}"

def type_in_gemini_chat(message: str) -> str:
    """
    Type text in Gemini's chat input field without sending.
    Useful for editing before sending.
    
    Args:
        message: The text to type
    
    Returns:
        Status message
    """
    if platform.system() != "Windows":
        return f"Error: Gemini chat control only works on Windows. Current system: {platform.system()}"
    
    if not _ensure_android_studio_focused():
        return "Error: Could not find or focus Android Studio window. Please make sure Android Studio is open."
    
    try:
        _type_text(message, delay=0.05)
        time.sleep(0.3)
        return f"Typed in Gemini chat: {message[:50]}..."
    except Exception as e:
        return f"Error typing in Gemini chat: {str(e)}"
