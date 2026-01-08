"""
IDE and Development Tools Control for Penelope
Provides unified interface for controlling various IDEs and development tools
"""
import subprocess
import os
import time
import platform
from typing import Optional, Dict, Any
from pathlib import Path

def _ensure_app_focused(app_name: str) -> bool:
    """Ensure an application window is focused"""
    if platform.system() != "Windows":
        return False
    
    try:
        import win32gui
        import win32con
        
        def find_window(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if app_name.lower() in window_text.lower():
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
        try:
            import pyautogui
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

# ============================================================================
# CURSOR IDE CONTROL
# ============================================================================

def control_cursor(action: str, **kwargs) -> str:
    """
    Control Cursor IDE programmatically.

    Available actions:
    - "open_project": Open a project/folder (requires path)
    - "open_file": Open a specific file (requires path)
    - "new_file": Create a new file (requires path, optional content)
    - "open_terminal": Open integrated terminal
    - "open_composer": Open Cursor Composer (AI chat)
    - "send_to_composer": Send message to Composer (requires message)
    - "run_command": Run command in terminal (requires command)
    - "search_replace": Search and replace in current file
    - "goto_line": Go to specific line number
    - "format_document": Format current document
    - "save_file": Save current file
    - "close_file": Close current file
    - "find_in_files": Search across all files
    - "toggle_sidebar": Toggle sidebar visibility
    - "command_palette": Open command palette
    - "git_status": Show git status
    - "git_commit": Commit changes
    """
    if platform.system() != "Windows":
        return f"Error: Cursor control only works on Windows"

    cursor_path = r"C:\Users\Ilja\AppData\Local\Programs\cursor\Cursor.exe"

    try:
        if action == "open_project":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened Cursor with project: {path}"

        elif action == "open_file":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened file in Cursor: {path}"

        elif action == "new_file":
            path = kwargs.get("path", "")
            content = kwargs.get("content", "")
            if not path:
                return "Error: path parameter required"

            # Create file first, then open in Cursor
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if content:
                p.write_text(content, encoding="utf-8")
            else:
                p.touch()

            subprocess.Popen([cursor_path, path])
            return f"Created and opened new file: {path}"

        elif action == "open_terminal":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', '`')  # Toggle terminal
            return "Opened terminal in Cursor"

        elif action == "open_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'i')  # Open Composer
            time.sleep(1)
            return "Opened Cursor Composer"

        elif action == "send_to_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            message = kwargs.get("message", "")
            if not message:
                return "Error: message parameter required"

            # Open Composer first
            _send_key_combination('ctrl', 'shift', 'i')
            time.sleep(1)
            _type_text(message, delay=0.05)
            time.sleep(0.5)
            _send_key_combination('enter')
            return f"Sent message to Cursor Composer: {message[:50]}..."

        elif action == "run_command":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            command = kwargs.get("command", "")
            if not command:
                return "Error: command parameter required"

            # Open terminal and run command
            _send_key_combination('ctrl', '`')
            time.sleep(0.5)
            _type_text(command, delay=0.05)
            _send_key_combination('enter')
            return f"Ran command in Cursor terminal: {command}"

        elif action == "search_replace":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            old_text = kwargs.get("old_text", "")
            new_text = kwargs.get("new_text", "")
            if not old_text:
                return "Error: old_text parameter required"

            _send_key_combination('ctrl', 'h')  # Open replace dialog
            time.sleep(0.5)
            _type_text(old_text)
            time.sleep(0.3)
            _send_key_combination('tab')  # Move to replace field
            _type_text(new_text)
            time.sleep(0.3)
            _send_key_combination('enter')  # Execute replace
            return f"Replaced '{old_text}' with '{new_text}'"

        elif action == "goto_line":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            line_number = kwargs.get("line", 1)
            _send_key_combination('ctrl', 'g')  # Go to line
            time.sleep(0.5)
            _type_text(str(line_number))
            _send_key_combination('enter')
            return f"Jumped to line {line_number}"

        elif action == "format_document":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('shift', 'alt', 'f')  # Format document
            return "Formatted current document"

        elif action == "save_file":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 's')  # Save file
            return "Saved current file"

        elif action == "close_file":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'w')  # Close file
            return "Closed current file"

        elif action == "find_in_files":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            search_text = kwargs.get("query", "")
            if not search_text:
                return "Error: query parameter required"
            _send_key_combination('ctrl', 'shift', 'f')  # Find in files
            time.sleep(0.5)
            _type_text(search_text)
            _send_key_combination('enter')
            return f"Searched for '{search_text}' in all files"

        elif action == "toggle_sidebar":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'b')  # Toggle sidebar
            return "Toggled sidebar visibility"

        elif action == "command_palette":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'p')  # Command palette
            return "Opened command palette"

        elif action == "git_status":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(0.5)
            return "Opened Git status view"

        elif action == "git_commit":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            message = kwargs.get("message", "Auto commit")
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(1)
            _send_key_combination('ctrl', 'enter')  # Commit
            time.sleep(0.5)
            _type_text(message)
            _send_key_combination('ctrl', 'enter')
            return f"Committed with message: {message}"

        else:
            available_actions = [
                "open_project", "open_file", "new_file", "open_terminal",
                "open_composer", "send_to_composer", "run_command",
                "search_replace", "goto_line", "format_document", "save_file",
                "close_file", "find_in_files", "toggle_sidebar", "command_palette",
                "git_status", "git_commit"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing Cursor action '{action}': {str(e)}"
    """
    Control Cursor IDE programmatically.

    Available actions:
    - "open_project": Open a project/folder (requires path)
    - "open_file": Open a specific file (requires path)
    - "new_file": Create a new file (requires path, optional content)
    - "open_terminal": Open integrated terminal
    - "open_composer": Open Cursor Composer (AI chat)
    - "send_to_composer": Send message to Composer (requires message)
    - "run_command": Run command in terminal (requires command)
    - "search_replace": Search and replace in current file
    - "goto_line": Go to specific line number
    - "format_document": Format current document
    - "save_file": Save current file
    - "close_file": Close current file
    - "find_in_files": Search across all files
    - "toggle_sidebar": Toggle sidebar visibility
    - "command_palette": Open command palette
    - "git_status": Show git status
    - "git_commit": Commit changes
    """
    if platform.system() != "Windows":
        return f"Error: Cursor control only works on Windows"

    cursor_path = r"C:\Users\Ilja\AppData\Local\Programs\cursor\Cursor.exe"

    try:
        if action == "open_project":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened Cursor with project: {path}"

        elif action == "open_file":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened file in Cursor: {path}"

        elif action == "new_file":
            path = kwargs.get("path", "")
            content = kwargs.get("content", "")
            if not path:
                return "Error: path parameter required"

            # Create file first, then open in Cursor
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if content:
                p.write_text(content, encoding="utf-8")
            else:
                p.touch()

            subprocess.Popen([cursor_path, path])
            return f"Created and opened new file: {path}"

        elif action == "open_terminal":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', '`')  # Toggle terminal
            return "Opened terminal in Cursor"

        elif action == "open_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'i')  # Open Composer
            time.sleep(1)
            return "Opened Cursor Composer"

        elif action == "send_to_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            message = kwargs.get("message", "")
            if not message:
                return "Error: message parameter required"

            # Open Composer first
            _send_key_combination('ctrl', 'shift', 'i')
            time.sleep(1)
            _type_text(message, delay=0.05)
            time.sleep(0.5)
            _send_key_combination('enter')
            return f"Sent message to Cursor Composer: {message[:50]}..."

        elif action == "run_command":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            command = kwargs.get("command", "")
            if not command:
                return "Error: command parameter required"

            # Open terminal and run command
            _send_key_combination('ctrl', '`')
            time.sleep(0.5)
            _type_text(command, delay=0.05)
            _send_key_combination('enter')
            return f"Ran command in Cursor terminal: {command}"

        elif action == "search_replace":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            old_text = kwargs.get("old_text", "")
            new_text = kwargs.get("new_text", "")
            if not old_text:
                return "Error: old_text parameter required"

            _send_key_combination('ctrl', 'h')  # Open replace dialog
            time.sleep(0.5)
            _type_text(old_text)
            time.sleep(0.3)
            _send_key_combination('tab')  # Move to replace field
            _type_text(new_text)
            time.sleep(0.3)
            _send_key_combination('enter')  # Execute replace
            return f"Replaced '{old_text}' with '{new_text}'"

        elif action == "goto_line":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            line_number = kwargs.get("line", 1)
            _send_key_combination('ctrl', 'g')  # Go to line
            time.sleep(0.5)
            _type_text(str(line_number))
            _send_key_combination('enter')
            return f"Jumped to line {line_number}"

        elif action == "format_document":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('shift', 'alt', 'f')  # Format document
            return "Formatted current document"

        elif action == "save_file":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 's')  # Save file
            return "Saved current file"

        elif action == "close_file":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'w')  # Close file
            return "Closed current file"

        elif action == "find_in_files":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            search_text = kwargs.get("query", "")
            if not search_text:
                return "Error: query parameter required"
            _send_key_combination('ctrl', 'shift', 'f')  # Find in files
            time.sleep(0.5)
            _type_text(search_text)
            _send_key_combination('enter')
            return f"Searched for '{search_text}' in all files"

        elif action == "toggle_sidebar":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'b')  # Toggle sidebar
            return "Toggled sidebar visibility"

        elif action == "command_palette":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'p')  # Command palette
            return "Opened command palette"

        elif action == "git_status":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(0.5)
            return "Opened Git status view"

        elif action == "git_commit":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            message = kwargs.get("message", "Auto commit")
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(1)
            _send_key_combination('ctrl', 'enter')  # Commit
            time.sleep(0.5)
            _type_text(message)
            _send_key_combination('ctrl', 'enter')
            return f"Committed with message: {message}"

        else:
            available_actions = [
                "open_project", "open_file", "new_file", "open_terminal",
                "open_composer", "send_to_composer", "run_command",
                "search_replace", "goto_line", "format_document", "save_file",
                "close_file", "find_in_files", "toggle_sidebar", "command_palette",
                "git_status", "git_commit"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing Cursor action '{action}': {str(e)}"

# ============================================================================
# VS CODE CONTROL
# ============================================================================

def control_vscode(action: str, **kwargs) -> str:
    """
    Control Visual Studio Code programmatically.

    Available actions:
    - "open_project": Open a project/folder (requires path)
    - "open_file": Open a specific file (requires path)
    - "open_terminal": Open integrated terminal
    - "run_command": Run command in terminal (requires command)
    - "search_replace": Search and replace in current file
    - "goto_line": Go to specific line number
    - "format_document": Format current document
    - "save_file": Save current file
    - "close_file": Close current file
    - "find_in_files": Search across all files
    - "toggle_sidebar": Toggle sidebar visibility
    - "command_palette": Open command palette
    - "install_extension": Install VS Code extension
    - "git_status": Show git status
    - "git_commit": Commit changes
    - "debug_start": Start debugging
    - "debug_stop": Stop debugging
    """
    if platform.system() != "Windows":
        return f"Error: VS Code control only works on Windows"

    try:
        if action == "open_project":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen(["code", path])
            return f"Opened VS Code with project: {path}"

        elif action == "open_file":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen(["code", path])
            return f"Opened file in VS Code: {path}"

        elif action == "open_terminal":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', '`')
            return "Opened terminal in VS Code"

        elif action == "run_command":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            command = kwargs.get("command", "")
            if not command:
                return "Error: command parameter required"

            _send_key_combination('ctrl', '`')
            time.sleep(0.5)
            _type_text(command, delay=0.05)
            _send_key_combination('enter')
            return f"Ran command in VS Code terminal: {command}"

        elif action == "search_replace":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            old_text = kwargs.get("old_text", "")
            new_text = kwargs.get("new_text", "")
            if not old_text:
                return "Error: old_text parameter required"

            _send_key_combination('ctrl', 'h')  # Open replace dialog
            time.sleep(0.5)
            _type_text(old_text)
            time.sleep(0.3)
            _send_key_combination('tab')  # Move to replace field
            _type_text(new_text)
            time.sleep(0.3)
            _send_key_combination('enter')  # Execute replace
            return f"Replaced '{old_text}' with '{new_text}'"

        elif action == "goto_line":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            line_number = kwargs.get("line", 1)
            _send_key_combination('ctrl', 'g')  # Go to line
            time.sleep(0.5)
            _type_text(str(line_number))
            _send_key_combination('enter')
            return f"Jumped to line {line_number}"

        elif action == "format_document":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('shift', 'alt', 'f')  # Format document
            return "Formatted current document"

        elif action == "save_file":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', 's')  # Save file
            return "Saved current file"

        elif action == "close_file":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', 'w')  # Close file
            return "Closed current file"

        elif action == "find_in_files":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            search_text = kwargs.get("query", "")
            if not search_text:
                return "Error: query parameter required"
            _send_key_combination('ctrl', 'shift', 'f')  # Find in files
            time.sleep(0.5)
            _type_text(search_text)
            _send_key_combination('enter')
            return f"Searched for '{search_text}' in all files"

        elif action == "toggle_sidebar":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', 'b')  # Toggle sidebar
            return "Toggled sidebar visibility"

        elif action == "command_palette":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'p')  # Command palette
            return "Opened command palette"

        elif action == "install_extension":
            extension_id = kwargs.get("extension", "")
            if not extension_id:
                return "Error: extension parameter required"

            # Use command line to install extension
            result = subprocess.run(
                ["code", "--install-extension", extension_id],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or f"Installed extension: {extension_id}"

        elif action == "git_status":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(0.5)
            return "Opened Git status view"

        elif action == "git_commit":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            message = kwargs.get("message", "Auto commit")
            _send_key_combination('ctrl', 'shift', 'g')  # Git view
            time.sleep(1)
            _send_key_combination('ctrl', 'enter')  # Commit
            time.sleep(0.5)
            _type_text(message)
            _send_key_combination('ctrl', 'enter')
            return f"Committed with message: {message}"

        elif action == "debug_start":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('f5')  # Start debugging
            return "Started debugging session"

        elif action == "debug_stop":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('shift', 'f5')  # Stop debugging
            return "Stopped debugging session"

        else:
            available_actions = [
                "open_project", "open_file", "open_terminal", "run_command",
                "search_replace", "goto_line", "format_document", "save_file",
                "close_file", "find_in_files", "toggle_sidebar", "command_palette",
                "install_extension", "git_status", "git_commit", "debug_start", "debug_stop"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing VS Code action '{action}': {str(e)}"

# ============================================================================
# GIT CONTROL
# ============================================================================

def control_git(action: str, **kwargs) -> str:
    """
    Control Git operations programmatically.
    
    Available actions:
    - "init": Initialize a new repository (requires path)
    - "status": Check repository status (requires path)
    - "add": Add files to staging (requires path, optional files)
    - "commit": Make a commit (requires path, message)
    - "push": Push to remote (requires path)
    - "pull": Pull from remote (requires path)
    - "branch": List/create branches (requires path, optional branch_name)
    - "log": Show commit log (requires path)
    """
    try:
        path = kwargs.get("path", ".")
        cwd = Path(path).resolve() if path else Path.cwd()
        
        if action == "init":
            result = subprocess.run(
                ["git", "init"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or "Repository initialized"
        
        elif action == "status":
            result = subprocess.run(
                ["git", "status"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr or "Status checked"
        
        elif action == "add":
            files = kwargs.get("files", ".")
            result = subprocess.run(
                ["git", "add", files] if files != "." else ["git", "add", "."],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or f"Added {files} to staging"
        
        elif action == "commit":
            message = kwargs.get("message", "")
            if not message:
                return "Error: message parameter required for commit"
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or f"Committed: {message}"
        
        elif action == "push":
            result = subprocess.run(
                ["git", "push"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or "Pushed to remote"
        
        elif action == "pull":
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or "Pulled from remote"
        
        elif action == "branch":
            branch_name = kwargs.get("branch_name", "")
            if branch_name:
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout or f"Created and switched to branch: {branch_name}"
            else:
                result = subprocess.run(
                    ["git", "branch"],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout or "Listed branches"
        
        elif action == "log":
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or "No commits found"
        
        else:
            return f"Error: Unknown action '{action}'. Available: init, status, add, commit, push, pull, branch, log"
    
    except Exception as e:
        return f"Error executing Git action '{action}': {str(e)}"

# ============================================================================
# PYTHON DEVELOPMENT TOOLS
# ============================================================================

def control_python(action: str, **kwargs) -> str:
    """
    Control Python development operations.

    Available actions:
    - "run_script": Run a Python script (requires path)
    - "install_package": Install a package via pip (requires package)
    - "run_tests": Run pytest tests (requires path)
    - "create_venv": Create virtual environment (requires path)
    - "check_syntax": Check Python syntax (requires path)
    - "install_requirements": Install from requirements.txt
    - "create_package": Create Python package structure
    - "run_linter": Run flake8 or pylint
    - "generate_docs": Generate documentation with sphinx
    - "profile_code": Profile Python code performance
    - "debug_script": Run script with debugger
    - "create_test": Generate unit test template
    """
    try:
        if action == "run_script":
            script_path = kwargs.get("path", "")
            if not script_path:
                return "Error: path parameter required"
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Script executed"

        elif action == "install_package":
            package = kwargs.get("package", "")
            if not package:
                return "Error: package parameter required"
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Installed {package}"

        elif action == "run_tests":
            test_path = kwargs.get("path", ".")
            result = subprocess.run(
                ["pytest", test_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Tests executed"

        elif action == "create_venv":
            venv_path = kwargs.get("path", "venv")
            result = subprocess.run(
                ["python", "-m", "venv", venv_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or f"Created virtual environment: {venv_path}"

        elif action == "check_syntax":
            file_path = kwargs.get("path", "")
            if not file_path:
                return "Error: path parameter required"
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return f"Syntax check passed for {file_path}"
            else:
                return f"Syntax errors in {file_path}: {result.stderr}"

        elif action == "install_requirements":
            req_file = kwargs.get("path", "requirements.txt")
            if not os.path.exists(req_file):
                return f"Error: {req_file} not found"
            result = subprocess.run(
                ["pip", "install", "-r", req_file],
                capture_output=True,
                text=True,
                timeout=600
            )
            return result.stdout or result.stderr or f"Installed requirements from {req_file}"

        elif action == "create_package":
            package_name = kwargs.get("name", "")
            if not package_name:
                return "Error: name parameter required"

            # Create package structure
            os.makedirs(package_name, exist_ok=True)
            os.makedirs(f"{package_name}/tests", exist_ok=True)

            # Create __init__.py
            with open(f"{package_name}/__init__.py", "w") as f:
                f.write(f'"""Package: {package_name}"""\n\n__version__ = "0.1.0"\n')

            # Create setup.py
            with open(f"{package_name}/setup.py", "w") as f:
                f.write(f'''"""Setup script for {package_name}"""

from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)
''')

            # Create README
            with open(f"{package_name}/README.md", "w") as f:
                f.write(f"# {package_name}\n\nPython package for {package_name} functionality.\n")

            return f"Created Python package structure for '{package_name}'"

        elif action == "run_linter":
            file_path = kwargs.get("path", ".")
            linter = kwargs.get("linter", "flake8")

            if linter == "flake8":
                result = subprocess.run(
                    ["flake8", file_path],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            elif linter == "pylint":
                result = subprocess.run(
                    ["pylint", file_path],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            else:
                return f"Error: Unknown linter '{linter}'. Use 'flake8' or 'pylint'"

            return result.stdout or result.stderr or f"Linted {file_path} with {linter}"

        elif action == "generate_docs":
            docs_dir = kwargs.get("path", "docs")
            if not os.path.exists("setup.py") and not os.path.exists("pyproject.toml"):
                return "Error: No Python project found (setup.py or pyproject.toml required)"

            # Create docs directory
            os.makedirs(docs_dir, exist_ok=True)

            # Generate basic Sphinx docs
            result = subprocess.run(
                ["sphinx-quickstart", docs_dir, "--quiet", "--project", "MyProject",
                 "--author", "Author", "--version", "0.1", "--release", "0.1"],
                capture_output=True,
                text=True,
                timeout=60
            )

            return f"Generated documentation structure in {docs_dir}"

        elif action == "profile_code":
            script_path = kwargs.get("path", "")
            if not script_path:
                return "Error: path parameter required"

            result = subprocess.run(
                ["python", "-m", "cProfile", script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Profiled {script_path}"

        elif action == "debug_script":
            script_path = kwargs.get("path", "")
            if not script_path:
                return "Error: path parameter required"

            result = subprocess.run(
                ["python", "-m", "pdb", script_path],
                capture_output=True,
                text=True,
                timeout=300,
                input="c\n"  # Continue execution
            )
            return result.stdout or result.stderr or f"Debugged {script_path}"

        elif action == "create_test":
            test_name = kwargs.get("name", "test_example")
            target_dir = kwargs.get("path", "tests")

            os.makedirs(target_dir, exist_ok=True)

            test_content = f'''"""Unit tests for {test_name}"""

import unittest


class Test{test_name.title()}(unittest.TestCase):
    """Test cases for {test_name}"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_example(self):
        """Example test case"""
        self.assertTrue(True)

    def tearDown(self):
        """Clean up test fixtures"""
        pass


if __name__ == "__main__":
    unittest.main()
'''

            test_file = f"{target_dir}/test_{test_name}.py"
            with open(test_file, "w") as f:
                f.write(test_content)

            return f"Created unit test template: {test_file}"

        else:
            available_actions = [
                "run_script", "install_package", "run_tests", "create_venv",
                "check_syntax", "install_requirements", "create_package",
                "run_linter", "generate_docs", "profile_code", "debug_script",
                "create_test"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing Python action '{action}': {str(e)}"

# ============================================================================
# NODE.JS / NPM CONTROL
# ============================================================================

def control_npm(action: str, **kwargs) -> str:
    """
    Control Node.js/npm operations.

    Available actions:
    - "init": Initialize npm project (requires path)
    - "install": Install packages (requires path, optional package)
    - "run_script": Run npm script (requires path, script_name)
    - "build": Run build script (requires path)
    - "start": Start development server
    - "test": Run test suite
    - "lint": Run linting
    - "format": Format code
    - "create_react_app": Create new React app
    - "add_dependency": Add npm dependency
    - "remove_dependency": Remove npm dependency
    - "update_dependencies": Update all dependencies
    - "audit": Run security audit
    - "publish": Publish package to npm
    """
    try:
        path = kwargs.get("path", ".")
        cwd = Path(path).resolve() if path else Path.cwd()

        if action == "init":
            result = subprocess.run(
                ["npm", "init", "-y"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or "Initialized npm project"

        elif action == "install":
            package = kwargs.get("package", "")
            dev = kwargs.get("dev", False)
            global_install = kwargs.get("global", False)

            cmd = ["npm", "install"]
            if global_install:
                cmd.append("-g")
            if dev:
                cmd.append("--save-dev")
            if package:
                cmd.append(package)

            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Packages installed"

        elif action == "run_script":
            script_name = kwargs.get("script_name", "")
            if not script_name:
                return "Error: script_name parameter required"
            result = subprocess.run(
                ["npm", "run", script_name],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Ran script: {script_name}"

        elif action == "build":
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Build completed"

        elif action == "start":
            result = subprocess.run(
                ["npm", "start"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or "Started development server"

        elif action == "test":
            result = subprocess.run(
                ["npm", "test"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Tests completed"

        elif action == "lint":
            result = subprocess.run(
                ["npm", "run", "lint"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Linting completed"

        elif action == "format":
            result = subprocess.run(
                ["npm", "run", "format"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Code formatting completed"

        elif action == "create_react_app":
            app_name = kwargs.get("name", "my-react-app")
            if not app_name:
                return "Error: name parameter required"

            result = subprocess.run(
                ["npx", "create-react-app", app_name, "--yes"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=600
            )
            return result.stdout or result.stderr or f"Created React app: {app_name}"

        elif action == "add_dependency":
            package = kwargs.get("package", "")
            if not package:
                return "Error: package parameter required"

            result = subprocess.run(
                ["npm", "install", package],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Added dependency: {package}"

        elif action == "remove_dependency":
            package = kwargs.get("package", "")
            if not package:
                return "Error: package parameter required"

            result = subprocess.run(
                ["npm", "uninstall", package],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or f"Removed dependency: {package}"

        elif action == "update_dependencies":
            result = subprocess.run(
                ["npm", "update"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Updated all dependencies"

        elif action == "audit":
            result = subprocess.run(
                ["npm", "audit"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Security audit completed"

        elif action == "publish":
            # Warning: This will publish to npm!
            confirm = kwargs.get("confirm", False)
            if not confirm:
                return "ERROR: Publishing requires confirm=true parameter. This will publish to npm!"

            result = subprocess.run(
                ["npm", "publish"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Package published to npm"

        else:
            available_actions = [
                "init", "install", "run_script", "build", "start", "test",
                "lint", "format", "create_react_app", "add_dependency",
                "remove_dependency", "update_dependencies", "audit", "publish"
            ]
            return f"Error: Unknown action '{action}'. Available: {', '.join(available_actions)}"

    except Exception as e:
        return f"Error executing npm action '{action}': {str(e)}"
